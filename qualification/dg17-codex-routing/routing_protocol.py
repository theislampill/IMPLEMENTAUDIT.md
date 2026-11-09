"""Pure canonical routing receiving. No I/O, target imports, provider or model execution."""

from __future__ import annotations
import hashlib, json, math, re, shlex

PROVIDER = "dg17_loopback"


GOVERNOR_BYTES = 21257


GOVERNOR_SHA = "4c8363c2235ba6c50675c93af7319aeb0caf57f020c4858eba1c28e76de4c6c5"


PREFIX_BYTES = 8000


PREFIX_SHA = "3c89161abdc251c3973122ed1d0e0e52b582e144b8d9f50148246972e2f1d791"


SKILLS = ("implementaudit", "audit-state", "audit-assess", "audit-implement", "audit-andon")


NAME_MAP = {"implementaudit:"+name:name for name in SKILLS}


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


def base_config_document(home, tmp, port):
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


MODEL="dg17-canonical-routing-fixture"
FAMILIES=("canonical",)
RPC_METHODS={"canonical":("initialize","plugin/install","plugin/read","skills/list","hooks/list","thread/start","turn/start")}

INDEX_SHA = '65284f14410d859bdef09e11f1be7c9f1be10d0bb783e853a098f5f95073b347'


CHILD_BYTES = 2039


CHILD_SHA = "6f5d5738b9efd5fa5d4c35868400220458a2f81179d4081fce508ef65c3f72e4"


RESOLVER_BYTES = 5178


RESOLVER_SHA = "97ce587a295cfa0f13276a8dfccf63ca9f679352fdcf0d769a095eab5284b67d"


CLAIMS = ("NINE_OPERATION_SCOPE_RECONCILIATION", "ORIGINAL95_IDENTITY_HISTORY_AND_COUNT_PRESERVATION",
          "HOST_FAMILY_SCOPE_AND_PENDING_CONJUNCTIONS", "NO_PROMOTION_AND_UNKNOWN_BOUNDARY_PRESERVATION")


OPERATION = "ONE_CANONICAL_AUDIT_ASSESS_NATIVE_ROUTE_NONVERDICT"


EXEC_IDS = ("dg17_route_governor", "dg17_route_resolver", "dg17_route_document")


COLLAB_IDS = ("dg17_route_spawn", "dg17_route_wait", "dg17_route_close")


ANNOUNCEMENT = "Loaded the exact audit-assess procedure after the governor and resolver gates. Starting one fresh native child for the bound composition object; the scripted NONVERDICT will leave substantive review pending."


ALLOWED_NOTIFICATIONS = frozenset({"skills/changed", "remoteControl/status/changed", "warning",
    "thread/started", "thread/status/changed", "thread/tokenUsage/updated", "turn/started", "turn/completed",
    "item/started", "item/completed", "item/commandExecution/outputDelta", "item/agentMessage/delta"})


def identifier(value):
    need(type(value) is str and re.fullmatch(r"[A-Za-z0-9_-]{1,128}", value) is not None, "NATIVE_THREAD_ID_SHAPE")
    return value


def string_values(value):
    pending=[value];out=[]
    while pending:
        item=pending.pop()
        if type(item) is str:out.append(item)
        elif type(item) is dict:pending.extend(item.values())
        elif type(item) is list:pending.extend(item)
    return out


def body_absent(value,governor,child):
    return all(governor not in text and child not in text for text in string_values(value))



AUDIT_OBJECT = 'HISTORICAL_COMPOSITION_DRAFT03_WITH_WINDOWS_STAGE_ADDENDUM_01'
SELECTION_PINS = {'REVIEW_PACKET_INDEX.json': {'path': 'REVIEW_PACKET_INDEX.json', 'bytes': 6499, 'sha256': '65284f14410d859bdef09e11f1be7c9f1be10d0bb783e853a098f5f95073b347', 'file_type': 'regular', 'mode_octal': '0644'}, 'SOURCE_BINDING.json': {'path': 'SOURCE_BINDING.json', 'bytes': 34822, 'sha256': '73e8e26cc7411cb84e460cfdbad704087004279d59dd4c168c704027dea48342', 'file_type': 'regular', 'mode_octal': '0644'}, 'PROSPECTIVE_SELECTION.json': {'path': 'PROSPECTIVE_SELECTION.json', 'bytes': 7216, 'sha256': '2c9956d3425884a3eb9e8ae78ee6933c0d16342d44baf39e23aa82ac0b1c792f', 'file_type': 'regular', 'mode_octal': '0644'}, 'OWNER_BINDING.json': {'path': 'OWNER_BINDING.json', 'bytes': 5373, 'sha256': 'dd06fa8a644b61a0f11323beb53a50e988dabddebe89e5a7e9ab17f9e6e45e90', 'file_type': 'regular', 'mode_octal': '0644'}}
DRIVER_APPLICABILITY = {'admission_limit': 'This clarification grants no native route, fresh context or operation admission and establishes no satisfaction, waiver or retirement of the original review obligation; all other owner-binding limits remain applicable.', 'fields_scoped': ['scripted_nonverdict_only', 'substantive_assessment_performed', 'review_obligation_satisfied'], 'interpretation': 'The historical deterministic driver is limited to scripted NONVERDICT and cannot perform substantive assessment or satisfy the substantive review obligation.', 'separately_commissioned_substantive_reviewer': 'This historical driver ceiling does not restrict the separately commissioned substantive reviewer from returning any disposition in allowed_dispositions: PASS, NEEDS_REVISION or NONVERDICT.', 'subject': 'HISTORICAL_DETERMINISTIC_NATIVE_ROUTING_DRIVER_FOR_ORIGINAL14_CURRENT_COMPOSITION_DRAFT03', 'temporal_scope': 'Retained historical driver capability ceiling only; these three fields do not describe or admit any present or future reviewer execution.'}
PACKET02_LINEAGE = {'selection_metadata': {'REVIEW_PACKET_INDEX.json': {'path': 'REVIEW_PACKET_INDEX.json', 'bytes': 6499, 'sha256': '65284f14410d859bdef09e11f1be7c9f1be10d0bb783e853a098f5f95073b347', 'file_type': 'regular', 'mode_octal': '0644'}, 'SOURCE_BINDING.json': {'path': 'SOURCE_BINDING.json', 'bytes': 34822, 'sha256': '73e8e26cc7411cb84e460cfdbad704087004279d59dd4c168c704027dea48342', 'file_type': 'regular', 'mode_octal': '0644'}, 'PROSPECTIVE_SELECTION.json': {'path': 'PROSPECTIVE_SELECTION.json', 'bytes': 7216, 'sha256': '2c9956d3425884a3eb9e8ae78ee6933c0d16342d44baf39e23aa82ac0b1c792f', 'file_type': 'regular', 'mode_octal': '0644'}, 'OWNER_BINDING.json': {'path': 'OWNER_BINDING.json', 'bytes': 5373, 'sha256': 'dd06fa8a644b61a0f11323beb53a50e988dabddebe89e5a7e9ab17f9e6e45e90', 'file_type': 'regular', 'mode_octal': '0644'}}, 'source_data_selection_only': True, 'native_launch_authority': False}

def selection_metadata(raws, index):
    need(type(raws) is dict and set(raws) == set(SELECTION_PINS), "SELECTION_METADATA_POPULATION")
    docs = {}
    for name, pin in SELECTION_PINS.items():
        raw = raws[name]
        need(type(raw) is bytes and len(raw) == pin["bytes"] and sha(raw) == pin["sha256"], "SELECTION_METADATA_PIN")
        docs[name] = parsed(raw)
    received_index = index_document(raws["REVIEW_PACKET_INDEX.json"])
    need(exact(received_index, index), "SELECTION_INDEX_JOIN")
    owner, source, selection = (docs[name] for name in ("OWNER_BINDING.json", "SOURCE_BINDING.json", "PROSPECTIVE_SELECTION.json"))
    need(all(doc.get("audit_object") == AUDIT_OBJECT and doc.get("global_current_acceptance_count") is None
             and doc.get("native_execution") is False and doc.get("new_original_awards") == [] for doc in docs.values()), "SELECTION_SUBJECT_CEILING")
    need(owner["review_packet_member_count"] == source["member_count"] == 20
         and owner["review_packet_total_bytes"] == 1356110
         and owner["read_boundary"] == [row["path"] for row in index["members"]]
         and owner["selection_metadata_boundary"] == ["REVIEW_PACKET_INDEX.json", "SOURCE_BINDING.json", "PROSPECTIVE_SELECTION.json", "OWNER_BINDING.json"], "SELECTION_OWNER_POPULATION")
    for doc in (owner, source, selection):
        need(exact(doc["review_packet_index"], SELECTION_PINS["REVIEW_PACKET_INDEX.json"]), "SELECTION_INDEX_BINDING")
    need(exact(owner["source_binding"], SELECTION_PINS["SOURCE_BINDING.json"])
         and exact(selection["source_binding"], SELECTION_PINS["SOURCE_BINDING.json"])
         and exact(owner["prospective_selection"], SELECTION_PINS["PROSPECTIVE_SELECTION.json"]), "SELECTION_METADATA_JOIN")
    rows = source["members"]
    need(type(rows) is list and len(rows) == 20 and len({r["packet_member"] for r in rows}) == 20, "SELECTION_SOURCE_POPULATION")
    by_path = {r["path"]:r for r in index["members"]}
    roles = {}
    for row in rows:
        need(row["packet_member"] in by_path, "SELECTION_SOURCE_MEMBER")
        expected = by_path[row["packet_member"]]
        need(all(exact(row["exact_source"][key], expected[key]) for key in ("bytes", "sha256", "file_type", "mode_octal")), "SELECTION_SOURCE_BODY_JOIN")
        roles[row["source_role"]] = roles.get(row["source_role"],0)+1
    need(roles == {"original14":14,"reviewed_sidecar":1,"draft02_preservation_predecessor":2,"G03_source_evidence":3}, "SELECTION_SOURCE_ROLES")
    precedence = selection["consumption_precedence"]
    need([r["order"] for r in precedence] == [1,2,3,4]
         and [r["role"] for r in precedence] == ["historical_base","bounded_stage_projection","draft02_preservation_predecessors","G03_source_evidence"], "SELECTION_PRECEDENCE")
    targets = precedence[1]["targets"]
    need([(r["packet_member"],r["json_pointer"],r["selected_projection_member"],r["selected_projection_pointer"]) for r in targets] == [
        ("composition/HOST_MAP.json","/windows_shared_finding","addenda/WINDOWS_STAGE_ADDENDUM.json","/current_stage_projection"),
        ("composition/ORIGINAL95_SOURCE_MAP.json","/check_registry/DG18_WINDOWS_ARTIFACT_RECEIVING","addenda/WINDOWS_STAGE_ADDENDUM.json","/current_stage_projection")], "SELECTION_STAGE_TARGETS")
    need(all(all(exact(row[key],by_path[row["packet_member"]][key]) for key in ("bytes","sha256")) for row in targets)
         and exact(selection["selected_stage_projection"],by_path["addenda/WINDOWS_STAGE_ADDENDUM.json"]), "SELECTION_STAGE_BODY_JOIN")
    need(exact(owner["driver_ceiling"]["applicability"], DRIVER_APPLICABILITY)
         and owner["driver_ceiling"]["scripted_nonverdict_only"] is True
         and owner["driver_ceiling"]["substantive_assessment_performed"] is False
         and owner["driver_ceiling"]["review_obligation_satisfied"] is False, "SELECTION_DRIVER_APPLICABILITY")
    return {"selection_metadata":SELECTION_PINS,"selection_metadata_member_count":4,
            "consumption_precedence":precedence,"driver_applicability":DRIVER_APPLICABILITY,
            "transport_modes":{"origin_modes":"EXACT_RECEIVED_DESCRIPTORS","public_body_and_metadata":"0644","private_body_and_metadata":"0600"},
            "instructions_inside_data":selection["instructions_inside_data"],
            "common_temporal_stage_interpretation":selection["common_temporal_stage_interpretation"],
            "historical_label_preservation":selection["historical_label_preservation"]}


def owner_selection(raw, expected_sha, index):
    index_document(encoded(index))
    need(type(raw) is bytes and 0 < len(raw) <= 4096 and type(expected_sha) is str
         and re.fullmatch(r"[0-9a-f]{64}", expected_sha) and sha(raw) == expected_sha, "OWNER_BINDING_BYTES")
    obj = parsed(raw)
    wanted = {
        "schema":"dg17.codex.routing.owner-binding.v3", "operation":OPERATION,
        "route_owner":"implementaudit", "selected_child":"audit-assess", "review_required":True,
        "claims":list(CLAIMS), "read_boundary":[row["path"] for row in index["members"]],
        "allowed_dispositions":["PASS", "NEEDS_REVISION", "NONVERDICT"],
        "independence":{"fork_context":False, "fresh_native_context_required":True,
            "authoring_notes_allowed":False, "other_composition_review_outputs_allowed":False,
            "prior_component_evidence_as_target_data":True},
        "authority_ceiling":{key:"NONE" for key in ("authority", "currentness", "lifecycle", "mutation", "release", "closure")},
        "driver_ceiling":{"scripted_nonverdict_only":True, "substantive_assessment_performed":False,
            "review_obligation_satisfied":False,"applicability":DRIVER_APPLICABILITY},
        "review_packet_index_sha256":INDEX_SHA, "review_packet_member_count":20,
        "review_packet_total_bytes":1356110, "audit_object":AUDIT_OBJECT,
        "packet02_lineage":PACKET02_LINEAGE,
    }
    need(type(obj) is dict and set(obj) == set(wanted)|{"root_binding_id"}
         and type(obj["root_binding_id"]) is str
         and re.fullmatch(r"[a-z0-9][a-z0-9-]{0,95}", obj["root_binding_id"]) is not None,
         "OWNER_BINDING_CLOSED_SHAPE")
    need(exact({key:obj[key] for key in wanted}, wanted), "OWNER_BINDING_SCOPE")
    return obj


def index_document(raw):
    need(type(raw) is bytes and sha(raw) == INDEX_SHA, "REVIEW_INDEX_PIN")
    obj = parsed(raw)
    need(obj["audit_object"] == AUDIT_OBJECT and obj["member_count"] == 20
         and len(obj["members"]) == 20 and obj["total_bytes"] == 1356110
         and len({row["path"] for row in obj["members"]}) == 20
         and sum(row["bytes"] for row in obj["members"]) == 1356110,
         "REVIEW_INDEX_POPULATION")
    return obj


def context(name, target, child_name, child_target, resolver, cwd, governor, child, index_raw,
            review_root, owner_raw, owner_sha, metadata_raws, metadata_root):
    need(name == "implementaudit:implementaudit" and child_name == "implementaudit:audit-assess", "SELECTED_NATIVE_NAMES")
    target=safe_path(target);child_target=safe_path(child_target);resolver=safe_path(resolver)
    cwd=safe_path(cwd);review_root=safe_path(review_root)
    need(target.endswith("/skills/implementaudit/SKILL.md"), "GOVERNOR_LAYOUT")
    base=target[:-len("skills/implementaudit/SKILL.md")]
    need(child_target == base+"skills/audit-assess/SKILL.md"
         and resolver == base+"skills/implementaudit/scripts/resolve-internal-skill.py", "SELECTED_PHYSICAL_LAYOUT")
    need(type(governor) is bytes and len(governor) == GOVERNOR_BYTES and sha(governor) == GOVERNOR_SHA
         and len(governor[:PREFIX_BYTES]) == PREFIX_BYTES and sha(governor[:PREFIX_BYTES]) == PREFIX_SHA,
         "GOVERNOR_AND_PREFIX_PIN")
    need(type(child) is bytes and len(child) == CHILD_BYTES and sha(child) == CHILD_SHA, "SELECTED_CHILD_PIN")
    index=index_document(index_raw);owner=owner_selection(owner_raw,owner_sha,index)
    selection=selection_metadata(metadata_raws,index);metadata_root=safe_path(metadata_root)
    text=governor.decode("utf-8","strict");child_text=child.decode("utf-8","strict")
    wrapper=lambda n,p,b:"<skill>\n<name>"+n+"</name>\n<path>"+p+"</path>\n"+b+"\n</skill>"
    input_envelope={"schema":"dg17.codex.routing.native-input.v2", "operation":OPERATION,
        "review_packet_root":review_root, "review_packet_index":index,
        "selection_metadata_root":metadata_root,"selection_contract":selection,
        "owner_selection":owner, "owner_selection_sha256":owner_sha,
        "substantive_review":"NOT_PERFORMED_BY_SCRIPTED_DRIVER", "authority_gain":"NONE"}
    envelope="DG17_CANONICAL_ROUTING_INPUT\n"+compact(input_envelope).decode()
    need(body_absent(input_envelope,text,child_text), "DOCUMENT_BODY_IN_INJECTED_PACKET")
    nonverdict=compact({"schema":"dg17.codex.routing.nonverdict.v1",
        "review_packet_index_sha256":INDEX_SHA, "audit_object":AUDIT_OBJECT,
        "claims":[{"claim":claim,"disposition":"NONVERDICT"} for claim in CLAIMS],
        "reason":"DETERMINISTIC_DRIVER_NO_SUBSTANTIVE_ASSESSMENT",
        "substantive_assessment_performed":False, "review_obligation_satisfied":False,
        "authority":"NONE"}).decode()
    commands=["/usr/bin/cat -- '"+target+"'",
        "/usr/bin/python3 -I -B '"+resolver+"' --governor '"+target+"' --child audit-assess",
        "/usr/bin/cat -- '"+child_target+"'"]
    args=[{"cmd":cmd,"workdir":cwd,"shell":"/usr/bin/bash","login":False,"tty":False,
        "yield_time_ms":30000,"max_output_tokens":8192,"sandbox_permissions":"use_default"} for cmd in commands]
    spawn={"items":[{"type":"text","text":envelope},
        {"type":"skill","name":child_name,"path":child_target}],"fork_context":False}
    need(body_absent(spawn,text,child_text), "DOCUMENT_BODY_IN_DELEGATION")
    return {"family":"canonical","name":name,"target":target,"child_name":child_name,
        "child_target":child_target,"resolver":resolver,"cwd":cwd,"governor":text,"child":child_text,
        "fragment":wrapper(name,target,governor[:PREFIX_BYTES].decode("utf-8","strict")),
        "child_fragment":wrapper(child_name,child_target,child_text),
        "envelope":envelope,"spawn_preview":envelope+"\n[skill:$"+child_name+"]("+child_target+")",
        "input_envelope":input_envelope,"nonverdict":nonverdict,
        "announcement":ANNOUNCEMENT,"exec_args":args,"spawn_args":spawn,
        "exec_outputs":[governor,(child_target+"\n").encode(),child],
        "owner_sha256":owner_sha,"parent_thread_id":None,"parent_turn_id":None,"child_thread_id":None,
        "parent_requests":0,"child_requests":0,"received_requests":0,"responses_complete":[],
        "request_order":[],"child_first_return":None,"phase_projections":[],"provider_advertisement":None}


def config_document(home,tmp,port):
    doc,unused=base_config_document(home,tmp,port)
    doc["agents"]={"enabled":True,"max_concurrent_threads_per_session":1,"max_depth":1}
    doc["features"].update({"multi_agent":True,"multi_agent_v2":False})
    doc["model_providers"][PROVIDER]["name"]="DG17 fixed canonical routing fixture"
    lines=[]
    def emit(table,path=()):
        if path:lines.append("["+".".join(path)+"]")
        for key,value in table.items():
            if type(value) is not dict:lines.append(key+" = "+json.dumps(value,ensure_ascii=True))
        lines.append("")
        for key,value in table.items():
            if type(value) is dict:emit(value,path+(key,))
    emit(doc)
    return doc,("\n".join(lines)+"\n").encode()


def turn_request(ctx,thread_id):
    identifier(thread_id)
    need(ctx["parent_thread_id"] == thread_id, "PARENT_THREAD_NOT_BOUND")
    return {"id":7,"method":"turn/start","params":{"threadId":thread_id,
        "input":[{"type":"text","text":ctx["envelope"],"text_elements":[]},
                 {"type":"skill","name":ctx["name"],"path":ctx["target"]}]}}


def bounded_description(value,limit=16384):
    need(type(value) is str and len(value.encode("utf-8","strict")) <= limit, "TOOL_DESCRIPTION_BOUND")


def string_property(value,kind="string"):
    need(type(value) is dict and set(value)=={"type","description"} and value["type"]==kind,
         "COLLAB_PROPERTY_PROFILE")
    bounded_description(value["description"])


def collaboration_advertisement(tools):
    need(type(tools) is list and 1 <= len(tools) <= 128, "TOOL_ADVERTISEMENT_BOUND")
    namespaces=[r for r in tools if type(r) is dict and r.get("type")=="namespace" and r.get("name")=="multi_agent_v1"]
    need(len(namespaces)==1, "EXACT_V1_NAMESPACE_REQUIRED")
    ns=namespaces[0]
    need(set(ns)=={"type","name","description","tools"} and type(ns["tools"]) is list,
         "V1_NAMESPACE_SHAPE")
    bounded_description(ns["description"])
    members=ns["tools"]
    names=("spawn_agent","send_input","resume_agent","wait_agent","close_agent")
    need(len(members)==5 and {r.get("name") for r in members if type(r) is dict}==set(names),
         "V1_EXACT_ADVERTISED_POPULATION")
    for other in tools:
        if other is ns:continue
        need(not(type(other) is dict and (other.get("name") in set(names)|{"multi_agent_v2","list_agents","followup_task","interrupt_agent"})),
             "OTHER_COLLABORATION_PROFILE")
    rows={r["name"]:r for r in members}
    for name,row in rows.items():
        need(set(row)=={"type","name","description","strict","parameters"}
             and row["type"]=="function" and row["strict"] is False,"V1_FUNCTION_PROFILE")
        bounded_description(row["description"],32768)
        params=row["parameters"]
        need(type(params) is dict and params.get("type")=="object" and params.get("additionalProperties") is False
             and type(params.get("properties")) is dict,"V1_PARAMETER_PROFILE")
    spawn=rows["spawn_agent"]["parameters"]
    need(set(spawn)=={"type","properties","additionalProperties"},"SPAWN_PARAMETER_KEYS")
    props=spawn["properties"];base={"message","items","fork_context","model","reasoning_effort"}
    need(set(props) in (base,base|{"agent_type"}),"SPAWN_PROPERTY_POPULATION")
    for key in set(props)-{"items"}:string_property(props[key],"boolean" if key=="fork_context" else "string")
    item=props["items"]
    need(type(item) is dict and set(item)=={"type","description","items"} and item["type"]=="array","SPAWN_ITEMS_PROFILE")
    bounded_description(item["description"]);entry=item["items"]
    need(type(entry) is dict and set(entry)=={"type","properties","additionalProperties"}
         and entry["type"]=="object" and entry["additionalProperties"] is False
         and set(entry["properties"])=={"type","text","image_url","audio_url","path","name"},"SPAWN_ITEM_PROFILE")
    for prop in entry["properties"].values():string_property(prop)
    wait=rows["wait_agent"]["parameters"]
    need(set(wait)=={"type","properties","required","additionalProperties"} and wait["required"]==["targets"]
         and set(wait["properties"])=={"targets","timeout_ms"},"WAIT_PARAMETER_PROFILE")
    targets=wait["properties"]["targets"]
    need(type(targets) is dict and set(targets)=={"type","description","items"}
         and targets["type"]=="array" and targets["items"]=={"type":"string"},"WAIT_TARGETS_PROFILE")
    bounded_description(targets["description"]);string_property(wait["properties"]["timeout_ms"],"number")
    close=rows["close_agent"]["parameters"]
    need(set(close)=={"type","properties","required","additionalProperties"} and close["required"]==["target"]
         and set(close["properties"])=={"target"},"CLOSE_PARAMETER_PROFILE")
    string_property(close["properties"]["target"])
    return {"v1_namespace_exact":True,"advertised_v1_tools":list(names),"namespace_sha256":sha(encoded(ns))}


def expected_calls(ctx,count):
    calls=[{"call_id":call_id,"name":"exec_command","namespace":None,"arguments":args}
           for call_id,args in zip(EXEC_IDS,ctx["exec_args"])]
    calls.append({"call_id":COLLAB_IDS[0],"name":"spawn_agent","namespace":"multi_agent_v1","arguments":ctx["spawn_args"]})
    if count>=5:
        child=identifier(ctx["child_thread_id"])
        calls.append({"call_id":COLLAB_IDS[1],"name":"wait_agent","namespace":"multi_agent_v1",
                      "arguments":{"targets":[child],"timeout_ms":10000}})
    if count>=6:
        calls.append({"call_id":COLLAB_IDS[2],"name":"close_agent","namespace":"multi_agent_v1",
                      "arguments":{"target":identifier(ctx["child_thread_id"])}})
    return calls[:count]


def terminal_output(text,expected):
    need(type(text) is str,"ORDINARY_NATIVE_TOOL_OUTPUT_PROFILE")
    raw=text.encode("utf-8","strict")
    pattern=rb"(?:Chunk ID: [A-Za-z0-9_-]{1,128}\n)?Wall time: [0-9]+(?:\.[0-9]+)? seconds\nProcess exited with code 0\n(?:Original token count: [0-9]+\n)?Output:\n"
    match=re.match(pattern,raw)
    need(match is not None and raw[match.end():]==expected,"FULL_TERMINAL_TOOL_BODY_UNRECEIVED")
    return {"terminal_exit_zero":True,"live_session_returned":False,"output_bytes":len(expected),
        "output_sha256":sha(expected),"tool_output_bytes":len(raw),"tool_output_sha256":sha(raw),"body_offset_utf8":match.end()}


def history_projection(items,ctx,count):
    calls=[r for r in items if type(r) is dict and r.get("type")=="function_call"]
    outputs=[r for r in items if type(r) is dict and r.get("type")=="function_call_output"]
    need(len(calls)==len(outputs)==count,"EXACT_ROUTING_CALL_HISTORY")
    projections=[]
    for ordinal,(call,output,wanted) in enumerate(zip(calls,outputs,expected_calls(ctx,count)),1):
        need(call.get("call_id")==wanted["call_id"] and call.get("name")==wanted["name"]
             and call.get("namespace")==wanted["namespace"] and type(call.get("arguments")) is str
             and exact(parsed(call["arguments"].encode("utf-8")),wanted["arguments"]),"EXACT_ROUTING_CALL_BINDING")
        need(output.get("call_id")==wanted["call_id"] and type(output.get("output")) is str,"EXACT_ROUTING_RETURN_BINDING")
        need(items.index(call)<items.index(output),"NATIVE_RETURN_BEFORE_CALL")
        if ordinal>1:need(items.index(outputs[ordinal-2])<items.index(call),"ROUTING_NATIVE_CALL_REORDER")
        raw=output["output"].encode("utf-8","strict")
        if ordinal<=3:projection=terminal_output(output["output"],ctx["exec_outputs"][ordinal-1])
        else:
            obj=parsed(raw)
            if ordinal==4:
                need(type(obj) is dict and set(obj)=={"agent_id","nickname"}
                     and (obj["nickname"] is None or type(obj["nickname"]) is str and len(obj["nickname"].encode())<=256),"SPAWN_RETURN_PROFILE")
                child=identifier(obj["agent_id"])
                need(child!=ctx["parent_thread_id"] and ctx["child_thread_id"] in (None,child),"SPAWN_CHILD_ID_CONTRADICTION")
                ctx["child_thread_id"]=child
            elif ordinal==5:
                need(exact(obj,{"status":{ctx["child_thread_id"]:{"completed":ctx["nonverdict"]}},"timed_out":False}),
                     "ACTUAL_FIRST_CHILD_RETURN_UNRECEIVED")
                need(ctx["child_requests"]==1 and "C1" in ctx["responses_complete"],"WAIT_RETURN_WITHOUT_COMPLETED_CHILD_DELIVERY")
                need(ctx["child_first_return"] in (None,ctx["nonverdict"]),"FIRST_CHILD_RETURN_CHANGED")
                ctx["child_first_return"]=ctx["nonverdict"]
            else:
                need(ctx["child_first_return"] is not None and exact(obj,{"previous_status":{"completed":ctx["child_first_return"]}}),
                     "NATIVE_CLOSE_PREVIOUS_STATUS_UNRECEIVED")
            projection={"json_return_exact":True,"return_bytes":len(raw),"return_sha256":sha(raw)}
        projections.append({"call_id":wanted["call_id"],**projection})
    return projections


def provider_projection(raw,ctx,ordinal,headers):
    need(type(headers) is dict and type(ordinal) is int and ordinal==ctx["received_requests"]+1 and ordinal<=8,
         "ROUTING_PROVIDER_REQUEST_QUOTA")
    thread=identifier(headers.get("thread-id"));need(headers.get("x-client-request-id")==thread,"HTTP_NATIVE_THREAD_HEADER_JOIN")
    value=parsed(raw)
    need(type(value) is dict and value.get("model")==MODEL and value.get("stream") is True
         and type(value.get("input")) is list and len(value["input"])<=256,"RESPONSES_REQUEST_PROFILE")
    items=value["input"];texts=input_texts(items);user_texts=input_texts(items,"user")
    need(all(type(row) is dict and row.get("type") in (None,"message","function_call","function_call_output")
             and (row.get("type") is not None or row.get("role") in ("system","developer","user","assistant")) for row in items),
         "UNADMITTED_RESPONSES_INPUT_ITEM")
    row={"ordinal":ordinal,"request_bytes":len(raw),"request_sha256":sha(raw),"thread_id_sha256":sha(thread.encode()),
         "request_header_thread_join":True,"native_history_count":0,"native_outputs":[]}
    if thread==ctx["parent_thread_id"]:
        need("x-openai-subagent" not in headers,"PARENT_SUBAGENT_HEADER_UNADMITTED")
        stage=ctx["parent_requests"]+1;need(stage<=7,"PARENT_REQUEST_QUOTA")
        label="P"+str(stage)
        need(stage==1 or "P"+str(stage-1) in ctx["responses_complete"],"PARENT_REQUEST_BEFORE_PRIOR_RESPONSE_COMPLETED")
        need(sum(text.count(ctx["fragment"]) for text in user_texts)==1
             and sum(text.count(ctx["envelope"]) for text in user_texts)==1,"EXACT_GOVERNOR_AND_PACKET_INPUT")
        if stage==1:
            need(ctx["received_requests"]==0 and ctx["child_requests"]==0,"INITIAL_PARENT_ORDER")
            need(not any(type(r) is dict and r.get("type") in ("function_call","function_call_output") for r in items),"INITIAL_TOOL_HISTORY_PRESENT")
            need(all(ctx["governor"] not in text and ctx["child"] not in text for text in texts),"INITIAL_FULL_PROCEDURE_INJECTION")
            ad={**advertisement(value.get("tools")),**collaboration_advertisement(value.get("tools"))}
            ctx["provider_advertisement"]=ad;row["advertisement"]=ad
        else:
            row["native_outputs"]=history_projection(items,ctx,stage-1);row["native_history_count"]=stage-1
            # The input envelope must never be replaced with hidden full-body payloads.
            need(all(ctx["governor"] not in text and ctx["child"] not in text for text in user_texts),"FULL_PROCEDURE_IN_USER_TEXT")
            announcements=[text for text in input_texts(items,"assistant") if text==ANNOUNCEMENT]
            need(len(announcements)==(1 if stage>=5 else 0),"EXACT_POST_LOAD_ANNOUNCEMENT_HISTORY")
        if stage>=6:need(ctx["child_requests"]==1,"MISSING_ACTUAL_CHILD_REQUEST")
        ctx["parent_requests"]=stage;row.update(role="parent",phase=label)
    else:
        need(headers.get("x-openai-subagent")=="collab_spawn" and ctx["parent_requests"] in (4,5)
             and "P4" in ctx["responses_complete"] and ctx["child_requests"]==0,
             "FRESH_CHILD_HEADER_OR_ORDER")
        need(ctx["child_thread_id"] in (None,thread),"CHILD_NATIVE_ID_DIFFERS")
        need(sum(text.count(ctx["child_fragment"]) for text in user_texts)==1
             and sum(text.count(ctx["envelope"]) for text in user_texts)==1,"EXACT_FRESH_CHILD_SKILL_AND_PACKET")
        need(all(ctx["governor"] not in text and ctx["fragment"] not in text for text in texts)
             and not any(type(r) is dict and r.get("type") in ("function_call","function_call_output") for r in items),
             "FRESH_CHILD_PARENT_HISTORY_PRESENT")
        need(not input_texts(items,"assistant"),"FRESH_CHILD_ASSISTANT_HISTORY_PRESENT")
        ctx["child_thread_id"]=thread;ctx["child_requests"]=1;label="C1"
        row.update(role="child",phase=label,full_child_document_bytes=CHILD_BYTES,full_child_document_sha256=CHILD_SHA,
                   fresh_no_parent_history=True)
    ctx["received_requests"]=ordinal;ctx["request_order"].append(label);ctx["phase_projections"].append(row)
    return row


def message_item(item_id,text,phase):
    return {"type":"message","id":item_id,"role":"assistant","status":"completed","phase":phase,
        "content":[{"type":"output_text","text":text,"annotations":[]}]}


def response_bytes(ctx,phase):
    need(phase in ("P1","P2","P3","P4","P5","P6","P7","C1"),"SSE_RESPONSE_PHASE")
    if phase in ("C1","P7"):
        if phase=="P7":need(ctx["child_first_return"]==ctx["nonverdict"],"PARENT_RETURN_BEFORE_CHILD_RESULT")
        items=[message_item("msg_dg17_"+phase,ctx["nonverdict"],"final_answer")]
    else:
        number=int(phase[1:]);call=expected_calls(ctx,number)[number-1]
        item={"type":"function_call","id":"fc_"+phase,"call_id":call["call_id"],"name":call["name"],
            "arguments":compact(call["arguments"]).decode(),"status":"completed"}
        if call["namespace"] is not None:item["namespace"]=call["namespace"]
        items=[item]
        if phase=="P4":items.insert(0,message_item("msg_dg17_announcement",ANNOUNCEMENT,"commentary"))
    need(body_absent(items,ctx["governor"],ctx["child"]),"SCRIPTED_PROCEDURE_BODY_INJECTION")
    rid="resp_dg17_route_"+phase
    events=[{"type":"response.created","response":{"id":rid}}]
    events.extend({"type":"response.output_item.done","output_index":i,"item":item} for i,item in enumerate(items))
    events.append({"type":"response.completed","response":{"id":rid,"status":"completed","output":items,
        "usage":{"input_tokens":0,"output_tokens":0,"total_tokens":0}}})
    raw=b"".join(b"event: "+event["type"].encode()+b"\ndata: "+compact(event)+b"\n\n" for event in events)
    need(len(raw)<=65536,"SSE_RESPONSE_BOUND")
    return raw


def response_complete(ctx,phase):
    need(phase in ctx["request_order"] and phase not in ctx["responses_complete"],"RESPONSE_COMPLETION_REPLAY")
    ctx["responses_complete"].append(phase)


def command_projection(item,ctx):
    need(type(item) is dict and item.get("type")=="commandExecution" and item.get("id") in EXEC_IDS,
         "UNADMITTED_COMMAND_ID")
    index=EXEC_IDS.index(item["id"])
    need(item.get("cwd")==ctx["cwd"] and item.get("status")=="completed"
         and type(item.get("exitCode")) is int and item["exitCode"]==0 and type(item.get("command")) is str,
         "TERMINAL_NATIVE_COMMAND_IDENTITY")
    try:tokens=shlex.split(item["command"],posix=True)
    except ValueError as exc:raise Refusal("NATIVE_COMMAND_DISPLAY_UNRECEIVED") from exc
    need(tokens==["/usr/bin/bash","-c",ctx["exec_args"][index]["cmd"]],"NATIVE_COMMAND_ARGV_DIFFERS")
    aggregate=item.get("aggregatedOutput")
    need(aggregate is None or type(aggregate) is str,"COMMAND_AGGREGATE_TYPE")
    if aggregate is not None:need(aggregate.encode("utf-8")==ctx["exec_outputs"][index],"COMMAND_AGGREGATE_DIFFERS")
    return {"call_id":item["id"],"exit_code":0,"argv_exact":True,"cwd_exact":True,
        "output_bytes":len(ctx["exec_outputs"][index]),"output_sha256":sha(ctx["exec_outputs"][index]),
        "aggregate_present":aggregate is not None}


def collab_projection(item,ctx,complete):
    need(type(item) is dict and set(item)=={"type","id","tool","status","senderThreadId","receiverThreadIds",
        "prompt","model","reasoningEffort","agentsStates"} and item["type"]=="collabAgentToolCall"
        and item["id"] in COLLAB_IDS,"COLLAB_ITEM_CLOSED_PROFILE")
    index=COLLAB_IDS.index(item["id"]);tools=("spawnAgent","wait","closeAgent")
    need(item["tool"]==tools[index] and item["senderThreadId"]==ctx["parent_thread_id"]
         and item["status"]==("completed" if complete else "inProgress"),"COLLAB_ITEM_IDENTITY_OR_STATUS")
    if index==0:
        need(type(item["prompt"]) is str and item["prompt"]==ctx["spawn_preview"],"COLLAB_SPAWN_PROMPT_DIFFERS")
        need(item["model"] in ("",MODEL) and (item["reasoningEffort"] is None or item["reasoningEffort"] in
             ("none","minimal","low","medium","high","xhigh","max")),"COLLAB_INHERITED_MODEL_PROFILE")
    else:
        need(item["prompt"] is None and item["model"] is None and item["reasoningEffort"] is None,"COLLAB_UNADMITTED_OVERRIDE")
    if not complete and index==0:
        need(item["receiverThreadIds"]==[] and item["agentsStates"]=={},"SPAWN_STARTED_CHILD_ALREADY_PRESENT")
    else:
        child=identifier(ctx["child_thread_id"])
        need(item["receiverThreadIds"]==[child],"COLLAB_CHILD_ID_JOIN")
        if complete:
            need(type(item["agentsStates"]) is dict and set(item["agentsStates"])=={child},"COLLAB_AGENT_STATE_POPULATION")
            state=item["agentsStates"][child]
            need(type(state) is dict and set(state)=={"status","message"},"COLLAB_AGENT_STATE_PROFILE")
            if index==0:
                need(state["status"] in ("pendingInit","running","completed") and
                     state["message"] in (None,ctx["nonverdict"]),"SPAWN_INITIAL_STATE_UNRECEIVED")
            else:need(state=={"status":"completed","message":ctx["nonverdict"]},"COLLAB_ACTUAL_RETURN_DIFFERS")
        else:need(item["agentsStates"]=={},"COLLAB_STARTED_STATE_PROFILE")
    return {"call_id":item["id"],"tool":tools[index],"completed":complete,
        "child_id_joined":complete or index!=0,"first_return_exact":complete and index in (1,2)}


def wire_projection(events,expected_sends,ctx=None,thread_id=None,turn_id=None,complete=False):
    need(type(events) is list and len(events)<=1024,"NATIVE_EVENT_BOUND")
    sent=[];responses={};notifications=[];commands=[];collabs=[];messages=[];warnings=[];turns=[];started=[]
    child=None if ctx is None else ctx["child_thread_id"]
    allowed_threads={value for value in (thread_id,child) if value is not None}
    for index,event in enumerate(events):
        need(type(event) is dict and set(event)=={"sequence","direction","value"}
             and type(event["sequence"]) is int and event["sequence"]==index+1,"WIRE_RECORD_SHAPE")
        value=event["value"]
        if event["direction"]=="send":
            need(len(sent)<len(expected_sends) and exact(value,expected_sends[len(sent)]),"NONADMITTED_RPC_SEND")
            sent.append(value);continue
        need(event["direction"]=="receive" and type(value) is dict,"WIRE_DIRECTION")
        if "id" in value:
            need(set(value)=={"id","result"} and type(value["id"]) is int
                 and value["id"] in {row["id"] for row in sent if "id" in row} and value["id"] not in responses,
                 "SERVER_REQUEST_ERROR_OR_UNKNOWN_ID")
            responses[value["id"]]=value["result"];continue
        need(set(value)=={"method","params","emittedAtMs"} and type(value["emittedAtMs"]) is int
             and 0<=value["emittedAtMs"]<=9223372036854775807 and value["method"] in ALLOWED_NOTIFICATIONS
             and type(value["params"]) is dict,"UNKNOWN_NATIVE_NOTIFICATION")
        method=value["method"];params=value["params"];notifications.append(method)
        if method=="skills/changed":need(params=={},"SKILLS_CHANGED_PROFILE");continue
        if method=="remoteControl/status/changed":
            need(params.get("status")=="disabled" and params.get("environmentId") is None,"REMOTE_CONTROL_UNADMITTED");continue
        if method=="thread/started":
            row=params.get("thread");need(type(row) is dict,"STARTED_THREAD_SHAPE")
            if thread_id is not None:need(row.get("id") in allowed_threads,"STARTED_THREAD_ID")
            continue
        need(ctx is not None and params.get("threadId") in allowed_threads,"NATIVE_NOTIFICATION_THREAD_SCOPE")
        owner=params["threadId"]
        if method=="warning":
            need(set(params)=={"threadId","message"} and owner==thread_id and params["message"]==
                 "Skill `"+ctx["name"]+"` exceeded the main prompt context limit and was truncated.","WARNING_NOT_EXACT_SELECTED_TRUNCATION")
            warnings.append(sha(params["message"].encode()));continue
        if method.startswith("item/"):
            if owner==thread_id and turn_id is not None:need(params.get("turnId")==turn_id,"ITEM_TURN_ID")
            else:identifier(params.get("turnId"))
            if method not in ("item/started","item/completed"):
                need(type(params.get("delta")) is str,"DELTA_TYPE")
                if method=="item/commandExecution/outputDelta":need(owner==thread_id and params.get("itemId") in EXEC_IDS,"OUTPUT_DELTA_CALL_ID")
                continue
            item=params.get("item");need(type(item) is dict and item.get("type") in
                 ("userMessage","agentMessage","commandExecution","collabAgentToolCall"),"UNADMITTED_NATIVE_ITEM")
            done=method=="item/completed"
            if done:need(type(params.get("completedAtMs")) is int and 0<=params["completedAtMs"]<=9223372036854775807,"ITEM_COMPLETED_TIMESTAMP")
            if item["type"]=="commandExecution":
                need(owner==thread_id and item.get("id") in EXEC_IDS and item.get("cwd")==ctx["cwd"],"STARTED_COMMAND_BINDING")
                if done:commands.append((index,command_projection(item,ctx)))
                else:started.append((index,item["id"]))
            elif item["type"]=="collabAgentToolCall":
                need(owner==thread_id,"CHILD_COLLABORATION_FORBIDDEN")
                collabs.append((index,collab_projection(item,ctx,done)))
            elif done and item["type"]=="agentMessage":
                need(type(item.get("text")) is str,"AGENT_MESSAGE_TYPE")
                if owner==thread_id:
                    need((item["text"]==ANNOUNCEMENT and item.get("phase")=="commentary")
                         or (item["text"]==ctx["nonverdict"] and item.get("phase")=="final_answer"),"PARENT_AGENT_MESSAGE_UNADMITTED")
                else:need(item["text"]==ctx["nonverdict"] and item.get("phase")=="final_answer","CHILD_FIRST_RETURN_DIFFERS")
                messages.append((index,owner,item["text"]))
        elif method in ("turn/started","turn/completed"):
            turn=params.get("turn");need(type(turn) is dict,"TURN_NOTIFICATION_SHAPE")
            if owner==thread_id and turn_id is not None:need(turn.get("id")==turn_id,"NATIVE_TURN_ID")
            else:identifier(turn.get("id"))
            if method=="turn/completed":
                need(turn.get("status")=="completed" and turn.get("error") is None,"NATIVE_TURN_NOT_SUCCESSFUL")
                turns.append((index,owner,turn.get("id")))
        elif method not in ("thread/status/changed","thread/tokenUsage/updated"):
            raise Refusal("UNHANDLED_NATIVE_NOTIFICATION")
    if complete:
        need(sent==expected_sends and set(responses)=={row["id"] for row in sent if "id" in row},"EXACT_RPC_POPULATION")
        need([row["call_id"] for _,row in commands]==list(EXEC_IDS)
             and [call for _,call in started]==list(EXEC_IDS),"EXACT_NATIVE_EXEC_POPULATION")
        for (si,_),(ci,_) in zip(started,commands):need(si<ci,"COMMAND_COMPLETION_ORDER")
        need([row["call_id"] for _,row in collabs]==[item for call in COLLAB_IDS for item in (call,call)]
             and [row["completed"] for _,row in collabs]==[False,True]*3,"EXACT_COLLABORATION_SEQUENCE")
        parent_messages=[(i,text) for i,owner,text in messages if owner==thread_id]
        child_messages=[text for _,owner,text in messages if owner==child]
        need([text for _,text in parent_messages]==[ANNOUNCEMENT,ctx["nonverdict"]]
             and child_messages in ([],[ctx["nonverdict"]]),"EXACT_NATIVE_RETURN_POPULATION")
        need(commands[0][0]<commands[1][0]<commands[2][0]<parent_messages[0][0]<collabs[0][0]
             and collabs[-1][0]<parent_messages[1][0],"LOAD_ANNOUNCE_DISPATCH_RETURN_ORDER")
        parent_turns=[row for row in turns if row[1]==thread_id];child_turns=[row for row in turns if row[1]==child]
        need(len(parent_turns)==1 and len(child_turns)<=1 and len(warnings)==1,"EXACT_ROUTING_TURN_AND_WARNING_POPULATION")
        need(ctx["parent_requests"]==7 and ctx["child_requests"]==1 and ctx["received_requests"]==8
             and set(ctx["responses_complete"])=={"P1","P2","P3","P4","P5","P6","P7","C1"}
             and ctx["child_first_return"]==ctx["nonverdict"],"COMPLETE_PROVIDER_ROUTE_REQUIRED")
    return {"response_count":len(responses),"notification_count":len(notifications),
        "notification_methods":sorted(set(notifications)),"warning_count":len(warnings),
        "warning_messages_sha256":sha(encoded(warnings)),"native_exec_started_count":len(started),
        "native_exec_completed_count":len(commands),"native_collab_started_count":sum(not r["completed"] for _,r in collabs),
        "native_collab_completed_count":sum(r["completed"] for _,r in collabs),
        "parent_completed_turn_count":sum(owner==thread_id for _,owner,_ in turns),
        "child_completed_turn_notifications":sum(owner==child for _,owner,_ in turns),
        "commands":[r for _,r in commands],"collaboration":[r for _,r in collabs],
        "load_announce_dispatch_return_order_received":complete,"unknown_frames":0,"server_requests":0},responses

