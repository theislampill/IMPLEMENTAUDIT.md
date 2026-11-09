"""Pure selected-profile receiving for two fixed Codex package body cases.

This module performs no I/O, dispatch, import of target code or model inference.
Unknown native forms are failures; all arbitrary strings remain private.
"""
from __future__ import annotations
import hashlib, json, math, re, shlex

MODEL = "dg17-package-body-fixture"
PROVIDER = "dg17_loopback"
FAMILIES = ("canonical", "standalone")
GOVERNOR_BYTES = 21257
GOVERNOR_SHA = "4c8363c2235ba6c50675c93af7319aeb0caf57f020c4858eba1c28e76de4c6c5"
PREFIX_BYTES = 8000
PREFIX_SHA = "3c89161abdc251c3973122ed1d0e0e52b582e144b8d9f50148246972e2f1d791"
SKILLS = ("implementaudit", "audit-state", "audit-assess", "audit-implement", "audit-andon")
NAME_MAP = {"implementaudit:"+name:name for name in SKILLS}
RPC_METHODS = {
    "canonical": ("initialize", "plugin/install", "plugin/read", "skills/list", "hooks/list", "thread/start", "turn/start"),
    "standalone": ("initialize", "skills/list", "hooks/list", "thread/start", "turn/start"),
}
MAX_JSON_BYTES = 2097152
STARTUP_BWRAP_WARNINGS = {
    "SYSTEM_BWRAP_MISSING": "Codex could not find bubblewrap on PATH. Install bubblewrap with your OS package manager. See the sandbox prerequisites: https://developers.openai.com/codex/concepts/sandboxing#prerequisites. Codex will use the bundled bubblewrap in the meantime.",
    "SYSTEM_BWRAP_USER_NAMESPACE": "Codex's Linux sandbox uses bubblewrap and needs access to create user namespaces.",
    "SYSTEM_BWRAP_WSL1": "Codex's Linux sandbox uses bubblewrap, which is not supported on WSL1 because WSL1 cannot create the required user namespaces. Use WSL2 for sandboxed shell commands.",
}

class Refusal(RuntimeError): pass

def need(ok, code):
    if not ok: raise Refusal(code)

def sha(raw): return hashlib.sha256(raw).hexdigest()

def encoded(value):
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True, allow_nan=False)+"\n").encode()

def compact(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False).encode()

def unique(pairs):
    obj = {}
    for key, value in pairs:
        need(key not in obj, "DUPLICATE_JSON_KEY")
        obj[key] = value
    return obj

def parsed(raw):
    need(type(raw) is bytes and len(raw) <= MAX_JSON_BYTES, "JSON_BYTES_BOUND")
    def bad_number(unused): raise Refusal("NONFINITE_JSON")
    try: value = json.loads(raw.decode("utf-8", "strict"), object_pairs_hook=unique, parse_constant=bad_number)
    except (UnicodeError, ValueError, RecursionError) as exc: raise Refusal("JSON_DECODE_REFUSED") from exc
    pending = [(value, 0)]; count = 0
    while pending:
        item, depth = pending.pop(); count += 1
        need(depth <= 32 and count <= 65536, "JSON_STRUCTURE_BOUND")
        if type(item) is dict:
            need(all(type(k) is str and len(k.encode("utf-8")) <= 1024 for k in item), "JSON_KEY_BOUND")
            pending.extend((v, depth+1) for v in item.values())
        elif type(item) is list: pending.extend((v, depth+1) for v in item)
        elif type(item) is str:
            try: need(len(item.encode("utf-8", "strict")) <= MAX_JSON_BYTES, "JSON_STRING_BOUND")
            except UnicodeError as exc: raise Refusal("JSON_STRING_UTF8") from exc
        elif type(item) is float: need(math.isfinite(item), "NONFINITE_JSON")
        else: need(item is None or type(item) in (bool, int), "JSON_SCALAR_TYPE")
    return value

def exact(left, right): return compact(left) == compact(right)

def refuse_startup_warning(params):
    # Pinned serde emits summary + details:null, omitting path/range. A recognized
    # warning is still fatal for this operation's system-only sandbox contract.
    need(type(params) is dict and set(params)=={"summary","details"} and params["details"] is None
         and type(params["summary"]) is str,"STARTUP_CONFIG_WARNING_UNRECEIVED")
    code=next((key for key,value in STARTUP_BWRAP_WARNINGS.items() if params["summary"]==value),None)
    need(code is not None,"STARTUP_CONFIG_WARNING_UNRECEIVED")
    raise Refusal(code)

def safe_path(value):
    need(type(value) is str and 1 < len(value.encode("ascii", "strict")) <= 512
         and re.fullmatch(r"/[A-Za-z0-9_./-]+", value) is not None
         and all(part not in ("", ".", "..") for part in value.split("/")[1:]), "FIXED_PATH_REFUSED")
    return value

def context(family, name, target, cwd, governor):
    need(family in FAMILIES and name == ("implementaudit:implementaudit" if family == "canonical" else "implementaudit"), "SELECTED_NAME")
    target = safe_path(target); cwd = safe_path(cwd)
    need(type(governor) is bytes and len(governor) == GOVERNOR_BYTES and sha(governor) == GOVERNOR_SHA, "GOVERNOR_PIN")
    text = governor.decode("utf-8", "strict")
    prefix = governor[:PREFIX_BYTES]
    # Pinned Host read is whole UTF8 bytes; the exact file's 8000th byte is a character boundary.
    need(len(prefix) == PREFIX_BYTES and sha(prefix) == PREFIX_SHA, "INITIAL_PREFIX_PIN")
    prefix_text = prefix.decode("utf-8", "strict")
    fragment = "<skill>\n<name>"+name+"</name>\n<path>"+target+"</path>\n"+prefix_text+"\n</skill>"
    cmd = "/usr/bin/cat -- '"+target+"'"
    return {"family":family, "name":name, "target":target, "cwd":cwd, "governor":text,
            "fragment":fragment, "marker":"DG17_FIXED_GOVERNOR_CONTENT_"+family.upper(),
            "call_id":"dg17_governor_read_"+family, "ack":"DG17_CONTENT_ACK_"+family.upper(),
            "args":{"cmd":cmd, "workdir":cwd, "shell":"/usr/bin/bash", "login":False,
                    "tty":False, "yield_time_ms":30000, "max_output_tokens":8192,
                    "sandbox_permissions":"use_default"}}

def config_document(home, tmp, port):
    safe_path(home); safe_path(tmp)
    need(type(port) is int and 1024 <= port <= 65535, "PROVIDER_PORT")
    doc = {"model":MODEL, "model_provider":PROVIDER, "approval_policy":"never",
           "sandbox_mode":"read-only", "allow_login_shell":False, "tool_output_token_limit":16384,
           "cli_auth_credentials_store":"ephemeral", "mcp_oauth_credentials_store":"file",
           "features":{"plugins":True,"plugin_discovery_prefetch":False,"remote_plugin":False,
                       "shell_tool":True,"unified_exec":True,"exec_permission_approvals":False,
                       "shell_snapshot":False,"shell_snapshot_v2":False,"code_mode":False,"code_mode_only":False},
           "analytics":{"enabled":False}, "feedback":{"enabled":False},
           "shell_environment_policy":{"inherit":"none","use_profile":False,
                 "set":{"HOME":home,"PATH":"/usr/bin:/bin","TMPDIR":tmp,"LANG":"C.UTF-8","LC_ALL":"C.UTF-8"}},
           "model_providers":{PROVIDER:{"name":"DG17 fixed local content fixture",
                 "base_url":"http://127.0.0.1:"+str(port)+"/v1", "wire_api":"responses",
                 "requires_openai_auth":False,"supports_websockets":False,
                 "request_max_retries":0,"stream_max_retries":0,"stream_idle_timeout_ms":15000}}}
    lines = []
    def emit(table, path=()):
        if path: lines.append("["+".".join(path)+"]")
        for key, value in table.items():
            if type(value) is not dict: lines.append(key+" = "+json.dumps(value, ensure_ascii=True))
        lines.append("")
        for key, value in table.items():
            if type(value) is dict: emit(value, path+(key,))
    emit(doc)
    return doc, ("\n".join(lines)+"\n").encode()

def initial_requests(family, image, cwd):
    need(family in FAMILIES, "CASE_FAMILY")
    requests = [{"id":1,"method":"initialize","params":{"clientInfo":{"name":"dg17_package_content","version":"1.0.0"},"capabilities":{"experimentalApi":True}}}, {"method":"initialized"}]
    if family == "canonical":
        requests.extend([{"id":2,"method":"plugin/install","params":{"pluginName":"implementaudit","marketplacePath":image+"/.claude-plugin/marketplace.json"}},
                         {"id":3,"method":"plugin/read","params":{"pluginName":"implementaudit","marketplacePath":image+"/.claude-plugin/marketplace.json"}}])
    next_id = 4 if family == "canonical" else 2
    requests.extend([{"id":next_id,"method":"skills/list","params":{"cwds":[cwd],"forceReload":True}},
                     {"id":next_id+1,"method":"hooks/list","params":{"cwds":[cwd]}}])
    return requests

def thread_request(family, cwd):
    return {"id":6 if family == "canonical" else 4,"method":"thread/start",
            "params":{"cwd":cwd,"approvalPolicy":"never","approvalsReviewer":"user","sandbox":"read-only","ephemeral":True,
                      "model":MODEL,"modelProvider":PROVIDER}}

def turn_request(ctx, thread_id):
    need(type(thread_id) is str and re.fullmatch(r"[A-Za-z0-9_-]{1,128}", thread_id), "THREAD_ID_SHAPE")
    return {"id":7 if ctx["family"] == "canonical" else 5,"method":"turn/start",
            "params":{"threadId":thread_id,"input":[{"type":"text","text":ctx["marker"],"text_elements":[]},
                      {"type":"skill","name":ctx["name"],"path":ctx["target"]}]}}

def advertisement(tools):
    need(type(tools) is list and 1 <= len(tools) <= 128, "TOOL_ADVERTISEMENT_BOUND")
    found = [row for row in tools if type(row) is dict and row.get("name") == "exec_command"]
    need(len(found) == 1, "EXACT_EXEC_ADVERTISEMENT_MISSING")
    row = found[0]
    need(set(row) == {"type","name","description","strict","parameters"}
         and row["type"] == "function" and row["strict"] is False
         and type(row["description"]) is str and len(row["description"].encode()) <= 4096, "EXEC_PROFILE_UNRECEIVED")
    params = row["parameters"]
    need(type(params) is dict and set(params) == {"type","properties","required","additionalProperties"}
         and params["type"] == "object" and params["required"] == ["cmd"]
         and params["additionalProperties"] is False and type(params["properties"]) is dict, "EXEC_PARAMETERS_UNRECEIVED")
    types = {"cmd":"string","workdir":"string","shell":"string","login":"boolean","tty":"boolean",
             "yield_time_ms":"number","max_output_tokens":"number","sandbox_permissions":"string",
             "justification":"string","prefix_rule":"array"}
    need(set(params["properties"]) == set(types), "EXEC_PROPERTY_POPULATION")
    for key, kind in types.items():
        prop = params["properties"][key]
        extras = {"enum"} if key == "sandbox_permissions" else {"items"} if key == "prefix_rule" else set()
        need(type(prop) is dict and set(prop) == {"type","description"}|extras
             and prop["type"] == kind and type(prop["description"]) is str
             and len(prop["description"].encode()) <= 8192, "EXEC_PROPERTY_SHAPE")
        if key == "sandbox_permissions": need(prop["enum"] == ["use_default","require_escalated"], "EXEC_SANDBOX_PROFILE")
        if key == "prefix_rule": need(prop["items"] == {"type":"string"}, "EXEC_PREFIX_ITEM_PROFILE")
    return {"exec_command_advertised":True,"exec_profile_exact":True,"advertised_tool_count":len(tools),
            "advertised_tools_sha256":sha(encoded(tools)),"exec_advertisement_sha256":sha(encoded(row))}

def input_texts(items, role=None):
    values = []
    for item in items:
        if type(item) is not dict or (role is not None and item.get("role") != role): continue
        content = item.get("content")
        if type(content) is str: values.append(content)
        elif type(content) is list:
            for part in content:
                if type(part) is dict and part.get("type") in ("input_text","output_text") and type(part.get("text")) is str:
                    values.append(part["text"])
    return values

def provider_projection(raw, ctx, ordinal):
    value = parsed(raw)
    need(type(value) is dict and value.get("model") == MODEL and value.get("stream") is True
         and type(value.get("input")) is list and len(value["input"]) <= 256, "RESPONSES_REQUEST_PROFILE")
    items = value["input"]; base = {"ordinal":ordinal,"request_bytes":len(raw),"request_sha256":sha(raw)}
    if ordinal == 1:
        ad = advertisement(value.get("tools"))
        texts = input_texts(items, "user")
        need(sum(text.count(ctx["fragment"]) for text in texts) == 1, "EXACT_INITIAL_FRAGMENT_MISSING")
        need(sum(text.count(ctx["marker"]) for text in texts) == 1, "FIXED_USER_MARKER_MISSING")
        need(all(ctx["governor"] not in text for text in input_texts(items)), "UNEXPECTED_FULL_BODY_IN_INITIAL_INPUT")
        need(not any(type(item) is dict and item.get("type") in ("function_call","function_call_output") for item in items), "INITIAL_TOOL_HISTORY_PRESENT")
        return {**base,**ad,"typed_fragment_exact":True,"typed_fragment_bytes":len(ctx["fragment"].encode()),
                "typed_fragment_sha256":sha(ctx["fragment"].encode()),"raw_prefix_bytes":PREFIX_BYTES,
                "raw_prefix_sha256":PREFIX_SHA,"full_body_present_initially":False}
    need(ordinal == 2, "RESPONSES_REQUEST_QUOTA")
    calls = [item for item in items if type(item) is dict and item.get("type") == "function_call"]
    outputs = [item for item in items if type(item) is dict and item.get("type") == "function_call_output"]
    need(len(calls) == len(outputs) == 1, "EXACT_ONE_NATIVE_TOOL_RETURN")
    call, output = calls[0], outputs[0]
    need(call.get("call_id") == ctx["call_id"] and call.get("name") == "exec_command"
         and type(call.get("arguments")) is str and exact(parsed(call["arguments"].encode()), ctx["args"]), "NATIVE_CALL_BINDING")
    need(output.get("call_id") == ctx["call_id"] and type(output.get("output")) is str, "ORDINARY_NATIVE_TOOL_OUTPUT_PROFILE")
    raw_output = output["output"].encode("utf-8", "strict")
    pattern = rb"(?:Chunk ID: [A-Za-z0-9_-]{1,128}\n)?Wall time: [0-9]+(?:\.[0-9]+)? seconds\nProcess exited with code 0\n(?:Original token count: [0-9]+\n)?Output:\n"
    match = re.match(pattern, raw_output)
    need(match is not None and raw_output[match.end():] == ctx["governor"].encode(), "FULL_TERMINAL_TOOL_BODY_UNRECEIVED")
    return {**base,"matching_call_id":True,"exact_fixed_arguments":True,"terminal_exit_zero":True,
            "live_session_returned":False,"full_governor_received":True,"full_governor_bytes":GOVERNOR_BYTES,
            "full_governor_sha256":GOVERNOR_SHA,"tool_output_bytes":len(raw_output),
            "tool_output_sha256":sha(raw_output),"body_offset_utf8":match.end(),
            "body_end_utf8":len(raw_output),"requested_output_tokens":8192,"configured_output_tokens":16384}

def response_bytes(ctx, ordinal):
    need(ordinal in (1,2), "SSE_RESPONSE_QUOTA")
    rid = "resp_dg17_"+ctx["family"]+"_"+str(ordinal)
    if ordinal == 1:
        item = {"type":"function_call","id":"fc_"+ctx["family"],"call_id":ctx["call_id"],
                "name":"exec_command","arguments":compact(ctx["args"]).decode(),"status":"completed"}
    else:
        item = {"type":"message","id":"msg_"+ctx["family"],"role":"assistant","status":"completed",
                "content":[{"type":"output_text","text":ctx["ack"],"annotations":[]}]}
    events = [
        {"type":"response.created","response":{"id":rid}},
        {"type":"response.output_item.done","output_index":0,"item":item},
        {"type":"response.completed","response":{"id":rid,"status":"completed","output":[item],
          "usage":{"input_tokens":0,"output_tokens":0,"total_tokens":0}}},
    ]
    return b"".join(b"event: "+event["type"].encode()+b"\ndata: "+compact(event)+b"\n\n" for event in events)

def command_projection(item, ctx):
    need(type(item) is dict and item.get("type") == "commandExecution" and item.get("id") == ctx["call_id"]
         and item.get("cwd") == ctx["cwd"] and item.get("status") == "completed"
         and type(item.get("exitCode")) is int and item["exitCode"] == 0
         and type(item.get("command")) is str, "TERMINAL_NATIVE_COMMAND_IDENTITY")
    try: tokens = shlex.split(item["command"], posix=True)
    except ValueError as exc: raise Refusal("NATIVE_COMMAND_DISPLAY_UNRECEIVED") from exc
    need(tokens == ["/usr/bin/bash","-c",ctx["args"]["cmd"]], "NATIVE_COMMAND_ARGV_DIFFERS")
    # Display is source-derived shlex_join(argv), after secret redaction. No actual secret is admitted.
    aggregate = item.get("aggregatedOutput")
    need(aggregate is None or type(aggregate) is str, "COMMAND_AGGREGATE_TYPE")
    if aggregate is not None: need(aggregate.encode() == ctx["governor"].encode(), "COMMAND_AGGREGATE_DIFFERS")
    return {"command_id_matches":True,"command_argv_matches":True,"cwd_matches":True,
            "completed":True,"exit_code":0,"aggregate_present":aggregate is not None,
            "aggregate_full_body_matches":aggregate is not None}

ALLOWED_NOTIFICATIONS = frozenset({"skills/changed","remoteControl/status/changed","warning",
    "thread/started","thread/status/changed","thread/tokenUsage/updated","turn/started","turn/completed",
    "item/started","item/completed","item/commandExecution/outputDelta","item/agentMessage/delta"})

def wire_projection(events, expected_sends, ctx=None, thread_id=None, turn_id=None, complete=False):
    need(type(events) is list and len(events) <= 1024, "NATIVE_EVENT_BOUND")
    sent=[]; responses={}; notifications=[]; commands=[]; agent_texts=[]; completed_turns=[]; warning_hashes=[]
    for index, event in enumerate(events):
        need(type(event) is dict and set(event) == {"sequence","direction","value"}
             and type(event["sequence"]) is int and event["sequence"] == index+1, "WIRE_RECORD_SHAPE")
        value=event["value"]
        if event["direction"] == "send":
            need(len(sent)<len(expected_sends) and exact(value,expected_sends[len(sent)]), "NONADMITTED_RPC_SEND")
            sent.append(value); continue
        need(event["direction"] == "receive" and type(value) is dict, "WIRE_DIRECTION")
        if "id" in value:
            need(set(value)=={"id","result"} and type(value["id"]) is int
                 and value["id"] in {r["id"] for r in sent if "id" in r} and value["id"] not in responses, "SERVER_REQUEST_ERROR_OR_UNKNOWN_ID")
            responses[value["id"]]=value["result"];continue
        need(set(value)=={"method","params","emittedAtMs"} and type(value["emittedAtMs"]) is int
             and 0<=value["emittedAtMs"]<=9223372036854775807 and value["method"] in ALLOWED_NOTIFICATIONS
             and type(value["params"]) is dict, "UNKNOWN_NATIVE_NOTIFICATION")
        method=value["method"]; params=value["params"]; notifications.append(method)
        if method=="skills/changed": need(params=={},"SKILLS_CHANGED_PROFILE")
        elif method=="remoteControl/status/changed":
            need(params.get("status")=="disabled" and params.get("environmentId") is None, "REMOTE_CONTROL_UNADMITTED")
        elif method=="warning":
            need(ctx is not None and set(params)=={"threadId","message"} and params.get("threadId")==thread_id
                 and params.get("message")=="Skill `"+ctx["name"]+"` exceeded the main prompt context limit and was truncated.",
                 "WARNING_NOT_EXACT_SELECTED_TRUNCATION")
            warning_hashes.append(sha(params["message"].encode()))
        elif method.startswith("item/"):
            need(thread_id is not None and params.get("threadId")==thread_id, "ITEM_THREAD_ID")
            if turn_id is not None: need(params.get("turnId")==turn_id,"ITEM_TURN_ID")
            if method in ("item/started","item/completed"):
                item=params.get("item");need(type(item) is dict and item.get("type") in ("userMessage","agentMessage","commandExecution"),"UNADMITTED_NATIVE_ITEM")
                if method=="item/completed":
                    need(type(params.get("completedAtMs")) is int and 0<=params["completedAtMs"]<=9223372036854775807,"ITEM_COMPLETED_TIMESTAMP")
                    if item["type"]=="commandExecution":
                        need(ctx is not None,"COMMAND_BEFORE_CONTEXT");commands.append(command_projection(item,ctx))
                    elif item["type"]=="agentMessage":
                        need(type(item.get("text")) is str,"AGENT_MESSAGE_TYPE");agent_texts.append(item["text"])
                elif item["type"]=="commandExecution":
                    need(ctx is not None and item.get("id")==ctx["call_id"] and item.get("cwd")==ctx["cwd"],"STARTED_COMMAND_BINDING")
            else:
                need(type(params.get("delta")) is str,"DELTA_TYPE")
                if method=="item/commandExecution/outputDelta":need(ctx is not None and params.get("itemId")==ctx["call_id"],"OUTPUT_DELTA_CALL_ID")
        elif method=="turn/completed":
            need(params.get("threadId")==thread_id and type(params.get("turn")) is dict,"COMPLETED_TURN_SCOPE")
            turn=params["turn"]
            need(turn.get("id")==turn_id and turn.get("status")=="completed" and turn.get("error") is None,"NATIVE_TURN_NOT_SUCCESSFUL")
            completed_turns.append(turn)
        elif method=="turn/started":
            need(params.get("threadId")==thread_id and type(params.get("turn")) is dict,"STARTED_TURN_SCOPE")
            if turn_id is not None:need(params["turn"].get("id")==turn_id,"STARTED_TURN_ID")
        elif method=="thread/started":
            need(type(params.get("thread")) is dict,"STARTED_THREAD_SHAPE")
            if thread_id is not None:need(params["thread"].get("id")==thread_id,"STARTED_THREAD_ID")
        elif method in ("thread/status/changed","thread/tokenUsage/updated"):
            need(params.get("threadId")==thread_id,"THREAD_NOTIFICATION_SCOPE")
    if complete:
        need(sent==expected_sends and set(responses)=={r["id"] for r in sent if "id" in r},"EXACT_RPC_POPULATION")
        need(len(commands)==len(completed_turns)==1 and agent_texts==[ctx["ack"]],"EXACT_NATIVE_TURN_COMPLETION")
        need(len(warning_hashes)==1,"EXACT_TYPED_TRUNCATION_WARNING_MISSING")
    return {"response_count":len(responses),"notification_count":len(notifications),
            "notification_methods":sorted(set(notifications)),"warning_count":len(warning_hashes),
            "warning_messages_sha256":sha(encoded(warning_hashes)),"terminal_command_count":len(commands),
            "turn_completed_count":len(completed_turns),"fixed_ack_observed":ctx is not None and agent_texts==[ctx["ack"]],
            "unknown_frames":0,"server_requests":0,"command":commands[0] if len(commands)==1 else None},responses
