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
    source = physical(path)
    with custody.held_file(path) as stream:
        require(same_physical(os.fstat(stream.fileno()), source), "HEADER_SOURCE_CHANGED")
        raw = stream.readline(MAX_RECORD + 1)
        require(len(raw) <= MAX_RECORD and raw.endswith(b"\n"), "HEADER_RANGE_BOUND")
        cutoff = os.fstat(stream.fileno()).st_size
    row = parse(raw)
    require(row.get("type") == "session_meta" and isinstance(row.get("payload"), dict), "HEADER_TYPE")
    payload = row["payload"]
    fields = ("id", "session_id", "parent_thread_id", "agent_path", "cli_version", "cwd",
              "originator", "thread_source", "history_mode")
    require(physical(path) == source, "HEADER_SOURCE_CHANGED")
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
            p.get("phase") in ("commentary", "final"), "PUBLIC_RECORD_REQUIRED")
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
            if row.get("type") == "response_item" and p.get("type") == "message" and p.get("role") == "assistant" and p.get("phase") in ("commentary", "final"):
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
