"""Generic source-owner acquisition. Its owning loader must supply a digest-pinned
private selection; input arguments alone convey no admission or lifecycle credit.
"""
import datetime

import hashlib

import importlib.util

import json

import os

from pathlib import Path

import re

import stat

import subprocess

MAX_RECORD = 256 * 1024

MAX_DISCOVERY = 256 * 1024

MAX_SELECTED = 8

def require(condition, code):
    if not condition:
        raise ValueError(code)

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def unique(pairs):
    out = {}
    for key, value in pairs:
        require(key not in out, "DUPLICATE_KEY")
        out[key] = value
    return out

def parse(raw):
    return json.loads(raw, object_pairs_hook=unique)

def canonical_path(value):
    text = str(value)
    if text.startswith("\\\\?\\"):
        text = text[4:]
    return Path(text).resolve(strict=True)

def physical(path):
    lexical=custody.lexical_path(path)
    with custody.held_file(lexical) as stream:
        info=os.fstat(stream.fileno())
        require(stat.S_ISREG(info.st_mode) and info.st_nlink==1,"SOURCE_NOT_REGULAR_OR_HARDLINK")
        return {"path": str(lexical), "device": info.st_dev, "inode": info.st_ino}

def same_physical(info, expected):
    return (info.st_dev, info.st_ino) == (expected["device"], expected["inode"])

def header(thread):
    path = custody.lexical_path(thread["path"])
    with custody.held_file(path) as stream:
        info = os.fstat(stream.fileno())
        require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, "SOURCE_NOT_REGULAR_OR_HARDLINK")
        source = {"path": str(path), "device": info.st_dev, "inode": info.st_ino}
        # Discover only the first metadata line within the existing bounded
        # prefix. No bytes after its LF are copied, parsed or retained. Mapping
        # the held descriptor avoids byte-at-a-time unbuffered readline calls.
        import mmap
        length = min(info.st_size, MAX_RECORD + 1)
        require(length > 0, "HEADER_RANGE_BOUND")
        with mmap.mmap(stream.fileno(), length, access=mmap.ACCESS_READ) as prefix:
            end = prefix.find(b"\n")
            require(0 <= end < MAX_RECORD, "HEADER_RANGE_BOUND")
            raw = prefix[:end + 1]
        require(len(raw) <= MAX_RECORD and raw.endswith(b"\n") and
                raw.find(b"\n") == len(raw) - 1, "HEADER_RANGE_BOUND")
        cutoff = os.fstat(stream.fileno()).st_size
        row = parse(raw)
        require(row.get("type") == "session_meta" and isinstance(row.get("payload"), dict), "HEADER_TYPE")
        payload = row["payload"]
        fields = ("id", "session_id", "parent_thread_id", "agent_path", "cli_version", "cwd",
                  "originator", "thread_source", "history_mode")
        # The same held leaf and every held ancestor stay protected through
        # parsing. held_file rechecks identity, hardlinks, reparsing and names
        # before this provisional value can escape its closing guard.
        return {"physical": source, "header_prefix": {"offset": 0, "bytes": len(raw),
            "sha256": digest(raw), "ordinal": row.get("ordinal")},
            "metadata": {key: payload[key] for key in fields if key in payload},
            "cutoff_bytes": cutoff}

def validate_relation(selection, root, child, root_header, child_header):
    ROOT_ID = selection['root_thread_id']
    CLI_VERSION = selection['cli_version']
    CWD = Path(selection['cwd'])
    require(root.get("id") == root.get("sessionId") == ROOT_ID and root.get("parentThreadId") is None,
            "WRONG_ROOT_NATIVE_RELATION")
    child_id = child.get("id")
    require(isinstance(child_id, str) and child_id and child_id != ROOT_ID and
            child.get("sessionId") == child_id and child.get("parentThreadId") == ROOT_ID and
            child.get("source_kind") == "subAgent" and child.get("threadSource") == "subagent",
            "WRONG_CHILD_NATIVE_RELATION")
    for native, meta, ident in ((root, root_header, ROOT_ID), (child, child_header, child_id)):
        require(native.get("cliVersion") == meta.get("cli_version") == CLI_VERSION and
                native.get("cwd") == meta.get("cwd") == str(CWD) and
                native.get("ephemeral") is False and native.get("historyMode") == "paginated" and
                meta.get("id") == ident and meta.get("session_id") == ROOT_ID,
                "VERSION_QUALIFIED_HEADER_RELATION_CHANGED")
    require(child_header.get("parent_thread_id") == ROOT_ID and
            child_header.get("thread_source") == "subagent" and
            isinstance(child_header.get("agent_path"), str) and child_header["agent_path"].startswith("/root/"),
            "CHILD_HEADER_PARENT_OR_TASK_CHANGED")
    return child_id

def public_record(row):
    require(isinstance(row, dict) and row.get("type") == "response_item", "PUBLIC_RECORD_REQUIRED")
    p = row.get("payload")
    require(isinstance(p, dict) and p.get("type") == "message" and p.get("role") == "assistant" and
            p.get("phase") in ("commentary", "final_answer"), "PUBLIC_RECORD_REQUIRED")
    meta = row.get("metadata")
    require(isinstance(meta, dict) and meta.get("client_authored") is False, "HOST_RETAINED_RECORD_REQUIRED")
    retained = meta.get("retained_source")
    require(isinstance(retained, dict) and retained.get("complete") is True and
            isinstance(retained.get("revision"), str) and retained["revision"].startswith("retained_"),
            "COMPLETE_RETAINED_REVISION_REQUIRED")
    ident = retained.get("id")
    require(isinstance(ident, dict) and ident.get("message_id") == p.get("id") and
            isinstance(p.get("id"), str) and p["id"] and ident.get("role") == "assistant" and
            isinstance(ident.get("turn_id"), str) and ident["turn_id"], "RETAINED_IDENTITY_CHANGED")
    content = p.get("content")
    require(isinstance(content, list) and len(content) == 1 and isinstance(content[0], dict) and
            set(content[0]) == {"type", "text", "annotations", "logprobs"} and
            content[0]["annotations"] == [] and content[0]["logprobs"] == [] and content[0]["type"] == "output_text" and
            isinstance(content[0]["text"], str), "PUBLIC_TEXT_SHAPE")
    require(type(row.get("ordinal")) is int and row["ordinal"] >= 0, "SOURCE_ORDINAL_REQUIRED")
    body = content[0]["text"].encode("utf-8")
    return {"id": p["id"], "turn_id": ident["turn_id"], "revision": retained["revision"],
            "phase": p["phase"], "body_bytes": len(body), "body_sha256": digest(body), "ordinal": row["ordinal"]}

def read_public(path, source, locator, cutoff):
    require(isinstance(locator, dict) and set(locator) == {"offset", "bytes", "sha256", "ordinal"}, "LOCATOR_SHAPE")
    start, size = locator["offset"], locator["bytes"]
    require(type(start) is int and type(size) is int and type(cutoff) is int and
            start > 0 and 0 < size <= MAX_RECORD and start + size <= cutoff, "PUBLIC_RANGE_BOUND")
    path = custody.lexical_path(path)
    require(physical(path) == source, "PUBLIC_SOURCE_CHANGED")
    with custody.held_file(path) as stream:
        opened = os.fstat(stream.fileno())
        require(same_physical(opened, source) and opened.st_size >= cutoff, "PUBLIC_SOURCE_CHANGED")
        stream.seek(start-1)
        require(stream.read(1) == b"\n", "PUBLIC_RECORD_BOUNDARY")
        raw = stream.read(size)
        require(len(raw) == size and raw.endswith(b"\n") and digest(raw) == locator["sha256"], "PUBLIC_BYTES_CHANGED")
        require(same_physical(os.fstat(stream.fileno()), source), "PUBLIC_SOURCE_CHANGED")
    require(physical(path) == source, "PUBLIC_SOURCE_CHANGED")
    result = public_record(parse(raw))
    require(result["ordinal"] == locator["ordinal"], "PUBLIC_ORDINAL_CHANGED")
    return result

def discover_public(source):
    """Discover at most one latest public record in a frozen 256 KiB tail.

    Only type/role/phase is inspected on other rows. Their content is not used.
    Discovery does not claim complete history, original/retry classification, or
    lifecycle coverage; selected rows still require exact native item binding.
    """
    path = Path(source["physical"]["path"])
    cutoff = source["cutoff_bytes"]
    start = max(source["header_prefix"]["bytes"], cutoff - MAX_DISCOVERY)
    require(physical(path) == source["physical"], "DISCOVERY_SOURCE_CHANGED")
    with custody.held_file(path) as stream:
        require(same_physical(os.fstat(stream.fileno()), source["physical"]), "DISCOVERY_SOURCE_CHANGED")
        stream.seek(start)
        raw = stream.read(cutoff-start)
    require(len(raw) == cutoff-start and physical(path) == source["physical"], "DISCOVERY_SOURCE_CHANGED")
    offset = start
    pieces = raw.splitlines(keepends=True)
    if start > source["header_prefix"]["bytes"] and pieces:
        offset += len(pieces.pop(0))
    chosen = None
    for index, block in enumerate(pieces):
        require(index < 2048, "DISCOVERY_RECORD_COUNT_BOUND")
        if block.endswith(b"\n") and len(block) <= MAX_RECORD:
            row = parse(block)
            p = row.get("payload", {}) if isinstance(row, dict) else {}
            if row.get("type") == "response_item" and p.get("type") == "message" and p.get("role") == "assistant" and p.get("phase") in ("commentary", "final_answer"):
                candidate = public_record(row)
                chosen = {"offset": offset, "bytes": len(block), "sha256": digest(block), "ordinal": candidate["ordinal"]}
        offset += len(block)
    require(chosen is not None, "NO_PUBLIC_RECORD_IN_BOUNDED_DISCOVERY")
    return [chosen], {"offset": start, "bytes": len(raw), "sha256": digest(raw),
                       "cutoff_bytes": cutoff, "classification": "BOUNDED_DISCOVERY_ONLY"}

def bind_public(source, native):
    require(all(source.get(key) == native.get(key) for key in
                ("id", "turn_id", "phase", "body_bytes", "body_sha256")), "NATIVE_PUBLIC_ID_BODY_PHASE_TURN_DIFFERS")

def same_selection(expected, current):
    require(expected == current, "SELECTED_PUBLIC_REVISION_OR_RECORD_CHANGED")

def owning_host(selection, reader):
    HOST_PID = selection['host_process']['pid']
    HOST_START = selection['host_process']['created_utc']
    DESKTOP_PID = selection['desktop_process']['pid']
    DESKTOP_START = selection['desktop_process']['created_utc']
    DESKTOP = Path(selection['desktop_executable']['path'])
    DESKTOP_SHA256 = selection['desktop_executable']['sha256']
    BINARY = Path(selection['native_executable']['path'])
    BINARY_SHA256 = selection['native_executable']['sha256']
    powershell = custody.trusted_system_tool('powershell.exe')
    cim = powershell.parent / 'Modules' / 'CimCmdlets' / 'CimCmdlets.psd1'
    require(cim.is_file() and Path(os.path.realpath(cim)) == cim, 'TRUSTED_CIM_MODULE_ABSENT')
    script = "Import-Module -Name '" + str(cim).replace("'", "''") + "' -Force -ErrorAction Stop; "
    script += r'''$targetPid = ''' + str(os.getpid()) + r'''; $rows = @(); $seen = @{}; for ($n=0; $n -lt 12 -and $targetPid -gt 0; $n++) { if ($seen.ContainsKey($targetPid)) { break }; $seen[$targetPid]=$true; $p=CimCmdlets\Get-CimInstance Win32_Process -Filter "ProcessId=$targetPid"; if (-not $p) { break }; $rows += [pscustomobject]@{pid=[int]$p.ProcessId; parent_pid=[int]$p.ParentProcessId; name=$p.Name; path=$p.ExecutablePath; created_utc=$p.CreationDate.ToUniversalTime().ToString('o')}; $targetPid=[int]$p.ParentProcessId }; $rows | ConvertTo-Json -Depth 3 -Compress'''
    run = subprocess.run([str(powershell), "-NoProfile", "-Command", script], capture_output=True,
        timeout=12, creationflags=subprocess.CREATE_NO_WINDOW)
    require(run.returncode == 0 and len(run.stdout) <= 32768, "OWNING_HOST_READ_FAILED")
    rows = parse(run.stdout)
    require(isinstance(rows, list), "OWNING_HOST_ANCESTRY_SHAPE")
    native = next((row for row in rows if row.get("pid") == HOST_PID), None)
    desktop = next((row for row in rows if row.get("pid") == DESKTOP_PID), None)
    require(native is not None and desktop is not None and native.get("name") == "codex.exe" and
            native.get("parent_pid") == DESKTOP_PID and native.get("created_utc") == HOST_START and
            desktop.get("created_utc") == DESKTOP_START and desktop.get("name") == "ChatGPT.exe" and
            canonical_path(native["path"]) == canonical_path(BINARY) and
            canonical_path(desktop["path"]) == canonical_path(DESKTOP), "SELECTED_OWNING_HOST_CHANGED")
    binary_pin = reader.file_pin(BINARY)
    desktop_pin = reader.file_pin(DESKTOP)
    require(binary_pin["sha256"] == BINARY_SHA256 and desktop_pin["sha256"] == DESKTOP_SHA256,
            "SELECTED_HOST_EXECUTABLE_CHANGED")
    return {"native_process": native, "desktop_process": desktop,
            "native_executable": binary_pin, "desktop_executable": desktop_pin}

def qualified_protocol(report):
    protocol = report.get("protocol", {})
    require(report.get("failure") is None and report.get("executable_unchanged") is True and
            protocol.get("process_terminated") is True and protocol.get("exit_code") == 0 and
            protocol.get("forced_cleanup") is False and protocol.get("streams_complete") is True and
            protocol.get("cleanup_failures") == [] and
            all(protocol.get("streams", {}).get(name, {}).get("eof") is True and
                protocol["streams"][name].get("done") is True and protocol["streams"][name].get("failure") is None
                for name in ("stdout", "stderr")), "NATIVE_READ_OR_CLEANUP_UNQUALIFIED")
    require(all("error" not in response for response in report.get("responses", [])), "NATIVE_RESPONSE_ERROR")


def ordinary_ancestry_pair_v1(selection, rows, caller_pid):
    """Pure discriminator for the explicit ordinary policy, never the old P."""
    require(selection.get('schema') == 'implementaudit.codex-ordinary-selection.v1' and
            selection.get('instance_selection') == 'EXACT_ROOT_EXECUTION_ANCESTRY',
            'ORDINARY_INSTANCE_POLICY_REQUIRED')
    require(isinstance(rows, list) and 1 <= len(rows) <= 12 and rows[0].get('pid') == caller_pid,
            'ORDINARY_ANCESTRY_ROOT')
    seen = set()
    for index, row in enumerate(rows):
        require(isinstance(row, dict) and set(row) == {'pid', 'parent_pid', 'name', 'path', 'created_utc'} and
                type(row['pid']) is int and row['pid'] > 0 and row['pid'] not in seen and
                type(row['parent_pid']) is int and row['parent_pid'] >= 0 and
                isinstance(row['created_utc'], str) and row['created_utc'], 'ORDINARY_ANCESTRY_SHAPE')
        seen.add(row['pid'])
        if index + 1 < len(rows):
            require(row['parent_pid'] == rows[index + 1].get('pid'), 'ORDINARY_ANCESTRY_LINK')
    candidates = [(left, right) for left, right in zip(rows, rows[1:])
                  if left['name'] == 'codex.exe' and right['name'] == 'ChatGPT.exe' and
                  canonical_path(left['path']) == canonical_path(selection['native_executable']['path']) and
                  canonical_path(right['path']) == canonical_path(selection['desktop_executable']['path'])]
    require(len(candidates) == 1, 'ORDINARY_OWNING_HOST_NOT_UNIQUE')
    native, desktop = candidates[0]
    return {'native_process': native, 'desktop_process': desktop}


def owning_ordinary_host(selection, reader):
    """Observe this process's bounded ancestry; accept no PID override.

    Binary/configuration equality remains the caller's immutable provider guard.
    Historical PID fields never become permission to relax those byte pins.
    """
    powershell = custody.trusted_system_tool('powershell.exe')
    cim = powershell.parent / 'Modules' / 'CimCmdlets' / 'CimCmdlets.psd1'
    require(cim.is_file() and Path(os.path.realpath(cim)) == cim, 'TRUSTED_CIM_MODULE_ABSENT')
    script = "Import-Module -Name '" + str(cim).replace("'", "''") + "' -Force -ErrorAction Stop; "
    script += '$targetPid = ' + str(os.getpid()) + '; '
    script += r'''$rows = @(); $seen = @{}; for ($n=0; $n -lt 12 -and $targetPid -gt 0; $n++) { if ($seen.ContainsKey($targetPid)) { break }; $seen[$targetPid]=$true; $p=CimCmdlets\Get-CimInstance Win32_Process -Filter "ProcessId=$targetPid"; if (-not $p) { break }; $rows += [pscustomobject]@{pid=[int]$p.ProcessId; parent_pid=[int]$p.ParentProcessId; name=$p.Name; path=$p.ExecutablePath; created_utc=$p.CreationDate.ToUniversalTime().ToString('o')}; $targetPid=[int]$p.ParentProcessId }; $rows | ConvertTo-Json -Depth 3 -Compress'''
    run = subprocess.run([str(powershell), '-NoProfile', '-Command', script], capture_output=True,
                         timeout=12, creationflags=subprocess.CREATE_NO_WINDOW)
    require(run.returncode == 0 and len(run.stdout) <= 32768, 'ORDINARY_ANCESTRY_READ_FAILED')
    pair = ordinary_ancestry_pair_v1(selection, parse(run.stdout), os.getpid())
    for name in ('native_executable', 'desktop_executable'):
        observed = reader.file_pin(Path(selection[name]['path']))
        require(observed['sha256'] == selection[name]['sha256'], 'SELECTED_HOST_EXECUTABLE_CHANGED')
    return pair


def run_held_ordinary_receiver_v1(selection, source_pin):
    """Execute the sole fixed receiver entry with held interpreter/source bytes.

    No shell, supplied command, model call, stdin, or environment override API.
    The receiver entry itself is constrained to the fixed local read-only owner.
    """
    import contextlib
    python_pin = selection['python_executable']
    require(Path(source_pin['path']).name == 'compaction-source-owner-codex-app.py', 'ORDINARY_RUNNER_SOURCE_NAME')
    argv = [python_pin['path'], '-I', '-S', '-B', source_pin['path'], '--ordinary-receiver']
    with contextlib.ExitStack() as stack:
        held = []
        for pin in (python_pin, source_pin):
            stream = stack.enter_context(custody.held_file(pin['path'], allow_append=False))
            info = os.fstat(stream.fileno())
            require(0 < pin['bytes'] <= 128 * 1024 * 1024 and info.st_size == pin['bytes'] and info.st_nlink == 1,
                    'ORDINARY_RUNNER_PIN_BOUND')
            checksum = hashlib.sha256(); remaining = pin['bytes']
            while remaining:
                block = stream.read(min(65536, remaining)); require(block, 'ORDINARY_RUNNER_TRUNCATED')
                checksum.update(block); remaining -= len(block)
            require(checksum.hexdigest() == pin['sha256'], 'ORDINARY_RUNNER_PIN_CHANGED')
            held.append((stream, info))
        environment = {key: value for key, value in os.environ.items()
            if key.casefold() in {'systemroot', 'windir', 'systemdrive', 'comspec', 'pathext', 'temp', 'tmp',
                                 'userprofile', 'localappdata', 'appdata', 'programfiles', 'programfiles(x86)'} }
        paths = [Path(python_pin['path']).parent]
        # Preserve the existing native owners' fixed host-tool discovery while
        # excluding the caller PATH and Git/Python configuration overrides.
        for key in ('ProgramFiles', 'ProgramFiles(x86)'):
            if os.environ.get(key):
                git_root = Path(os.environ[key]) / 'Git'
                paths.extend(git_root / name for name in ('cmd', 'bin', 'usr/bin'))
        if os.environ.get('SystemRoot'):
            system = Path(os.environ['SystemRoot'])
            paths.extend((system / 'System32', system))
        paths.append(custody.trusted_system_tool('powershell.exe').parent)
        environment['PATH'] = os.pathsep.join(dict.fromkeys(str(path.resolve()) for path in paths if path.is_dir()))
        process = subprocess.Popen(argv, cwd=selection['episode_owner']['repository'], env=environment,
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        try:
            stdout, stderr = process.communicate(timeout=180)
        except subprocess.TimeoutExpired:
            if os.name == 'nt':
                subprocess.run([str(custody.trusted_system_tool('taskkill.exe')), '/PID', str(process.pid), '/T', '/F'],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=15, check=False,
                    creationflags=subprocess.CREATE_NO_WINDOW)
            else:
                process.kill()
            process.communicate(timeout=15)
            raise ValueError('ORDINARY_RECEIVER_TIMEOUT_UNQUALIFIED')
        require(len(stdout) <= 256 * 1024 and len(stderr) <= 256 * 1024 and type(process.returncode) is int,
                'ORDINARY_RECEIVER_OUTPUT_BOUND')
        for stream, before in held:
            after = os.fstat(stream.fileno())
            require((before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) ==
                    (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns), 'ORDINARY_RUNNER_CHANGED_DURING_EXECUTION')
        return {'argv': argv, 'python_pin': dict(python_pin), 'source_pin': dict(source_pin), 'exit_code': process.returncode,
                'stdout': stdout.decode('utf-8', 'strict'), 'stdout_sha256': digest(stdout), 'stderr_sha256': digest(stderr)}

def selected_child(selection, caller, previous):
    root = selection['root_thread_id']
    child = selection['selected_child_thread_id']
    require(isinstance(child, str) and child and child != root and caller in (root, child),
            'SELECTED_EPISODE_CALLER_REQUIRED')
    if previous is not None:
        require(caller == root and previous.get('schema') == 'implementaudit.codex-current-public-source-observation.v1' and
                previous.get('root_thread_id') == root and previous.get('child_thread_id') == child and
                previous.get('selection_sha256') == selection['_selection_sha256'],
                'PREVIOUS_OBSERVATION_SELECTION_CHANGED')
    return child

def acquire(selection, reader, *, previous=None, nominations=None, receipts=None):
    ROOT_ID = selection['root_thread_id']
    ROOT_SOURCE = Path(selection['root_source'])
    SESSION_ROOT = Path(selection['session_root'])
    COMMISSION_SHA256 = selection['commission_sha256']
    receipts = receipts if receipts is not None else []
    caller = os.environ.get("CODEX_THREAD_ID")
    child_id = selected_child(selection, caller, previous)
    host = owning_host(selection, reader)
    code = dict(selection['_source_code_sha256'])
    if previous is not None:
        require(previous.get('source_code_sha256') == code, 'PREVIOUS_OBSERVATION_CODE_CHANGED')
    metadata_read = reader.probe(selection, child_id=child_id)
    receipts.append(metadata_read)
    qualified_protocol(metadata_read)
    root, child = [response["thread"] for response in metadata_read["responses"]]
    require(root["id"] == ROOT_ID and child["id"] == child_id, "NATIVE_RESPONSE_SUBJECT_CHANGED")
    require(canonical_path(root["path"]) == canonical_path(ROOT_SOURCE), "ROOT_SOURCE_PATH_CHANGED")
    child_path = canonical_path(child["path"])
    require(child_path.is_relative_to(canonical_path(SESSION_ROOT)) and
            child_path.name.endswith("-" + child_id + ".jsonl"), "CHILD_SOURCE_PATH_OUTSIDE_SELECTED_ROOT")
    sources = {"parent": header(root), "child": header(child)}
    validate_relation(selection, root, child, sources["parent"]["metadata"], sources["child"]["metadata"])
    require(sources['child']['metadata']['agent_path'] == selection['selected_agent_path'],
            'SELECTED_CHILD_TASK_CHANGED')
    if previous is not None:
        for role in sources:
            old = previous["sources"][role]
            require(all(sources[role][key] == old[key] for key in ("physical", "header_prefix", "metadata")) and
                    sources[role]["cutoff_bytes"] >= old["cutoff_bytes"], "PREVIOUS_SOURCE_OR_PREFIX_CHANGED")
            sources[role]["cutoff_bytes"] = old["cutoff_bytes"]
    selections = []
    for role, source in sources.items():
        if previous is None:
            if nominations is None:
                locators, discovery = discover_public(source)
            else:
                require(isinstance(nominations, dict) and set(nominations) == {'parent', 'child'}, 'NOMINATION_SCOPE')
                locators = nominations[role]
                discovery = {'classification': 'EXACT_NOMINATIONS_REQUIRE_NATIVE_BINDING'}
            source['discovery'] = discovery
        else:
            locators = [row["locator"] for row in previous["records"] if row["role"] == role]
            source["discovery"] = previous["sources"][role]["discovery"]
        require(0 < len(locators) <= MAX_SELECTED, "SELECTED_RECORD_COUNT_BOUND")
        for locator in locators:
            record = read_public(source["physical"]["path"], source["physical"], locator, source["cutoff_bytes"])
            selections.append({"role": role, "locator": locator, "public": record})
    require(len(selections) <= MAX_SELECTED, "SELECTED_RECORD_COUNT_BOUND")
    if previous is not None:
        for old, current in zip(previous["records"], selections):
            require(old["role"] == current["role"] and old["locator"] == current["locator"], "PREVIOUS_SELECTION_CHANGED")
            same_selection(old["public"], current["public"])
        require(len(previous["records"]) == len(selections), "PREVIOUS_SELECTION_CHANGED")
    methods = [("thread/items/read", {"threadId": ROOT_ID if row["role"] == "parent" else child_id,
                "turnId": row["public"]["turn_id"], "itemIds": [row["public"]["id"]]}) for row in selections]
    public_read = reader.probe(selection, methods, child_id=child_id)
    receipts.append(public_read)
    qualified_protocol(public_read)
    require(len(public_read["responses"]) == len(selections), "NATIVE_PUBLIC_POPULATION_CHANGED")
    for row, response in zip(selections, public_read["responses"]):
        bind_public(row["public"], response["items"][0])
        row["native_response_sha256"] = response["response_sha256"]
        source = sources[row["role"]]
        same_selection(row["public"], read_public(source["physical"]["path"], source["physical"], row["locator"], source["cutoff_bytes"]))
    for role, native in (("parent", root), ("child", child)):
        after = header(native)
        require(all(after[key] == sources[role][key] for key in ("physical", "header_prefix", "metadata")), "SOURCE_HEADER_CHANGED_DURING_ACQUISITION")
    require(owning_host(selection, reader) == host and all(reader.file_pin(Path(path))['sha256'] == sha for path, sha in code.items()),
            "HOST_OR_SOURCE_CODE_CHANGED_DURING_ACQUISITION")
    return {"schema": "implementaudit.codex-current-public-source-observation.v1",
            "time_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "root_thread_id": ROOT_ID, "child_thread_id": child_id,
            "actual_agent_path": sources["child"]["metadata"]["agent_path"],
            "source_owner": "R003A/continuity/Codex-app", "commission_sha256": COMMISSION_SHA256,
            "source_code_sha256": code, "selection_sha256": selection["_selection_sha256"], "host": host, "native_metadata": {"parent": root, "child": child},
            "metadata_read": metadata_read, "public_read": public_read, "sources": sources, "records": selections,
            "admission_status": "STAGED_SOURCE_OWNER_OUTPUT_REQUIRES_EXACT_ROOT_ADMISSION",
            "authority_ceiling": "NONE", "coverage": "EXACT_SELECTED_PUBLIC_RECORDS_ONLY",
            "noncredits": ["lifecycle", "result", "acceptance", "JOIN", "occurrence_history", "campaign_epoch", "campaign_currentness"]}


def _ordinary_public_batch_v1(runtime, obs, context, specs, native_call, resolve):
    """Private fixed-owner read composition; no authentication from caller data."""
    require(type(specs) is list and 1 <= len(specs) <= 4, 'ORDINARY_NATIVE_PUBLIC_POPULATION')
    prepared, methods = [], []
    for role, locator, phase in specs:
        row, pin = resolve(obs, context, role, locator)
        body = obs.public_message(row, phase, context=context)
        retained = obs.current_retained_locator(row, context)
        ident = retained['id']
        thread = context['actual_child_identity']['thread_id'] if role == 'child' else context['parent_identity']['thread_id']
        methods.append(('thread/items/read', {'threadId': thread, 'turnId': ident['turn_id'], 'itemIds': [ident['message_id']]}))
        expected = {'id': ident['message_id'], 'turn_id': ident['turn_id'], 'phase': phase,
                    'body_bytes': len(body.encode('utf-8')), 'body_sha256': obs.digest(body.encode('utf-8'))}
        prepared.append((row, pin, body, retained, expected))
    report = native_call(runtime, methods, context['actual_child_identity']['thread_id'])
    require(len(report['responses']) == len(prepared), 'ORDINARY_NATIVE_PUBLIC_POPULATION')
    values = []
    for (role, locator, phase), (row, pin, body, retained, expected), response in zip(specs, prepared, report['responses']):
        require(response['items'] == [expected], 'ORDINARY_NATIVE_PUBLIC_BODY_DIFFERS')
        require(resolve(obs, context, role, locator) == (row, pin), 'ORDINARY_PUBLIC_CHANGED_DURING_READ')
        values.append({'pin': pin, 'message_id': expected['id'], 'turn_id': expected['turn_id'],
            'revision': retained['revision'], 'phase': phase, 'body': body, 'body_sha256': expected['body_sha256']})
    return values


def _bind_episode_owner_v1(selected, actual):
    """Private equality constraint against the fixed graph owner's live source."""
    code = 'ORDINARY_SELECTED_EPISODE_OWNER_DIFFERS'
    require(type(selected) is dict and type(actual) is dict and
            set(selected) == set(actual) == {'repository', 'controller', 'module_pin'}, code)
    for value in (selected, actual):
        require(type(value['repository']) is str and type(value['controller']) is str and
                type(value['module_pin']) is dict and set(value['module_pin']) == {'path', 'bytes', 'sha256'} and
                type(value['module_pin']['path']) is str and type(value['module_pin']['bytes']) is int and
                0 < value['module_pin']['bytes'] <= 512 * 1024 and type(value['module_pin']['sha256']) is str, code)
    require(Path(selected['repository']) == Path(actual['repository']) and selected['controller'] == actual['controller'] and
            Path(selected['module_pin']['path']) == Path(actual['module_pin']['path']) and
            all(selected['module_pin'][key] == actual['module_pin'][key] for key in ('bytes', 'sha256')), code)


def _subject_from_episode_v1(runtime, episode, native_call):
    selected, _, _, helpers, _ = runtime
    parent_id = selected['root_thread_id']
    params = {'parentThreadId': parent_id, 'sourceKinds': ['subAgent'], 'limit': 100, 'cursor': None, 'archived': False, 'useStateDbOnly': True}
    catalog = native_call(runtime, [('thread/list', params)])
    records = catalog['responses'][0]['threads']
    expected_path = selected['root_agent_path'] + '/' + episode['logical_task']
    matches = []
    for record in records:
        require(isinstance(record.get('path'), str), 'NONPROTECTED_CATALOG_PHYSICAL_PATH_ABSENT')
        require(helpers.canonical_path(record['path']).is_relative_to(helpers.canonical_path(selected['session_root'])) and Path(record['path']).name.endswith('-' + record['id'] + '.jsonl'), 'NONPROTECTED_CATALOG_SOURCE_NAMESPACE')
        source = helpers.header(record)
        require(source['metadata'].get('id') == record['id'] and source['metadata'].get('parent_thread_id') == parent_id, 'NONPROTECTED_CATALOG_HEADER_PARENT_DIFFERS')
        if source['metadata'].get('agent_path') == expected_path:
            matches.append((record['id'], source))
    require(len(matches) == 1, 'NONPROTECTED_CANONICAL_CHILD_NOT_UNIQUE')
    child_id, discovered = matches[0]
    metadata = native_call(runtime, [('thread/read', {'threadId': ident, 'includeTurns': False}) for ident in (parent_id, child_id)], child_id)
    parent, child = [row['thread'] for row in metadata['responses']]
    sources = {'parent': helpers.header(parent), 'child': helpers.header(child)}
    helpers.validate_relation(selected, parent, child, sources['parent']['metadata'], sources['child']['metadata'])
    require(child['id'] == child_id and all((sources['child'][key] == discovered[key] for key in ('physical', 'header_prefix', 'metadata'))) and (sources['child']['metadata']['agent_path'] == expected_path) and (helpers.canonical_path(parent['path']) == helpers.canonical_path(selected['root_source'])), 'NONPROTECTED_SELECTED_NATIVE_CHILD_CHANGED')
    return {'episode': episode, 'metadata': metadata, 'catalog': catalog, 'sources': sources, 'parent_identity': {'thread_id': parent_id, 'agent_path': selected['root_agent_path']}, 'actual_child_identity': {'thread_id': child_id, 'parent_thread_id': parent_id, 'agent_path': expected_path}}


def _recheck_ordinary_native_v1(runtime, obs, context, public, occurrences, native_call, resolve):
    """Fresh bounded native exit read for the fixed owner's active observation.

    Private implementation helper, not an authentication entry or credential.
    Batch the same read-only API predicates in one process; retain each exact
    response, source-header, physical-record, body and relation check.
    """
    selected, _, _, helpers, _ = runtime
    subject = context['_native_subject']
    parent_id = subject['parent_identity']['thread_id']
    child_id = subject['actual_child_identity']['thread_id']
    params = {'parentThreadId': parent_id, 'sourceKinds': ['subAgent'], 'limit': 100,
              'cursor': None, 'archived': False, 'useStateDbOnly': True}
    methods = [('thread/list', params)] + [
        ('thread/read', {'threadId': ident, 'includeTurns': False}) for ident in (parent_id, child_id)]
    originals = []
    for item in public:
        pin = item['pin']; role, locator = pin['role'], pin['locator']
        row, actual_pin = resolve(obs, context, role, locator)
        retained = obs.current_retained_locator(row, context)
        require(actual_pin == pin and obs.public_message(row, item['phase'], context=context) == item['body'] and
                retained['revision'] == item['revision'] and retained['id']['message_id'] == item['message_id'] and
                retained['id']['turn_id'] == item['turn_id'], 'ORDINARY_PUBLIC_CHANGED_DURING_READ')
        methods.append(('thread/items/read', {'threadId': child_id if role == 'child' else parent_id,
            'turnId': item['turn_id'], 'itemIds': [item['message_id']]}))
        originals.append((row, actual_pin))
    report = native_call(runtime, methods, child_id)
    responses = report['responses']
    require(len(responses) == len(methods), 'ORDINARY_NATIVE_RESPONSE_POPULATION')
    matches = []
    expected_path = subject['actual_child_identity']['agent_path']
    for record in responses[0]['threads']:
        require(isinstance(record.get('path'), str) and
                helpers.canonical_path(record['path']).is_relative_to(helpers.canonical_path(selected['session_root'])) and
                Path(record['path']).name.endswith('-' + record['id'] + '.jsonl'), 'NONPROTECTED_CATALOG_SOURCE_NAMESPACE')
        source = helpers.header(record)
        require(source['metadata'].get('id') == record['id'] and
                source['metadata'].get('parent_thread_id') == parent_id, 'NONPROTECTED_CATALOG_HEADER_PARENT_DIFFERS')
        if source['metadata'].get('agent_path') == expected_path:
            matches.append((record['id'], source))
    require(len(matches) == 1 and matches[0][0] == child_id, 'NONPROTECTED_CANONICAL_CHILD_NOT_UNIQUE')
    parent, child = [row['thread'] for row in responses[1:3]]
    sources = {'parent': helpers.header(parent), 'child': helpers.header(child)}
    helpers.validate_relation(selected, parent, child, sources['parent']['metadata'], sources['child']['metadata'])
    require(child['id'] == child_id and helpers.canonical_path(parent['path']) == helpers.canonical_path(selected['root_source']) and
            all(sources[role][key] == subject['sources'][role][key] for role in ('parent', 'child')
                for key in ('physical', 'header_prefix', 'metadata')) and
            all(matches[0][1][key] == sources['child'][key] for key in ('physical', 'header_prefix', 'metadata')),
            'NONPROTECTED_SELECTED_NATIVE_CHILD_CHANGED')
    for item, response, before in zip(public, responses[3:], originals):
        expected = {'id': item['message_id'], 'turn_id': item['turn_id'], 'phase': item['phase'],
                    'body_bytes': len(item['body'].encode('utf-8')), 'body_sha256': item['body_sha256']}
        require(response['items'] == [expected], 'ORDINARY_NATIVE_PUBLIC_BODY_DIFFERS')
        require(resolve(obs, context, item['pin']['role'], item['pin']['locator']) == before,
                'ORDINARY_PUBLIC_CHANGED_DURING_READ')
    for pin in (occurrences['spawn']['call'], occurrences['spawn']['output'], occurrences['activation']):
        require(resolve(obs, context, pin['role'], pin['locator'])[1] == pin, 'ORDINARY_OCCURRENCE_CHANGED')


def acquire_owned_stdio_public_v1(source, native_item, start_offset, cutoff, observation_owner):
    """Read one exact-turn native public item in a bounded original-source interval.

    This adds no source admission. The pinned 0.153.4 observation grammar and
    existing physical custody remain distinct from the desktop retained grammar.
    """
    require(isinstance(native_item, dict) and set(native_item) ==
            {'id', 'turn_id', 'phase', 'body_bytes', 'body_sha256'}, 'OWNED_STDIO_NATIVE_ITEM_SHAPE')
    require(type(start_offset) is int and type(cutoff) is int and
            source['header_prefix']['bytes'] <= start_offset < cutoff <= source['cutoff_bytes'] and
            cutoff - start_offset <= MAX_DISCOVERY, 'OWNED_STDIO_PUBLIC_INTERVAL_BOUND')
    require(source['metadata'].get('cli_version') == '0.153.4', 'OWNED_STDIO_SOURCE_VERSION')
    path = Path(source['physical']['path'])
    require(physical(path) == source['physical'], 'OWNED_STDIO_PUBLIC_PHYSICAL_CHANGED')
    selected = None
    active_turn = None
    offset = start_offset
    count = 0
    digestor = hashlib.sha256()
    with custody.held_file(path) as stream:
        opened = os.fstat(stream.fileno())
        require(same_physical(opened, source['physical']) and opened.st_size >= cutoff,
                'OWNED_STDIO_PUBLIC_SOURCE_CHANGED')
        stream.seek(start_offset - 1)
        require(stream.read(1) == b'\n', 'OWNED_STDIO_PUBLIC_RECORD_BOUNDARY')
        while offset < cutoff:
            raw = stream.readline(min(MAX_RECORD + 1, cutoff - offset))
            require(raw and len(raw) <= MAX_RECORD and raw.endswith(b'\n'), 'OWNED_STDIO_PUBLIC_FRAME')
            count += 1
            require(count <= 2048, 'OWNED_STDIO_PUBLIC_RECORD_BOUND')
            digestor.update(raw)
            row = parse(raw)
            require(isinstance(row, dict) and isinstance(row.get('payload'), dict), 'OWNED_STDIO_PUBLIC_FRAME')
            payload = row['payload']
            if row.get('type') == 'turn_context' or (row.get('type') == 'event_msg' and payload.get('type') == 'task_started'):
                active_turn = payload.get('turn_id')
            # Other records are classified only. Their text/summary/replacement
            # bodies supply no public proof and never escape this function.
            if row.get('type') == 'response_item' and payload.get('type') == 'message' and payload.get('role') == 'assistant' and payload.get('id') == native_item['id']:
                require(selected is None and active_turn == native_item['turn_id'], 'OWNED_STDIO_PUBLIC_ID_OR_ACTIVE_TURN')
                body = observation_owner.public_message(row, phase=native_item['phase'],
                    context={'profile_id': observation_owner.PROFILE}).encode('utf-8')
                observed = {'id': payload['id'], 'turn_id': active_turn, 'phase': payload['phase'],
                            'body_bytes': len(body), 'body_sha256': digest(body)}
                bind_public(observed, native_item)
                require(type(row.get('ordinal')) is int and row['ordinal'] >= 0, 'SOURCE_ORDINAL_REQUIRED')
                selected = {'public': observed, 'locator': {'offset': offset, 'bytes': len(raw),
                    'sha256': digest(raw), 'ordinal': row['ordinal']}}
            offset += len(raw)
        after = os.fstat(stream.fileno())
        require((opened.st_dev, opened.st_ino, opened.st_size, opened.st_mtime_ns) ==
                (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns), 'OWNED_STDIO_PUBLIC_SOURCE_CHANGED')
    require(physical(path) == source['physical'] and selected is not None, 'OWNED_STDIO_PUBLIC_NOT_FOUND')
    return {'public': selected['public'], 'locator': selected['locator'], 'physical': source['physical'],
            'source_interval': {'offset': start_offset, 'bytes': cutoff - start_offset,
                'sha256': digestor.hexdigest(), 'cutoff_bytes': cutoff}, 'authority_ceiling': 'NONE'}

def _held_owned_stdio_child_discovery_v1(selected, logical_task):
    """Complete explicitly bounded traversal; any unknown coverage refuses."""
    import contextlib
    @contextlib.contextmanager
    def acquire():
        root=custody.lexical_path(selected['session_root'])
        expected_path=selected['root_agent_path']+'/'+logical_task
        candidates=[];entry_count=1;directory_count=0;file_count=0
        with contextlib.ExitStack() as held:
            def walk(directory,depth):
                nonlocal entry_count,directory_count,file_count
                require(depth<=3,'OWNED_STDIO_HEADER_DISCOVERY_DEPTH_BOUND')
                held.enter_context(custody.held_directory(directory));directory_count+=1
                # os.scandir and entry.stat errors propagate. Never use glob,
                # which suppresses enumeration PermissionError on this runtime.
                with os.scandir(directory) as entries:
                    for entry in entries:
                        entry_count+=1
                        require(entry_count<=128,'OWNED_STDIO_HEADER_DISCOVERY_ENTRY_BOUND')
                        path=directory/entry.name
                        # Windows DirEntry.stat may report nlink=0; obtain the
                        # actual path metadata before the held relative open.
                        info=os.lstat(path)
                        require(not stat.S_ISLNK(info.st_mode) and not getattr(info,'st_file_attributes',0)&0x400,
                            'OWNED_STDIO_DISCOVERY_ALIAS_REFUSED')
                        if stat.S_ISDIR(info.st_mode):
                            walk(path,depth+1)
                        elif stat.S_ISREG(info.st_mode):
                            require(info.st_nlink==1,'OWNED_STDIO_DISCOVERY_HARDLINK_REFUSED')
                            file_count+=1
                            if not entry.name.startswith('rollout-') or not entry.name.endswith('.jsonl'):
                                continue
                            source=header({'path':str(path)});meta=source['metadata'];ident=meta.get('id')
                            require(isinstance(ident,str) and path.name.endswith('-'+ident+'.jsonl'),
                                'OWNED_STDIO_HEADER_FILENAME_IDENTITY')
                            if meta.get('parent_thread_id')==selected['root_thread_id'] and meta.get('agent_path')==expected_path:
                                require(meta.get('cli_version')==selected['cli_version'] and meta.get('cwd')==selected['cwd'] and
                                    meta.get('thread_source')=='subagent','OWNED_STDIO_CHILD_HEADER_SCOPE')
                                candidates.append((ident,source))
                        else:
                            raise ValueError('OWNED_STDIO_DISCOVERY_ENTRY_KIND_REFUSED')
            walk(root,0)
            require(len(candidates)==1,'OWNED_STDIO_ACTUAL_CHILD_NOT_UNIQUE_OR_TRANSPORT_UNAVAILABLE')
            yield candidates[0],{'schema':'implementaudit.owned-stdio-header-discovery.v1','namespace':str(root),
                'enumerated_entries':entry_count,'enumerated_directories':directory_count,'enumerated_files':file_count,
                'logical_task':logical_task,'source':'EXISTING_BOUNDED_NATIVE_HEADER_OWNER',
                'native_catalog_claim':False,'authority_ceiling':'NONE'}
    return acquire()

def discover_owned_stdio_child_v1(selected, logical_task):
    with _held_owned_stdio_child_discovery_v1(selected,logical_task) as observed:
        return observed

def _subject_from_owned_stdio_episode_v1(runtime, episode, native_call):
    selected, _, _, helpers, _ = runtime
    parent_id=selected['root_thread_id']
    with helpers._held_owned_stdio_child_discovery_v1(selected,episode['logical_task']) as ((child_id,discovered),discovery):
        expected_path=selected['root_agent_path']+'/'+episode['logical_task']
        metadata=native_call(runtime,[('thread/read',{'threadId':ident,'includeTurns':False})
            for ident in (parent_id,child_id)],child_id)
        parent,child=[row['thread'] for row in metadata['responses']]
        sources={'parent':helpers.header(parent),'child':helpers.header(child)}
        helpers.validate_relation(selected,parent,child,sources['parent']['metadata'],sources['child']['metadata'])
        require(child['id']==child_id and all(sources['child'][key]==discovered[key]
            for key in ('physical','header_prefix','metadata')) and sources['child']['metadata']['agent_path']==expected_path and
            custody.lexical_path(parent['path'])==custody.lexical_path(selected['root_source']),'OWNED_STDIO_NATIVE_CHILD_CHANGED')
        return {'episode':episode,'metadata':metadata,'catalog':discovery,'sources':sources,
            'parent_identity':{'thread_id':parent_id,'agent_path':selected['root_agent_path']},
            'actual_child_identity':{'thread_id':child_id,'parent_thread_id':parent_id,'agent_path':expected_path}}


# Live acquisition uses the existing producer, file custody and sticky kernel
# cancellation capability. This creates no thread, store, source selection or H0.
def validate_lifecycle_item_v1(ledger, item, completed, raw=False):
    """Pinned 0.153.4 conservative shapes; terminal transport is not success.

    Injected only by the already pinned helper. Unconfigured ledgers refuse
    lifecycle items. Raw calls stay outstanding independently of typed items.
    """
    def need(ok, reason='LIFECYCLE_ITEM_SHAPE_OR_OUTCOME_UNKNOWN'):
        if not ok:ledger._deny(reason)
    def text(value):return type(value) is str and bool(value)
    kind=item['type']
    if raw:
        common={'type','id','internal_chat_message_metadata_passthrough'}
        need('id' not in item or item['id'] is None or text(item['id']))
        if kind=='reasoning':
            need({'type','summary'}<=set(item)<=common|{'summary','content','encrypted_content'} and
                 type(item['summary']) is list and (item.get('content') is None or type(item['content']) is list))
            return
        output=kind.endswith('_output')
        family=kind.removesuffix('_output')
        need(family in {'function_call','custom_tool_call'})
        identity=item.get('call_id')
        need(text(identity), 'RAW_TOOL_CALL_ID_REQUIRED')
        key=('raw',identity)
        seen=getattr(ledger,'_raw_seen',None)
        if seen is None:seen=ledger._raw_seen=set()
        if not output:
            field='arguments' if family=='function_call' else 'input'
            optional={'namespace','encrypted_function_args'} if family=='function_call' else {'namespace','status'}
            need({'type','call_id','name',field}<=set(item)<=common|{'call_id','name',field}|optional and
                 text(item['name']) and type(item[field]) is str and
                 (item.get('namespace') is None or text(item['namespace'])) and
                 item.get('status') in (None,'completed'), 'RAW_TOOL_CALL_SHAPE_UNKNOWN')
            need(identity not in seen, 'DUPLICATE_RAW_TOOL_CALL')
            seen.add(identity);ledger._items[key]=family
        else:
            optional={'namespace'} if family=='function_call' else set()
            need({'type','call_id','output'}<=set(item)<=common|{'call_id','name','output'}|optional,
                 'RAW_TOOL_OUTPUT_SHAPE_UNKNOWN')
            value=item['output']
            need(type(value) in (str,list), 'RAW_TOOL_OUTPUT_SHAPE_UNKNOWN')
            if type(value) is list:
                fields={'input_text':'text','input_image':'image_url','input_audio':'audio_url','encrypted_content':'encrypted_content'}
                for part in value:
                    need(type(part) is dict and type(part.get('type')) is str and part['type'] in fields, 'RAW_TOOL_OUTPUT_SHAPE_UNKNOWN')
                    field=fields[part['type']]
                    need({'type',field}<=set(part)<={'type',field}|({'detail'} if part['type']=='input_image' else set())
                         and type(part[field]) is str, 'RAW_TOOL_OUTPUT_SHAPE_UNKNOWN')
            need(ledger._items.get(key)==family, 'UNMATCHED_OR_DUPLICATE_RAW_TOOL_OUTPUT')
            del ledger._items[key]
        return
    if kind=='contextCompaction':
        need(set(item)=={'type','id'})
        return
    required,optional,terminal={
        'commandExecution':({'command','commandActions','cwd'},
            {'aggregatedOutput','durationMs','exitCode','pluginId','processId','scriptPath','source'}, {'completed','failed','declined'}),
        'mcpToolCall':({'arguments','server','tool'},
            {'appContext','durationMs','error','mcpAppResourceUri','pluginId','readOnlyHint','result'}, {'completed','failed'}),
        'dynamicToolCall':({'arguments','tool'},
            {'contentItems','durationMs','namespace','success'}, {'completed','failed'}),
        'collabAgentToolCall':({'agentsStates','receiverThreadIds','senderThreadId','tool'},
            {'model','prompt','reasoningEffort'}, {'completed','failed','interrupted'}),
    }[kind]
    required=required|{'type','id','status'}
    need(required<=set(item)<=required|optional and type(item['status']) is str and
         item['status'] in (terminal if completed else {'inProgress'}), 'NONTERMINAL_OR_UNKNOWN_LIFECYCLE_ITEM')
    for name in required-{'type','id','status','arguments','agentsStates','receiverThreadIds','commandActions'}:
        need(text(item[name]))
    if kind=='commandExecution':need(type(item['commandActions']) is list)
    if kind=='collabAgentToolCall':
        need(item['senderThreadId']==ledger._thread and type(item['receiverThreadIds']) is list and
             all(text(value) for value in item['receiverThreadIds']) and type(item['agentsStates']) is dict)
    if 'durationMs' in item:need(item['durationMs'] is None or type(item['durationMs']) is int and item['durationMs']>=0)
    if 'exitCode' in item:need(item['exitCode'] is None or type(item['exitCode']) is int and -(2**31)<=item['exitCode']<2**31)
    if 'success' in item:need(item['success'] is None or type(item['success']) is bool)


class OwnedStdioLiveProducerV1:
    def __init__(self, process, source_owner, claim_owner, producer_pins, *, emit,
                 selected_thread_id=None, native_module=None):
        import types
        require(type(process) is subprocess.Popen and process.poll() is None and
                process.stdin is not None and process.stdout is not None and
                not process.stdin.closed and not process.stdout.closed, 'LIVE_ORIGINAL_POPEN_REQUIRED')
        self.process, self.source_owner, self.claim = process, source_owner, claim_owner
        self.pins = {key:dict(value) for key,value in producer_pins.items()}
        loop_pin = self.pins['loop']
        require(self.pins['helper']['path'] == str(Path(__file__).absolute()), 'LIVE_ACTUAL_HELPER_SOURCE_PATH')
        self.held = []
        self.signal = None
        self._cancelled = __import__('threading').Event()
        try:
            for pin in self.pins.values():
                holder = claim_owner.PinnedFile(Path(pin['path']), max_bytes=512*1024)
                self.held.append(holder)
                source_owner._np_read_pin(pin,512*1024)
            # Read exactly the held, verified loop bytes; normal import path
            # search and a later hash of already executing code are not used.
            loop_raw = source_owner._np_read_pin(loop_pin,128*1024)
            module = types.ModuleType('_owned_stdio_live_loop_'+digest(loop_raw))
            module.__file__ = loop_pin['path']
            exec(compile(loop_raw,loop_pin['path'],'exec',dont_inherit=True),module.__dict__)
            self.loop = module.OwnedStdioLoop(process,source_owner,selected_thread_id=selected_thread_id,
                emit=emit,mode='strict',native_module=native_module)
            self.loop._live_producer = self
            self.loop.ledger._lifecycle_validator = validate_lifecycle_item_v1
            self.process_identity = claim_owner.native_process_identity_v1(process.pid)
            self.producer_identity = claim_owner.native_process_identity_v1(os.getpid())
            self._stdio = (process.stdin,process.stdout,process.stdin.fileno(),process.stdout.fileno())
            self._sealed = None
        except BaseException:
            for holder in reversed(self.held):holder.close()
            raise

    def check(self):
        require(not self._cancelled.is_set(), 'LIVE_CAPTURE_CANCELLED')
        require(self.process.poll() is None and self.process.stdin is self._stdio[0] and
                self.process.stdout is self._stdio[1] and not self.process.stdin.closed and not self.process.stdout.closed and
                (self.process.stdin.fileno(),self.process.stdout.fileno()) == self._stdio[2:] and
                self.claim.native_process_identity_v1(self.process.pid) == self.process_identity and
                self.claim.native_process_identity_v1(os.getpid()) == self.producer_identity,
                'LIVE_OWNED_PROCESS_OR_PIPE_CHANGED')
        for holder in self.held:holder.verify()
        if self.signal is not None:self.signal.check()

    def seal(self, runtime):
        """Freeze an unadmitted initial acquisition from this actual connection."""
        import secrets
        require(self._sealed is None and self.signal is None, 'LIVE_ACQUISITION_ALREADY_ATTEMPTED')
        require(not self._cancelled.is_set(), 'LIVE_CAPTURE_CANCELLED_BEFORE_SIGNAL_INSTALL')
        nonce = secrets.token_hex(16)
        try:
            # Failure/EOF before event installation is sticky. Installation and
            # the final publication fence share the reader's state lock.
            with self.loop._state_lock:
                self.loop.live_acquisition_facts_v1()
                self.signal = self.claim.NativeCancellationSignalV1(nonce)
                if self._cancelled.is_set():self.signal.signal()
                require(not self._cancelled.is_set(), 'LIVE_CAPTURE_CANCELLED_DURING_SIGNAL_INSTALL')
                self.signal.check()
                epoch = self.loop._raw_epoch
            return self._seal(runtime, nonce, epoch)
        except BaseException:
            self.cancel_now()
            if self.signal is not None:self.signal.close()
            raise

    def _seal(self, runtime, nonce, epoch):
        selected, custody_owner, protocol, helpers, _ = runtime
        require(self._sealed is None, 'LIVE_ACQUISITION_ALREADY_SEALED')
        self.check()
        require(self.process.args == [selected['native_executable']['path'],'app-server','--listen','stdio://'] and
                self.process_identity['image'] == selected['native_executable']['path'] and
                self.pins == {'runner':selected['capture_producer_pin'],
                    **{key:selected['producer_dependencies'][name] for key,name in
                       (('loop','owned_stdio_loop.py'),('claim','claim-run-rotation.py'),('helper','bounded_source_owner.py'),('source_owner','compaction-source-owner-codex-app.py'))}},
                'LIVE_PRODUCER_OR_LAUNCH_DIFFERS')
        # The loop returns only facts retained at actual send/reply, under its
        # ingress barrier. No caller supplies a thread/read response or flag.
        facts = self.loop.live_acquisition_facts_v1()
        require(facts['thread_id'] == selected['root_thread_id'] and facts['source_path'] == selected['root_source'] and
                facts['thread_start']['experimentalRawEvents'] is True and
                facts['thread_start']['cwd'] == selected['cwd'], 'LIVE_NATIVE_ACQUISITION_SCOPE')
        header = helpers.header({'path':selected['root_source']})
        require(header['metadata'].get('id') == header['metadata'].get('session_id') == selected['root_thread_id'] and
            header['metadata'].get('cli_version') == selected['cli_version'] and
            Path(header['metadata'].get('cwd','')) == Path(selected['cwd']), 'LIVE_ORIGINAL_HEADER_DIFFERS')
        physical = {key:header['physical'][key] for key in ('device','inode')}
        context = {'parent':{'path':selected['root_source'],'physical':physical,
            'metadata':{'bytes':header['header_prefix']['bytes']}}}
        size = Path(selected['root_source']).stat().st_size
        prefix = self.source_owner.sealed_prefix(helpers._observation_owner,context,'parent',size)
        require(self.loop.live_acquisition_facts_v1() == facts, 'LIVE_CAPTURE_INGRESS_ADVANCED_DURING_SEAL')
        source = {'path':selected['root_source'],'bytes':size,'sha256':prefix['prefix_sha256'],'physical':physical,
            'metadata':{'id':selected['root_thread_id'],'session_id':selected['root_thread_id'],'cli_version':selected['cli_version']}}
        record = {'schema':'implementaudit.owned-stdio-live-acquisition.v1','status':'LIVE_SOURCE_CAPTURED_UNADMITTED',
            'thread_id':selected['root_thread_id'],'native_version':selected['native_version'],
            'native_executable_sha256':selected['native_executable']['sha256'],'transport':'dedicated-owner-started-stdio',
            'profile_admission':'UNADMITTED','native_pending_consumption':False,
            'capture_script_sha256':self.pins['runner']['sha256'],'producer_dependencies':selected['producer_dependencies'],
            'codex_home':selected['codex_home'],'cwd':selected['cwd'],'source':source,'connection':facts,
            'producer_process':self.producer_identity,'host_process':self.process_identity,
            'cancellation':self.signal.descriptor,'connection_id':nonce,'authority_ceiling':'NONE'}
        self.check()
        with self.loop._state_lock:
            require(not self._cancelled.is_set() and self.loop._raw_epoch == epoch and
                    self.loop.live_acquisition_facts_v1() == facts, 'LIVE_CAPTURE_INVALIDATED_DURING_SEAL')
            self.signal.check()
            self._sealed = record
        return json.loads(json.dumps(record))

    def cancel_now(self):
        self._cancelled.set()
        if self.signal is not None and self.signal.handle:self.signal.signal()

    def finish(self):
        self.cancel_now()
        if self.signal is not None:self.signal.close()
        for holder in reversed(self.held):holder.close()


def validate_live_capture_v1(selected, capture, read_pin):
    fields = {'schema','status','thread_id','native_version','native_executable_sha256','transport',
        'profile_admission','native_pending_consumption','capture_script_sha256','producer_dependencies',
        'codex_home','cwd','source','connection','producer_process','host_process','cancellation','connection_id','authority_ceiling'}
    require(type(capture) is dict and set(capture) == fields and
        capture['schema'] == 'implementaudit.owned-stdio-live-acquisition.v1' and
        capture['status'] == 'LIVE_SOURCE_CAPTURED_UNADMITTED' and capture['profile_admission'] == 'UNADMITTED' and
        capture['native_pending_consumption'] is False and capture['authority_ceiling'] == 'NONE' and
        capture['transport'] == 'dedicated-owner-started-stdio' and
        capture['thread_id'] == selected['root_thread_id'] and capture['native_version'] == selected['native_version'] and
        capture['native_executable_sha256'] == selected['native_executable']['sha256'] and
        capture['capture_script_sha256'] == selected['capture_producer_pin']['sha256'] and
        capture['producer_dependencies'] == selected['producer_dependencies'] and
        capture['codex_home'] == selected['codex_home'] and capture['cwd'] == selected['cwd'], 'LIVE_CAPTURE_FIXED_BINDING')
    deps = selected['producer_dependencies']
    require(type(deps) is dict and set(deps) == {'owned_stdio_loop.py','claim-run-rotation.py','bounded_source_owner.py','compaction-source-owner-codex-app.py'}, 'LIVE_PRODUCER_CLOSURE_REQUIRED')
    read_pin(selected['capture_producer_pin'],128*1024)
    read_pin(deps['owned_stdio_loop.py'],128*1024)
    read_pin(deps['claim-run-rotation.py'],512*1024)
    read_pin(deps['bounded_source_owner.py'],128*1024)
    read_pin(deps['compaction-source-owner-codex-app.py'],128*1024)
    facts = capture['connection']
    require(type(facts) is dict and set(facts) == {'thread_id','source_path','thread_start','effective_config',
        'thread_start_response_sha256','thread_read_response_sha256','read_frame_ordinal','wire_prefix_sha256','wire_prefix_bytes'} and
        facts['thread_id'] == selected['root_thread_id'] and facts['source_path'] == selected['root_source'] and
        type(facts['thread_start']) is dict and facts['thread_start'].get('experimentalRawEvents') is True and
        facts['thread_start'].get('cwd') == selected['cwd'] and type(facts['effective_config']) is dict and
        all(type(facts[k]) is str and re.fullmatch('[0-9a-f]{64}',facts[k]) for k in
            ('thread_start_response_sha256','thread_read_response_sha256','wire_prefix_sha256')) and
        all(type(facts[k]) is int and facts[k] > 0 for k in ('read_frame_ordinal','wire_prefix_bytes')), 'LIVE_CAPTURE_CONNECTION_FACTS')
    source = capture['source']
    require(type(source) is dict and set(source) == {'path','bytes','sha256','physical','metadata'} and
        source['path'] == selected['root_source'] and source['metadata'] == {'id':selected['root_thread_id'],
            'session_id':selected['root_thread_id'],'cli_version':selected['cli_version']} and
        type(source['bytes']) is int and source['bytes'] > 0 and re.fullmatch('[0-9a-f]{64}',source['sha256']), 'LIVE_CAPTURE_SOURCE_FACTS')
    return capture


def held_live_capture_v1(selected, capture, claim_owner):
    """Active reads require an actual kernel Event plus current PID/birth/image."""
    from contextlib import contextmanager, ExitStack
    @contextmanager
    def held():
        with ExitStack() as stack:
            waiter = claim_owner.NativeCancellationWaitV1(capture['cancellation'],capture['producer_process'],capture['connection_id'])
            stack.callback(waiter.close)
            pins = [selected['capture_producer_pin'],*selected['producer_dependencies'].values()]
            holders=[]
            for pin in pins:
                holder=claim_owner.PinnedFile(Path(pin['path']),max_bytes=512*1024)
                holders.append(holder);stack.callback(holder.close)
            def verify():
                waiter.check()
                require(claim_owner.native_process_identity_v1(capture['host_process']['pid']) == capture['host_process'] and
                    capture['host_process']['image'] == selected['native_executable']['path'], 'LIVE_HOST_DEAD_OR_REPLACED')
                for holder in holders:holder.verify()
                waiter.check()
            verify(); yield; verify()
    return held()


def read_preopen_route_v1(runtime, executing_owner):
    """Read the selected canonical owner; exceptions are never absence proof."""
    selected=runtime[0];owner=selected['episode_owner']
    route=executing_owner._np_module(owner['module_pin'],'route-transaction.py',runtime[1])
    with route.current_route_observation_v1(Path(owner['repository']),owner['controller']) as observed:
        raw=observed.scope_bytes()
        value=parse(raw)
        require(value.get('schema')=='implementaudit.current-route-scope.v1' and
                value.get('authority_ceiling')=='READ_ONLY_CURRENT_ROUTE_FACT' and
                value.get('route',{}).get('route_state')=='UNSATISFIED' and
                value['route'].get('decision')=='REQUIRED' and
                value.get('owner',{}).get('controller_id')==owner['controller'] and
                value.get('host',{}).get('host_session_id')==selected['root_thread_id'],
                'INITIAL_TRANSFER_REQUIRES_CURRENT_PREOPEN_ROUTE')
    return raw


def transfer_live_interval_v1(runtime, producer, executing_owner, read_release):
    """Transfer actual initialization custody; no old ledger grants acceptance."""
    loop = producer.loop
    require(type(producer.process) is subprocess.Popen and loop.process is producer.process,
            'ORIGINAL_LIVE_PROCESS_REQUIRED_FOR_TRANSFER')
    producer.check()
    require(producer._sealed == executing_owner._as_capture_v1(runtime[0],runtime[1]),
            'LIVE_INITIAL_ACQUISITION_DIFFERS_FROM_SELECTION')
    # Git/pending reads occur outside the ingress lock. The raw epoch barrier
    # rejects any overlap before the new ledger can be made visible.
    with loop._arm_lock:
        with loop._state_lock:
            epoch = loop._raw_epoch
            loop._assert_interval_transferable()
            if read_release is None:
                require(loop._transfer_stage=='CAPTURE' and not loop._retired_intervals and not loop.ledger._lifecycle,
                        'INITIAL_TRANSFER_ALREADY_USED_OR_WRONG_STAGE')
            else:
                require(loop._transfer_stage=='C5_LIFECYCLE', 'C5_TRANSFER_WRONG_STAGE')
        preopen=None if read_release is not None else read_preopen_route_v1(runtime,executing_owner)
        release = None if read_release is None else read_release()
        require(read_release is None or release is not None, 'EXISTING_C5_TERMINAL_RELEASE_REQUIRED')
        if release is not None:
            require(release.get('status') == 'AVAILABLE' and
                release['lifecycle']['source_terminal_release']['status'] == 'SOURCE_OWNER_VALIDATED' and
                release['lifecycle']['join']['status'] == 'JOINED_EVIDENCE_ONLY' and
                release['episode']['parent_identity']['thread_id'] == runtime[0]['root_thread_id'],
                'EXISTING_C5_TERMINAL_RELEASE_REQUIRED')
            # Retain the entire original covered/uncovered census. No row is
            # consumed or relabeled by this transport interval transition.
            retained = {'export_digest':release['export_digest'],'pending':release['pending'],
                        'terminal_release':release['lifecycle']['source_terminal_release']}
            expected_children = {release['episode']['actual_child_identity']['thread_id']}
        else:
            retained = {'kind':'INITIAL_UNADMITTED_CONNECTION_TRANSFER','authority_ceiling':'NONE'}
            expected_children = set()
        producer.check()
        if preopen is not None:
            require(read_preopen_route_v1(runtime,executing_owner)==preopen, 'INITIAL_TRANSFER_ROUTE_CHANGED')
        with loop._state_lock:
            loop._assert_interval_transferable()
            require(loop._raw_epoch == epoch and loop.ledger._children == expected_children,
                    'LIVE_TRANSFER_INGRESS_OR_UNRECONCILED_CHILD')
            old = loop.ledger
            new = executing_owner.OwnedStdioQuiescenceV1(loop.messages,
                selected_thread_id=runtime[0]['root_thread_id'],native_process=producer.process)
            # These are the actual retained exchange objects from the sole
            # sender/reader, not fabricated initialize records or booleans.
            init = loop._actual_initialize
            require(init['sent']['method'] == 'initialize' and type(init['sent']['id']) is int and
                type(init['reply'].get('id')) is int and init['sent']['id'] == init['reply']['id'] and
                loop._actual_initialized == {'method':'initialized'}, 'ORIGINAL_INITIALIZE_EXCHANGE_REQUIRED')
            new.before_send(init['sent']); new.after_record(init['reply']); new.before_send(loop._actual_initialized)
            new._lifecycle_validator=validate_lifecycle_item_v1
            loop._retired_intervals.append((old,retained))
            loop.source_owner=executing_owner;producer.source_owner=executing_owner;loop.ledger=new
            loop.native_state=None;loop._usage_binding=None
            loop._actual_read=None
            loop._actual_resume=None
            loop._transfer_stage='SELECTED_NEEDS_RESUME' if release is None else 'FRESH_NEEDS_RESUME'
            event = {'event':'OWNED_INTERVAL_TRANSFER','retired_intervals':len(loop._retired_intervals),
                     'after_c5':release is not None,'retained_export_digest':None if release is None else release['export_digest'],
                     'authority_ceiling':'NONE','next_required_native_request':'thread/resume'}
        loop.emit(event)  # No fsync/journal work under the raw-ingress lock.
        return retained


def load_live_claim_v1(pin, read_pin):
    # Initial unadmitted producer template and final materialized owner are
    # distinct declared roles. The already frozen canonical claim companion
    # can be held by both; no physical owner equivalence is inferred.
    import types
    require(Path(pin['path']).name == 'claim-run-rotation.py', 'LIVE_CLAIM_COMPANION_NAME')
    raw=read_pin(pin,512*1024)
    module=types.ModuleType('_live_claim_'+digest(raw));module.__file__=pin['path']
    exec(compile(raw,pin['path'],'exec',dont_inherit=True),module.__dict__)
    require(all(callable(getattr(module,name,None)) for name in
        ('PinnedFile','NativeCancellationSignalV1','NativeCancellationWaitV1','native_process_identity_v1')),
        'LIVE_CLAIM_CUSTODY_INTERFACE_REQUIRED')
    return module


def initial_transfer_and_open_v1(runtime, producer, owner, opening, *, execute=False, deadline=None):
    import sys, time
    if execute is not True:
        return {'status':'PREPARED_NO_EFFECTS','sequence':[
            'current UNSATISFIED owner read','one initial selected-owner transfer',
            'actual warm thread/resume on retained pipes','same-source thread/read',
            'fresh exact pre-OPEN owner read','existing route-transaction.py open CAS',
            'existing canonical OPEN readback'], 'authority_ceiling':'NONE'}
    def need(ok,code):
        if not ok:raise ValueError(code)
    selected=runtime[0];loop=producer.loop
    required={'request','packet','logical_task','expected_record','binding_generation'}
    need(type(opening) is dict and set(opening)==required and
         all(type(value) is str and value for value in opening.values()), 'EXACT_PREPARED_OPEN_ARGUMENTS_REQUIRED')
    need(type(deadline) in (int,float) and 0<deadline-time.monotonic()<=30,
         'BOUNDED_INITIAL_DRIVER_DEADLINE_REQUIRED')
    need(owner.OWNED_STDIO_SELECTION_PIN is not None and selected==owner._np_selection() and
         loop._live_producer is producer and loop._transfer_stage=='CAPTURE', 'INITIAL_DRIVER_SCOPE_OR_REPLAY')
    producer.check()
    capture=producer._sealed
    need(type(capture) is dict and capture.get('schema')=='implementaudit.owned-stdio-live-acquisition.v1' and
         capture['thread_id']==selected['root_thread_id'] and capture['source']['path']==selected['root_source'],
         'INITIAL_DRIVER_LIVE_SOURCE_IDENTITY_REQUIRED')
    for key in ('request','packet'):
        path=Path(opening[key])
        need(path.is_absolute() and path.resolve(strict=True)==path, 'PREPARED_OPEN_PATH_ALIAS')
    try:
        with owner._as_provider_guard_v1(runtime):
            owner.transfer_owned_stdio_interval_v1(runtime,producer,after_c5=False)
            resumed=loop.call('thread/resume',{'threadId':selected['root_thread_id'],
                'excludeTurns':True,'approvalPolicy':'never','sandbox':'read-only'},deadline)
            need(resumed.get('thread',{}).get('id')==selected['root_thread_id'] and
                 resumed['thread'].get('path')==selected['root_source'], 'WARM_RESUME_ACTUAL_SOURCE_CHANGED')
            read=loop.call('thread/read',{'threadId':selected['root_thread_id'],'includeTurns':False},deadline)
            need(read.get('thread',{}).get('id')==selected['root_thread_id'] and
                 read['thread'].get('path')==selected['root_source'], 'WARM_READ_ACTUAL_SOURCE_CHANGED')
            scope=json.loads(runtime[3].read_preopen_route_v1(runtime,owner))
            need(scope['route']['record_oid']==opening['expected_record'] and
                 scope['host']['host_binding_generation']==opening['binding_generation'], 'PREOPEN_EXPECTED_OWNER_CHANGED')
            episode_owner=selected['episode_owner'];pin=episode_owner['module_pin']
            owner._np_read_pin(pin,512*1024,runtime[1])
            producer.check()
            with loop._state_lock:
                loop._assert_interval_transferable()
                need(loop._transfer_stage=='SELECTED_RESUMED' and loop._actual_resume is not None,
                     'OPEN_REQUIRES_ACTUAL_SELECTED_WARM_RESUME')
                loop._transfer_stage='OPEN_IN_FLIGHT'
            argv=[sys.executable,'-I','-S','-B',pin['path'],'open',
                '--controller',episode_owner['controller'],'--store',selected['pending_owner']['store'],
                '--host-id','codex','--host-session-id',selected['root_thread_id'],
                '--binding-generation',opening['binding_generation'],'--request',opening['request'],
                '--expected-record',opening['expected_record'],'--packet',opening['packet'],
                '--logical-task',opening['logical_task']]
            remaining=deadline-time.monotonic()
            need(remaining>0,'INITIAL_DRIVER_DEADLINE_BEFORE_OPEN')
            with producer.claim.PinnedFile(Path(pin['path']),max_bytes=512*1024) as route_file:
                raw=route_file.read()
                need(len(raw)==pin['bytes'] and digest(raw)==pin['sha256'], 'OPEN_OWNER_SOURCE_CHANGED')
                result=subprocess.run(argv,cwd=episode_owner['repository'],capture_output=True,
                    check=False,timeout=remaining)
                route_file.verify()
            need(result.returncode==0,'EXISTING_OPEN_REFUSED_OR_UNKNOWN_READBACK_REQUIRED')
            opened=json.loads(result.stdout)
            need(opened.get('status')=='CHILD_OPEN','EXISTING_OPEN_RESULT_UNKNOWN')
            owner._np_read_pin(pin,512*1024,runtime[1]);producer.check()
            episode=owner._np_episode(runtime)
            need(episode['logical_task']==opening['logical_task'] and
                 episode['host_and_scope']['host_session_id']==selected['root_thread_id'] and
                 episode['open_record_oid']==opened.get('record_oid') and
                 episode['open_record_identity']==opened.get('record_identity'), 'OPEN_READBACK_IDENTITY_CHANGED')
            with loop._state_lock:
                loop._assert_interval_transferable()
                need(loop._transfer_stage=='OPEN_IN_FLIGHT','OPEN_STAGE_CHANGED')
                loop._transfer_stage='OPEN_VERIFIED'
            return {'status':'EXISTING_OPEN_VERIFIED_NATIVE_CHILD_NOT_STARTED',
                    'open':opened,'episode':episode,'authority_ceiling':'NONE'}
    except BaseException as exc:
        # CAS can already have occurred. The stopped, sticky producer cannot be
        # replayed; ROOT must reconcile the existing owner before any successor.
        loop._record_failure(exc)
        raise


def owned_stdio_public_turn_v2(obs, context, role, pin):
    """Read the complete finite 0.153.4 public interval, segmented by real turns.

    The C5 protocol has seven parent turns through its final release. Each turn
    retains the original 64-frame limit; the fresh child still has exactly one
    turn. The original two-MiB whole interval and per-frame byte bounds remain.
    Every byte/frame from the bound original anchor to selected response is read.
    No profile, turn ID, source locator or native-public confirmation is minted.
    """
    require(context.get('profile_id') == 'codex-app-server-0.153.4-owned-stdio-candidate-v1'
            and role in ('parent', 'child') and obs.MAX_RECORDS == 64, 'OWNED_STDIO_PUBLIC_PROFILE_SCOPE')
    anchor = context['parent_turn_start'] if role == 'parent' else context['child_activation']
    first_locator, last_locator = anchor['locator'], pin['locator']
    start, end = first_locator['offset'], last_locator['offset'] + last_locator['bytes']
    require(type(start) is int and type(end) is int and 0 <= start < end and end-start <= obs.MAX_TOTAL,
            'OWNED_STDIO_PUBLIC_TURN_BOUND')
    path, before = obs.physical(context[role]['path'])
    require(obs.identity(before) == context[role]['physical'] and end <= before.st_size,
            'OWNED_STDIO_PUBLIC_PHYSICAL_CHANGED')
    maximum_turns = 7 if role == 'parent' else 1
    active, seen, frames, context_seen, previous_ordinal = None, set(), 0, False, None
    uuid = r'[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}'
    selected_seen = False
    position = start
    prefix_hash = hashlib.sha256()
    with path.open('rb') as stream:
        require(obs.identity(os.fstat(stream.fileno())) == context[role]['physical'],
                'OWNED_STDIO_PUBLIC_PHYSICAL_CHANGED')
        stream.seek(start)
        while position < end:
            raw = stream.readline(min(obs.MAX_RECORD+1, end-position))
            require(raw and raw.endswith(b'\n') and raw.count(b'\n') == 1
                    and b'\r' not in raw and b'\0' not in raw and len(raw) <= obs.MAX_RECORD,
                    'OWNED_STDIO_PUBLIC_TURN_FRAME')
            row = obs.json.loads(raw, object_pairs_hook=obs.unique)
            require(type(row) is dict and set(row) == {'timestamp', 'ordinal', 'type', 'payload'}
                    and type(row['payload']) is dict and type(row['type']) is str
                    and type(row['timestamp']) is str and type(row['ordinal']) is int and row['ordinal'] >= 0,
                    'OWNED_STDIO_PUBLIC_FRAME_SHAPE')
            require(previous_ordinal is None or row['ordinal'] == previous_ordinal+1,
                    'OWNED_STDIO_PUBLIC_ORDINAL_GAP_OR_REPLAY')
            previous_ordinal = row['ordinal']
            p, kind = row['payload'], row['type']
            event = p.get('type') if kind == 'event_msg' else None
            if position == start:
                require(len(raw) == first_locator['bytes'] and digest(raw) == first_locator['sha256']
                        and row['ordinal'] == first_locator['embedded_ordinal'] and event == 'task_started',
                        'OWNED_STDIO_ORIGINAL_TURN_ANCHOR_CHANGED')
            if event == 'task_started':
                identity = p.get('turn_id')
                require(active is None, 'OWNED_STDIO_PUBLIC_OVERLAPPING_TURNS')
                require(type(identity) is str and re.fullmatch(uuid, identity) and identity not in seen,
                        'OWNED_STDIO_PUBLIC_DUPLICATE_OR_UNKNOWN_TURN')
                seen.add(identity)
                require(len(seen) <= maximum_turns, 'OWNED_STDIO_PUBLIC_TURN_POPULATION_BOUND')
                active, frames, context_seen = identity, 0, False
            else:
                require(active is not None, 'OWNED_STDIO_PUBLIC_FRAME_OUTSIDE_ACTUAL_TURN')
            frames += 1
            require(frames <= obs.MAX_RECORDS, 'OWNED_STDIO_PUBLIC_TURN_FRAME')
            if 'turn_id' in p:
                require(p['turn_id'] == active, 'OWNED_STDIO_PUBLIC_FOREIGN_TURN_FRAME')
            if kind == 'turn_context':
                require(not context_seen and p.get('turn_id') == active,
                        'OWNED_STDIO_PUBLIC_CONTEXT_ABSENT_DUPLICATE_OR_FOREIGN')
                require(type(p.get('root_turn_id')) is str and re.fullmatch(uuid, p['root_turn_id'])
                        and (role != 'parent' or p['root_turn_id'] == active),
                        'OWNED_STDIO_PUBLIC_ROOT_TURN_CHANGED')
                context_seen = True
            elif event == 'task_complete':
                require(context_seen and p.get('turn_id') == active, 'OWNED_STDIO_PUBLIC_TERMINAL_WITHOUT_CONTEXT')
                active = None
            elif kind == 'event_msg':
                require(event in ('task_started', 'item_completed', 'token_count'),
                        'OWNED_STDIO_PUBLIC_UNKNOWN_OR_INVALIDATING_EVENT')
                require(event != 'item_completed' or p.get('turn_id') == active,
                        'OWNED_STDIO_PUBLIC_FOREIGN_TURN_FRAME')
            elif kind == 'token_usage_record':
                require(p.get('turn_id') == active, 'OWNED_STDIO_PUBLIC_FOREIGN_TURN_FRAME')
            elif kind == 'response_item':
                require(p.get('type') in ('message', 'reasoning', 'function_call', 'function_call_output',
                        'custom_tool_call', 'custom_tool_call_output', 'agent_message'),
                        'OWNED_STDIO_PUBLIC_UNKNOWN_RESPONSE_FRAME')
            else:
                require(kind in ('world_state', 'inter_agent_communication_metadata'),
                        'OWNED_STDIO_PUBLIC_UNKNOWN_FRAME')
            if position == last_locator['offset']:
                require(len(raw) == last_locator['bytes'] and digest(raw) == last_locator['sha256']
                        and row['ordinal'] == last_locator['embedded_ordinal'] and position+len(raw) == end
                        and active is not None and context_seen and kind == 'response_item'
                        and p.get('type') == 'message' and p.get('role') == 'assistant',
                        'OWNED_STDIO_SELECTED_PUBLIC_RESPONSE_CHANGED')
                selected_seen = True
            prefix_hash.update(raw)
            position += len(raw)
        after = os.fstat(stream.fileno())
        # Recheck the entire traversed original prefix, not just the chosen row.
        stream.seek(start)
        checked = hashlib.sha256()
        remaining = end-start
        while remaining:
            raw = stream.read(min(65536, remaining))
            require(raw, 'OWNED_STDIO_PUBLIC_PREFIX_TRUNCATED')
            checked.update(raw)
            remaining -= len(raw)
    _, current = obs.physical(path)
    require(selected_seen and position == end and checked.digest() == prefix_hash.digest()
            and obs.identity(before) == obs.identity(after) == obs.identity(current)
            and (before.st_size, before.st_mtime_ns) == (after.st_size, after.st_mtime_ns)
                == (current.st_size, current.st_mtime_ns), 'OWNED_STDIO_PUBLIC_PREFIX_CHANGED')
    return active
