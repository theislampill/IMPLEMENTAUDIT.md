#!/usr/bin/env python3
"""Separately admitted two-family Codex full governor-content observation.

Authoring is inert. This executable is solely for an independently reviewed and
effect/resource-admitted hosted parent. No original or governance award follows.
"""
from __future__ import annotations
import argparse, ctypes, hashlib, importlib.util, io, json, os, re, signal, stat, sys, time, tomllib, zipfile
from pathlib import Path

CONTROL_COMMIT="0d57929be5bd15682b4e9da2c0209d5dff307843"
CONTROL_TREE="ee316c27250ec422d35a1ea965182ebddf7a5da0"
PACKAGE_COMMIT="8ee4ae44d67eb7ac8e8c7d8530c455ae1768605b"
PACKAGE_TREE="0da374609f7fea2463a2926f3603b976620bd10e"
PINS={
 "activation_probe.py":"2e8c14c80867af22240daef0ee9bf2b56bf9293035442e2b6d84ac315d4e481a",
 "catalogue_probe.py":"9456e39cf3be3254b4c25c74716a1b87ba5f2accd6bf196db061e326c7a50277",
 "host_utility.py":"429c6b50cef6ef6352a0c812ce9fcf386cc852156ba54c2d1419088c8f89f85c",
 "owned_resources.py":"0b7d871aca378dc807bc33211d4b84a1b0baa45939c9c24ca54374c23468e33a",
 "namespace_process_custody.py":"6d2e049a8ddbc89e6213c4968d44e6e1483254d852d45480b90f01f960453630",
 "content_protocol.py":"f44976a86ef155d0b2bec26f6d1dd80610abfe010de6fd02da1f5ad3e3e32320",
 "content_transport.py":"00160be92d38b2858860e239155d6e250c987d405793fecd87e35e8619ee9a2d",
 "SOURCE_INPUT_PINS.json":"d5e1e1e9abeeaa79500acc0c41f1555df4a1dc6e5a50259a94db8895500edaad",
}
PACKAGES={
 "canonical":{"archive_bytes":584974,"archive_sha256":"18bb9d7dcb876f7c6be4340bec10dbc77f091227c24504dcecdb0b7d9853f458",
    "matrix_file":"CANONICAL_PACKAGE_MATRIX.json","matrix_sha256":"ef9cbbe7c2c277c434139080d548f0cb868ee091fe79aa96633dcd46cc86a117",
    "files":75,"payload_bytes":2092025},
 "standalone":{"archive_bytes":580372,"archive_sha256":"b6fd05b9f1c0b26fe6a193b47e8f6487f3a161e51824670ca0a520772b307413",
    "matrix_file":"STANDALONE_PACKAGE_MATRIX.json","matrix_sha256":"687367382cf92717c87a5b838aaebf2a39e15e6b98ddf34baa40c0e2ff8d9b6f",
    "files":72,"payload_bytes":2087351},
}
BINARY_BYTES=324012616
BINARY_SHA="57c94ea520df28beb76955316c5c48f672550fe42c6cff7003badb76e1ee10d8"
PRIVATE_FILE_LIMIT=8388608
PRIVATE_TOTAL_LIMIT=33554432
PRIVATE_ENTRY_LIMIT=2048
PUBLIC_LIMIT=32768

class Refusal(RuntimeError):pass

def need(ok,code):
    if not ok:raise Refusal(code)

def sha(raw):return hashlib.sha256(raw).hexdigest()

def encoded(value):return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=True,allow_nan=False)+"\n").encode()

def load_module(root,name,expected,key):
    path=root/name;info=path.lstat()
    need(stat.S_ISREG(info.st_mode) and info.st_nlink==1 and info.st_size<=1048576 and path.resolve(strict=True)==path,"DEPENDENCY_FILE_SHAPE")
    raw=path.read_bytes();need(sha(raw)==expected and key not in sys.modules,"DEPENDENCY_PIN")
    spec=importlib.util.spec_from_file_location(key,path);module=importlib.util.module_from_spec(spec);sys.modules[key]=module
    spec.loader.exec_module(module);return module

def package_matrix(packet,family,a):
    pin=PACKAGES[family];raw,row=a.regular_bytes(packet/pin["matrix_file"],65536)
    need(row["sha256"]==pin["matrix_sha256"],"PACKAGE_MATRIX_PIN");matrix=a.parsed(raw)
    need(type(matrix) is dict and len(matrix)==pin["files"] and sum(r["bytes"] for r in matrix.values())==pin["payload_bytes"],"PACKAGE_MATRIX_POPULATION")
    for path,row in matrix.items():
        need(type(path) is str and not path.startswith("/") and "\\" not in path
             and all(x not in ("",".","..") for x in path.split("/"))
             and type(row) is dict and set(row)=={"bytes","sha256","mode"}
             and type(row["bytes"]) is int and 0<=row["bytes"]<=PRIVATE_FILE_LIMIT
             and row["mode"] in (0o644,0o755) and re.fullmatch("[0-9a-f]{64}",row["sha256"]),"PACKAGE_MATRIX_MEMBER")
    return matrix

def directory_names(matrix):
    return {parent.as_posix() for rel in matrix for parent in Path(rel).parents if parent!=Path(".")}

def package_census(root,matrix,uid,gid,a):
    a.physical_dir(root,uid,gid)
    found={};dirs={};pending=[root];expected_dirs=directory_names(matrix)
    while pending:
        parent=pending.pop();before=parent.lstat()
        with os.scandir(parent) as stream:entries=list(stream)
        need(len(found)+len(dirs)+len(entries)<=len(matrix)+len(expected_dirs),"PACKAGE_CENSUS_BOUND")
        for entry in entries:
            path=parent/entry.name;info=path.lstat();rel=path.relative_to(root).as_posix()
            need(info.st_uid==uid and info.st_gid==gid and not info.st_mode&0o022,"PACKAGE_MEMBER_OWNER")
            if stat.S_ISDIR(info.st_mode):
                need(rel in expected_dirs and path.resolve(strict=True)==path and stat.S_IMODE(info.st_mode) in (0o700,0o755),"PACKAGE_DIRECTORY_SHAPE")
                dirs[rel]=a.identity(info);pending.append(path)
            else:
                need(rel in matrix and stat.S_ISREG(info.st_mode) and stat.S_IMODE(info.st_mode)==matrix[rel]["mode"],"PACKAGE_MEMBER_SHAPE")
                _,row=a.regular_bytes(path,PRIVATE_FILE_LIMIT,uid,matrix[rel]);found[rel]=row
        need(a.identity(parent.lstat())==a.identity(before),"PACKAGE_DIRECTORY_CHANGED")
    need(set(found)==set(matrix) and set(dirs)==expected_dirs,"PACKAGE_EXACT_POPULATION")
    return {"root_identity":a.identity(root.lstat()),"files":found,"directories":dirs,
            "member_count":len(found),"bytes":sum(row["bytes"] for row in found.values())}

def extract_package(archive,target,matrix,family,uid,gid,a):
    pin=PACKAGES[family];raw,row=a.regular_bytes(archive,pin["archive_bytes"],uid)
    need(row["bytes"]==pin["archive_bytes"] and row["sha256"]==pin["archive_sha256"],"RAW_PACKAGE_PIN")
    need(archive.resolve(strict=True)==archive,"RAW_PACKAGE_PATH_ALIAS")
    target.mkdir(mode=0o700)
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        members=z.infolist();need(len(members)==len(matrix) and len({r.filename for r in members})==len(matrix),"ZIP_CLOSED_POPULATION")
        need(z.comment==b"" and z.testzip() is None,"ZIP_CRC_OR_COMMENT")
        for info in members:
            rel=info.filename;need(rel in matrix and not info.is_dir() and not info.flag_bits&1,"ZIP_PATH_OR_TYPE")
            mode=info.external_attr>>16
            need(stat.S_ISREG(mode) and stat.S_IMODE(mode)==matrix[rel]["mode"] and info.file_size==matrix[rel]["bytes"],"ZIP_MODE_OR_SIZE")
            data=z.read(info);need(len(data)==matrix[rel]["bytes"] and sha(data)==matrix[rel]["sha256"],"ZIP_MEMBER_PIN")
            path=target/rel;path.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
            fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,matrix[rel]["mode"])
            with os.fdopen(fd,"wb") as stream:
                stream.write(data);stream.flush();os.fchmod(stream.fileno(),matrix[rel]["mode"]);os.fsync(stream.fileno())
    return row,package_census(target,matrix,uid,gid,a)

def source_inputs(source,pins,uid,a):
    rows={}
    for item in pins["members"]:
        path=source/item["path"];need(path.resolve(strict=True)==path,"SOURCE_INPUT_ALIAS")
        _,row=a.regular_bytes(path,PRIVATE_FILE_LIMIT,uid,item);rows[item["path"]]=row
    return rows

def startup_guard(source,image,neutral,home,uid,gid,a):
    for root in (source,image,neutral):
        for ancestor in (root,*root.parents):
            for name in ("config.toml","hooks.json","managed_config.toml","requirements.toml"):
                need(not os.path.lexists(ancestor/".codex"/name),"PROJECT_STARTUP_LAYER")
    for ancestor in (neutral,*neutral.parents):
        for name in ("AGENTS.md","AGENTS.override.md",".agents/skills"):
            need(not os.path.lexists(ancestor/name),"NEUTRAL_INSTRUCTION_OR_SKILL_LAYER")
    for name in ("config.toml","managed_config.toml","requirements.toml","hooks.json"):
        need(not os.path.lexists(Path("/etc/codex")/name),"SYSTEM_STARTUP_LAYER")
    for name in ("auth.json","auth.json.tmp","managed_config.toml","requirements.toml","hooks.json",".env",
                 "AGENTS.md","AGENTS.override.md",".gitconfig",".config/git/config"):
        need(not os.path.lexists(home/name),"NATIVE_HOME_STARTUP_LAYER")
    for name in ("plugin.json",".mcp.json",".app.json","hooks/hooks.json","commands",".codex-plugin/migrated-command-skills"):
        need(not os.path.lexists(image/name),"PACKAGE_ACTIVE_EXTRAS")
    a.physical_dir(neutral,uid,gid,True)
    with os.scandir(neutral) as stream:need(list(stream)==[],"NEUTRAL_CWD_CHANGED")
    return True

def config_snapshot(home,expected,installed,uid,gid,a):
    raw,row=a.regular_bytes(home/"config.toml",32768,uid)
    need(row["identity"]["gid"]==gid and row["identity"]["mode"] in (0o600,0o644),"CONFIG_OWNER_MODE")
    actual=tomllib.loads(raw.decode("utf-8","strict"));wanted=dict(expected)
    if installed:wanted["plugins"]={"implementaudit@implementaudit":{"enabled":True}}
    need(encoded(actual)==encoded(wanted),"CLOSED_CONFIG_DIFFERS")
    return {"bytes":len(raw),"sha256":sha(raw),"identity":row["identity"],"document":actual}

def helper_snapshot(launch,home,env,uid,gid,h,a):
    need(launch.name=="owned-binary" and launch.resolve(strict=True)==launch
         and not launch.is_relative_to(home/"packages/standalone/releases"),"INSTALL_CONTEXT_NOT_OTHER")
    need(env["PATH"]=="/usr/bin:/bin" and not any(key.startswith(("CODEX_MANAGED_BY_","RUNFILES_")) or key in
         ("CARGO_BIN_EXE_bwrap","TEST_SRCDIR","TEST_WORKSPACE","BASH_ENV","ENV","LD_PRELOAD","LD_LIBRARY_PATH") for key in env),"HELPER_ENVIRONMENT_UNADMITTED")
    tools={name:h.executable_identity(Path("/usr/bin")/name) for name in ("bash","cat","bwrap","true","python3","env")}
    aliases={}
    for name in ("bash","cat","bwrap","true"):
        path=Path("/bin")/name;row=h.executable_identity(path)
        need(row["resolved"]==tools[name]["resolved"]=="/usr/bin/"+name and row["sha256"]==tools[name]["sha256"],"SYSTEM_ALIAS_IDENTITY")
        aliases[name]=row
    absent=[]
    for path in (launch/"codex-resources",launch.parent/"codex-resources",launch/"bwrap",launch/"codex-path"):
        need(not os.path.lexists(path),"BUNDLED_HELPER_CANDIDATE_PRESENT");absent.append(str(path))
    a.physical_dir(launch,uid,gid,True)
    with os.scandir(launch) as stream:entries=list(stream)
    need({entry.name for entry in entries} in ({"codex"},set()),"RUNTIME_DIRECTORY_POPULATION")
    return {"tools":tools,"bin_aliases":aliases,"absent_candidates":absent,
            "install_context":"OTHER_FIXED_OWNED_BINARY_LEAF","managed_bazel_environment_absent":True,
            "native_initial_path":"/usr/bin:/bin","system_capability_fallback":"UNAVAILABLE_WHEN_SYSTEM_REJECTED"}

def alias_snapshot(home,launch,uid,gid,a,live):
    root=home/"tmp/arg0-linux";rows=[]
    if not os.path.lexists(root):
        need(not live,"NATIVE_ARG0_ALIASES_MISSING");return {"live":False,"roots":[],"present_unrequested_aliases":[]}
    a.physical_dir(root,uid,gid,True)
    with os.scandir(root) as stream:entries=list(stream)
    if not live:
        need(entries==[],"NATIVE_ARG0_ALIASES_RETAINED");return {"live":False,"roots":[],"present_unrequested_aliases":[]}
    need(len(entries)==1 and re.fullmatch(r"codex-arg0[A-Za-z0-9_-]+",entries[0].name),"NATIVE_ARG0_ROOT_POPULATION")
    directory=root/entries[0].name;a.physical_dir(directory,uid,gid,True)
    with os.scandir(directory) as stream:members=list(stream)
    need({entry.name for entry in members}=={".lock","apply_patch","applypatch","codex-linux-sandbox"},"NATIVE_ARG0_HELPER_POPULATION")
    for entry in members:
        path=directory/entry.name;info=path.lstat()
        need(info.st_uid==uid and info.st_gid==gid,"NATIVE_ARG0_OWNER")
        if entry.name==".lock":
            need(stat.S_ISREG(info.st_mode) and info.st_nlink==1 and info.st_size==0 and not info.st_mode&0o022,"NATIVE_ARG0_LOCK")
            row={"name":entry.name,"kind":"REGULAR","identity":a.identity(info)}
        else:
            need(stat.S_ISLNK(info.st_mode) and os.readlink(path)==str(launch/"codex")
                 and path.resolve(strict=True)==launch/"codex","NATIVE_ARG0_TARGET")
            row={"name":entry.name,"kind":"SAME_RUNTIME_SYMLINK","identity":a.identity(info),"target":os.readlink(path)}
        rows.append(row)
    need(not os.path.lexists(directory/"bwrap"),"ARG0_BWRAP_FALLBACK")
    return {"live":True,"roots":[{"path":str(directory),"identity":a.identity(directory.lstat()),"members":sorted(rows,key=lambda r:r["name"])}],
            "present_unrequested_aliases":["apply_patch","applypatch"]}

def metadata_rows(private,cases,uid,gid,a):
    owners=[("evidence",private,())]
    for family,case in cases.items():
        if case.get("home") is not None:
            owners.append((family+"-home",case["home"],(case["effective"],) if case.get("effective") is not None else ()))
            owners.append((family+"-tmp",case["tmp"],()))
    rows=[];total=0
    for owner,root,exclusions in owners:
        a.physical_dir(root,uid,gid,True);pending=[root]
        while pending:
            parent=pending.pop();before=parent.lstat()
            with os.scandir(parent) as stream:entries=list(stream)
            for entry in entries:
                path=parent/entry.name
                if path in exclusions or path==private/"PRIVATE_EVIDENCE_SEAL.json":continue
                info=path.lstat();name=owner+"/"+path.relative_to(root).as_posix()
                need(info.st_uid==uid and info.st_gid==gid and not info.st_mode&0o022,"PRIVATE_MEMBER_OWNER")
                if stat.S_ISDIR(info.st_mode):
                    need(path.resolve(strict=True)==path,"PRIVATE_DIRECTORY_ALIAS")
                    rows.append({"path":name,"kind":"DIRECTORY"});pending.append(path)
                else:
                    need(stat.S_ISREG(info.st_mode),"PRIVATE_NONREGULAR_MEMBER")
                    _,observed=a.regular_bytes(path,PRIVATE_FILE_LIMIT,uid)
                    total+=observed["bytes"];need(total<=PRIVATE_TOTAL_LIMIT,"PRIVATE_AGGREGATE_BOUND")
                    rows.append({"path":name,"kind":"REGULAR","bytes":observed["bytes"],"sha256":observed["sha256"]})
                need(len(rows)<=PRIVATE_ENTRY_LIMIT,"PRIVATE_POPULATION_BOUND")
            need(a.identity(parent.lstat())==a.identity(before),"PRIVATE_DIRECTORY_CHANGED")
    return sorted(rows,key=lambda row:row["path"])

def payload_owners(root,cases,uid,gid,a):
    a.physical_dir(root,uid,gid,True)
    with os.scandir(root) as stream:entries=list(stream)
    need({entry.name for entry in entries}==set(cases),"PAYLOAD_CASE_POPULATION")
    rows=[]
    for family,case in cases.items():
        case_root=root/family;a.physical_dir(case_root,uid,gid,True)
        with os.scandir(case_root) as stream:children=list(stream)
        wanted={"home","neutral","tmp"}|({"source-package"} if family=="canonical" else set())
        need({entry.name for entry in children}==wanted,"PAYLOAD_ROOT_POPULATION")
        rows.append({"family":family,"identity":{key:value for key,value in a.identity(case_root.lstat()).items()
                    if key in ("device","inode","mode","uid","gid")},"children":sorted(wanted)})
    return rows

def runtime_owner_rows(root,uid,gid,a):
    a.physical_dir(root,uid,gid,True);rows=[];pending=[root]
    while pending:
        parent=pending.pop();before=parent.lstat()
        with os.scandir(parent) as stream:entries=list(stream)
        for entry in entries:
            path=parent/entry.name;info=path.lstat();rel=path.relative_to(root).as_posix()
            need(info.st_uid==uid and info.st_gid==gid and not info.st_mode&0o022,"RUNTIME_OWNER_IDENTITY")
            if stat.S_ISDIR(info.st_mode):
                need(path.resolve(strict=True)==path and rel in {"canonical","standalone","canonical/owned-binary","standalone/owned-binary"},"RUNTIME_DIRECTORY_UNADMITTED")
                pending.append(path);rows.append({"path":rel,"kind":"DIRECTORY","identity":a.identity(info)})
            else:
                need(rel in ("canonical/owned-binary/codex","standalone/owned-binary/codex"),"RUNTIME_UNADMITTED_FILE")
                _,row=a.regular_bytes(path,BINARY_BYTES,uid,{"bytes":BINARY_BYTES,"sha256":BINARY_SHA})
                rows.append({"path":rel,"kind":"REGULAR",**row})
        need(a.identity(parent.lstat())==a.identity(before),"RUNTIME_DIRECTORY_CHANGED")
    return sorted(rows,key=lambda row:row["path"])

def failure_row(exc,phase):
    code=str(exc)
    if not re.fullmatch(r"[A-Z][A-Z0-9_]{0,95}",code):code="OS_OR_INSTRUMENT_REFUSAL"
    return {"phase":phase,"code":code,"exception_type":type(exc).__name__ if type(exc).__name__ in
             ("Refusal","OSError","TimeoutError","ValueError","PermissionError","FileNotFoundError","CustodyError") else "OtherError"}

def package_public(family,snapshot):
    return {"family":family,"files":snapshot["member_count"],"bytes":snapshot["bytes"],
            "matrix_sha256":PACKAGES[family]["matrix_sha256"],"complete_matrix_matches":True}

def capture_public(record):
    if record is None:return None
    row=dict(record)
    row["cleanup"]={key:record["cleanup"][key] for key in
        ("echild","pidfd_signals","retained_status_count","retained_statuses_sha256","reaped_statuses","reaped_statuses_truncated")}
    return row

def receive_progress(case):
    out=case["public"];native=case.get("native");provider=case.get("provider")
    if native is not None:
        rpc=[row for row in native.send_records if row["id"] is not None]
        out["rpc_methods"]=[row["method"] for row in rpc]
        out["rpc_frames_attempted"]=len(rpc);out["rpc_frames_complete"]=sum(row["complete"] for row in rpc)
        for label,method in (("native_builtin_started_count","item/started"),("native_builtin_completed_count","item/completed")):
            out[label]=sum(event["direction"]=="receive" and event["value"].get("method")==method
                and type(event["value"].get("params")) is dict and type(event["value"]["params"].get("item")) is dict
                and event["value"]["params"]["item"].get("type")=="commandExecution" for event in native.events)
    if provider is not None:
        rows=provider.rows
        first=rows[0] if rows else None
        out["builtin_read_response_started"]=first is not None and first["response_sent_bytes"]>0
        out["builtin_read_response_complete"]=first is not None and first["response_prepared_bytes"]>0 and first["complete"]
        out["builtin_reads"]=int(out["builtin_read_response_started"])
        out["provider"]={"accepted_sockets":provider.accepted,"semantic_requests":sum(row["projection"] is not None for row in rows),
            "listener_closed":provider.closed,"thread_joined":provider.joined,
            "responses_fully_sent":len(rows)==2 and all(row["complete"] and row["response_sent_bytes"]==row["response_prepared_bytes"] for row in rows)}
        for row in rows:
            if row["projection"] is not None:out["typed_request" if row["ordinal"]==1 else "full_body_request"]=row["projection"]

def selected_skills(response,family,cwd,effective,matrix,p,a):
    need(type(response) is dict and set(response)=={"data"} and type(response["data"]) is list and len(response["data"])==1,"SKILLS_RESPONSE_SHAPE")
    data=response["data"][0]
    need(type(data) is dict and set(data)=={"cwd","skills","errors"} and data["cwd"]==str(cwd)
         and type(data["skills"]) is list and len(data["skills"])<=128 and data["errors"]==[],"SKILLS_RESPONSE_SCOPE")
    rows=[];other=[]
    for row in data["skills"]:
        need(type(row) is dict and type(row.get("name")) is str and type(row.get("path")) is str,"SKILL_ROW_TYPE")
        logical=p.NAME_MAP.get(row["name"]) if family=="canonical" else "implementaudit" if row["name"]=="implementaudit" else None
        if logical is None:
            need(row.get("pluginId")!="implementaudit@implementaudit" and not Path(row["path"]).is_relative_to(effective),"UNADMITTED_CANDIDATE_SKILL")
            other.append(row);continue
        rel="skills/"+logical+"/SKILL.md" if family=="canonical" else "SKILL.md"
        need(row["path"]==str(effective/rel) and row.get("enabled") is True,"SELECTED_SKILL_PATH_OR_ENABLED")
        if family=="canonical":need(row.get("pluginId")=="implementaudit@implementaudit","SELECTED_PLUGIN_ATTRIBUTION")
        else:need(row.get("pluginId") is None,"STANDALONE_PLUGIN_ATTRIBUTION")
        rows.append({"name":row["name"],"logical_name":logical,"relative_path":rel,"sha256":matrix[rel]["sha256"],"enabled":True})
    wanted=set(p.SKILLS) if family=="canonical" else {"implementaudit"}
    need(len(rows)==len(wanted) and {r["logical_name"] for r in rows}==wanted,"EXACT_SELECTED_SKILL_POPULATION")
    main=next(row for row in rows if row["logical_name"]=="implementaudit")
    return {"selected_entries":sorted(rows,key=lambda r:r["name"]),"selected_count":len(rows),"other_entry_count":len(other),
            "other_entries_sha256":p.sha(p.encoded(other)),"selected_enabled":True},main["name"],str(effective/main["relative_path"])

def run(args):
    result={"schema":"dg17.codex.package-content.v1","status":"NOT_EXECUTED",
        "control_source_commit":CONTROL_COMMIT,"control_source_tree":CONTROL_TREE,
        "package_source_commit":PACKAGE_COMMIT,"package_source_tree":PACKAGE_TREE,
        "runtime_release_declared":"0.167.0-alpha.4","runtime_bytes":BINARY_BYTES,"runtime_sha256":BINARY_SHA,
        "parent_full_source_admission_required":True,"source_before":False,"source_after":False,"runtime_before":False,"runtime_after":False,
        "currentness_before":False,"currentness_after":False,"currentness_receipt_sha256":None,"git_unchanged":False,
        "offline":None,"cases":[],"planned_families":["canonical","standalone"],"unstarted_families":["canonical","standalone"],
        "requested_rpc_count":0,"requested_builtin_reads":0,"native_internal_helper_count":"UNESTABLISHED",
        "cleanup":{"all_native_closed":False,"all_provider_closed":False,"global_echild_after_close":False,"global_echild_after_seal":False,
                   "runtime_copy_files_retained":None,"runtime_owner_sha256":None,"private_seal_sha256":None,"private_seal_unchanged":False,
                   "private_plaintext_policy":"RETAIN_UNTIL_HOST_TEARDOWN","host_teardown_observed":False},
        "failure":None,"supplemental_failures":[],"additional_failure_count":0,"independent_receiving":"NOT_PERFORMED",
        "model_inference_proven":False,"governed_child_routing_proven":False,"internal_procedure_loading_proven":False,
        "persistent_real_home_installation_proven":False,"original_acceptance_awarded":False}
    a=p=t=h=u=None;modules={};private=payloads=runtime_root=result_path=None;cases={};records=[];safe=False
    deadline=time.monotonic()+240;phase="PRECONDITIONS";source_before=store_before=runtime_before=git_before=None
    source=episode=binary=gate_home=None;source_pins=None
    def fail(exc,where):
        nonlocal safe
        safe=False;row=failure_row(exc,where)
        if result["failure"] is None:result["failure"]=row
        elif len(result["supplemental_failures"])<8:result["supplemental_failures"].append(row)
        else:result["additional_failure_count"]+=1
    def core_bookend():
        need(source_inputs(source,source_pins,args.expected_uid,a)==source_before,"SOURCE_INPUT_CHANGED")
        need(h.source_store_guard(source)==store_before,"SOURCE_STORE_CHANGED")
        need(a.runtime_guard(binary,args.expected_uid)==runtime_before,"RUNTIME_INPUT_CHANGED")
        need(h.offline_guard(args)==result["offline"],"OFFLINE_ENVELOPE_CHANGED")
        a.git_metadata_equal(h,gate_home,source,git_before)
        return True
    def case_bookend(family,case):
        matrix=case["matrix"]
        native=case["native"]
        if native.launch_removed:
            need(not os.path.lexists(native.launch_dir/"codex"),"DELETED_RUNTIME_COPY_REAPPEARED")
        else:
            need(a.runtime_guard(native.launch_dir/"codex",args.expected_uid)==native.copy_identity,"NATIVE_RUNTIME_COPY_CHANGED")
        _,archive_now=a.regular_bytes(case["archive"],PACKAGES[family]["archive_bytes"],args.expected_uid,
                    {"bytes":PACKAGES[family]["archive_bytes"],"sha256":PACKAGES[family]["archive_sha256"]})
        need(archive_now==case["archive_before"],"RAW_PACKAGE_INPUT_CHANGED")
        startup_guard(source,case["image"],case["cwd"],case["home"],args.expected_uid,args.expected_gid,a)
        need(package_census(case["image"],matrix,args.expected_uid,args.expected_gid,a)==case["image_before"],"PACKAGE_INPUT_CHANGED")
        if case.get("effective_before") is not None:
            need(package_census(case["effective"],matrix,args.expected_uid,args.expected_gid,a)==case["effective_before"],"EFFECTIVE_PACKAGE_CHANGED")
        need(config_snapshot(case["home"],case["config_expected"],family=="canonical" and case.get("installed",False),args.expected_uid,args.expected_gid,a)==case["config_before"],"NATIVE_CONFIG_CHANGED")
        need(helper_snapshot(case["native"].launch_dir,case["home"],case["native"].environment,args.expected_uid,args.expected_gid,h,a)==case["helpers_before"],"HELPER_ADMISSION_CHANGED")
        return True
    try:
        packet=Path(__file__).resolve(strict=True).parent
        a=load_module(packet,"activation_probe.py",PINS["activation_probe.py"],"dg17_content_base")
        p=load_module(packet,"content_protocol.py",PINS["content_protocol.py"],"dg17_content_protocol")
        t=load_module(packet,"content_transport.py",PINS["content_transport.py"],"dg17_content_transport")
        h=load_module(packet,"catalogue_probe.py",PINS["catalogue_probe.py"],"dg17_content_admission")
        u=load_module(packet,"host_utility.py",PINS["host_utility.py"],"dg17_content_utility")
        modules={"base":a,"admission":h,"utility":u}
        for name in ("owned_resources","namespace_process_custody"):
            modules[name]=load_module(packet,name+".py",PINS[name+".py"],"dg17_content_"+name)
        result["offline"]=h.offline_guard(args)
        need(re.fullmatch(r"[a-z0-9][a-z0-9-]{0,95}",args.controller) and re.fullmatch(r"refs/implementaudit/continuity-receipts/"+re.escape(args.controller)+r"/G[0-9]{4}@[0-9a-f]{40}",args.receipt),"CURRENTNESS_ARGUMENT_SHAPE")
        source=Path(args.source);episode=Path(args.episode);binary=Path(args.binary);gate_home=episode/"home"
        for directory in (episode,episode/"private",gate_home):a.physical_dir(directory,args.expected_uid,args.expected_gid,True)
        a.physical_dir(source,args.expected_uid,args.expected_gid)
        need(not source.is_relative_to(episode) and not episode.is_relative_to(source),"SOURCE_EPISODE_OVERLAP")
        private=episode/"private/package-content";payloads=episode/"package-content-payloads";runtime_root=episode/"package-content-runtime";result_path=episode/"private/CONTENT_RESULT.json"
        need(not any(os.path.lexists(path) for path in (private,payloads,runtime_root,result_path)),"CONTENT_EPISODE_NOT_FRESH")
        for path in (private,payloads,runtime_root):path.mkdir(mode=0o700)
        raw,pinrow=a.regular_bytes(packet/"SOURCE_INPUT_PINS.json",32768)
        need(pinrow["sha256"]==PINS["SOURCE_INPUT_PINS.json"],"SOURCE_PINS_DIGEST");source_pins=a.parsed(raw)
        source_before=source_inputs(source,source_pins,args.expected_uid,a);store_before=h.source_store_guard(source)
        runtime_before=a.runtime_guard(binary,args.expected_uid);result["source_before"]=True;result["runtime_before"]=True
        a.write_new(private/"SOURCE_BEFORE.json",{"inputs":source_before,"store":store_before})
        a.write_new(private/"RUNTIME_BEFORE.json",runtime_before)
        libc=ctypes.CDLL(None,use_errno=True);need(libc.prctl(36,1,0,0,0)==0,"SUBREAPER_UNAVAILABLE")
        a.quiescent(u)
        phase="INITIAL_GIT_ADMISSION";git_before,unused=h.git_startup_guard(gate_home,True,source)
        a.write_new(private/"GIT_BEFORE.json",git_before)
        core_bookend();a.quiescent(u)
        phase="CURRENTNESS_BEFORE";result["currentness_receipt_sha256"]=a.currentness_capture(args,source,gate_home,private,u,records,deadline,"gate-before")
        result["currentness_before"]=True;safe=True
        for family in p.FAMILIES:
            need(safe and time.monotonic()<deadline,"NEXT_CASE_NOT_ADMITTED");core_bookend();a.quiescent(u)
            phase=family.upper()+"_PREPARE";case={"family":family,"native":None,"provider":None};cases[family]=case
            out={"family":family,"status":"FAILED_OR_PARTIAL","archive_bytes":PACKAGES[family]["archive_bytes"],
                 "archive_sha256":PACKAGES[family]["archive_sha256"],"matrix_sha256":PACKAGES[family]["matrix_sha256"],
                 "native_started":False,"runtime_reported_version_matches":False,"rpc_methods":[],"rpc_frames_attempted":0,"rpc_frames_complete":0,"builtin_reads":0,
                 "builtin_read_response_started":False,"builtin_read_response_complete":False,"native_builtin_started_count":0,"native_builtin_completed_count":0,
                 "package_before":None,"package_after":None,"package_unchanged":False,"helper_bookends_unchanged":False,
                 "arg0_aliases_exact":False,"arg0_aliases_closed":False,"config_unchanged":False,
                 "catalog":None,"skills":None,"hooks":None,"typed_request":None,"full_body_request":None,"native_protocol":None,
                 "provider":None,"capture":None,"runtime_scope":None,"failure":None}
            result["cases"].append(out);case["public"]=out
            case_root=payloads/family;case_root.mkdir(mode=0o700);evidence=private/family;evidence.mkdir(mode=0o700)
            rt=runtime_root/family;rt.mkdir(mode=0o700)
            home=case_root/"home";cwd=case_root/"neutral";tmp=case_root/"tmp"
            for path in (home,cwd,tmp):path.mkdir(mode=0o700)
            case.update(home=home,cwd=cwd,tmp=tmp,evidence=evidence)
            matrix=package_matrix(packet,family,a);case["matrix"]=matrix
            image=case_root/"source-package" if family=="canonical" else home/"skills/implementaudit"
            image.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
            archive=Path(args.canonical_archive if family=="canonical" else args.standalone_archive)
            archive_row,image_before=extract_package(archive,image,matrix,family,args.expected_uid,args.expected_gid,a)
            effective=home/"plugins/cache/implementaudit/implementaudit/0.4.0" if family=="canonical" else image
            case.update(image=image,image_before=image_before,effective=effective,effective_before=None,archive=archive,archive_before=archive_row)
            a.write_new(evidence/"PACKAGE_BEFORE.json",{"archive":archive_row,"image":image_before})
            out["package_before"]=package_public(family,image_before)
            startup_guard(source,image,cwd,home,args.expected_uid,args.expected_gid,a)
            case_deadline=min(deadline,time.monotonic()+90)
            provider=t.LocalResponses(evidence/"http",p,case_deadline);case["provider"]=provider
            native=t.NativeSession(evidence/"native",rt,binary,home,cwd,tmp,modules,p,case_deadline);case["native"]=native
            native.prepare_copy();helpers=helper_snapshot(native.launch_dir,home,native.environment,args.expected_uid,args.expected_gid,h,a)
            case["helpers_before"]=helpers;a.write_new(evidence/"HELPERS_BEFORE_NATIVE.json",helpers)
            core_bookend();a.quiescent(u)
            port=provider.start();expected_config,config_raw=p.config_document(str(home),str(tmp),port)
            t.write_bytes(home/"config.toml",config_raw);case["config_expected"]=expected_config
            case["config_before"]=config_snapshot(home,expected_config,False,args.expected_uid,args.expected_gid,a)
            a.write_new(evidence/"CONFIG_BEFORE_NATIVE.json",case["config_before"])
            case_bookend(family,case);core_bookend();a.quiescent(u)
            phase=family.upper()+"_NATIVE";native.start();out["native_started"]=True;result["unstarted_families"].remove(family)
            sends=p.initial_requests(family,str(image),str(cwd));responses={}
            for request in sends:
                response=native.request(request,provider)
                if "id" not in request:continue
                responses[request["method"]]=response;out["rpc_methods"].append(request["method"]);result["requested_rpc_count"]+=1
                if request["method"]=="initialize":
                    a.initialize_projection(response,home);out["runtime_reported_version_matches"]=True
                    aliases=alias_snapshot(home,native.launch_dir,args.expected_uid,args.expected_gid,a,True)
                    a.write_new(evidence/"ALIASES_AFTER_INITIALIZE.json",aliases)
                    observed=helper_snapshot(native.launch_dir,home,native.environment,args.expected_uid,args.expected_gid,h,a)
                    need(observed==helpers,"HELPERS_CHANGED_AT_INITIALIZE");a.write_new(evidence/"HELPERS_AFTER_INITIALIZE.json",observed)
                elif request["method"]=="plugin/install":
                    a.install_projection(response);case["installed"]=True
                    case["config_before"]=config_snapshot(home,expected_config,True,args.expected_uid,args.expected_gid,a)
                    a.write_new(evidence/"CONFIG_AFTER_INSTALL.json",case["config_before"])
                elif request["method"]=="plugin/read":out["catalog"]=a.catalog_projection(response,image,matrix)
                elif request["method"]=="hooks/list":out["hooks"]=a.hooks_projection(response,cwd)
            effective_before=package_census(effective,matrix,args.expected_uid,args.expected_gid,a);case["effective_before"]=effective_before
            a.write_new(evidence/"EFFECTIVE_BEFORE_TURN.json",effective_before)
            projection,name,target=selected_skills(responses["skills/list"],family,cwd,effective,matrix,p,a);out["skills"]=projection
            governor,unused=a.regular_bytes(Path(target),21257,args.expected_uid)
            ctx=p.context(family,name,target,str(cwd),governor);case["ctx"]=ctx
            provider.set_context(ctx)
            aliases2=alias_snapshot(home,native.launch_dir,args.expected_uid,args.expected_gid,a,True)
            need(aliases2==aliases,"NATIVE_ARG0_ALIAS_CHANGED")
            out["arg0_aliases_exact"]=True;a.write_new(evidence/"ALIASES_BEFORE_TURN.json",aliases2)
            case_bookend(family,case);core_bookend();a.write_new(evidence/"HELPERS_BEFORE_TURN.json",helpers)
            # Native parent is intentionally live here; global ECHILD is required between sessions, not during a live RPC.
            request=p.thread_request(family,str(cwd));sends.append(request);response=native.request(request,provider)
            out["rpc_methods"].append(request["method"]);result["requested_rpc_count"]+=1
            need(type(response) is dict and response.get("model")==p.MODEL and response.get("modelProvider")==p.PROVIDER
                 and response.get("cwd")==str(cwd) and response.get("approvalPolicy")=="never"
                 and response.get("approvalsReviewer")=="user" and (p.exact(response.get("sandbox"),{"type":"readOnly","networkAccess":False})
                     or p.exact(response.get("sandbox"),{"type":"readOnly"}))
                 and response.get("instructionSources",[])==[] and response.get("disabledPluginIds",[])==[]
                 and type(response.get("thread")) is dict and response["thread"].get("ephemeral") is True
                 and response["thread"].get("cwd")==str(cwd) and response["thread"].get("modelProvider")==p.PROVIDER
                 and response["thread"].get("turns")==[] and response["thread"].get("parentThreadId") is None,
                 "THREAD_START_PROFILE")
            thread_id=response["thread"].get("id")
            request=p.turn_request(ctx,thread_id);sends.append(request);response=native.request(request,provider)
            out["rpc_methods"].append(request["method"]);result["requested_rpc_count"]+=1
            need(type(response) is dict and type(response.get("turn")) is dict and type(response["turn"].get("id")) is str,"TURN_START_PROFILE")
            turn_id=response["turn"]["id"];native.wait_turn(thread_id,turn_id,provider)
            provider.check();provider.close();provider_record=provider.record()
            need(provider_record["accepted_socket_count"]==provider_record["semantic_request_count"]==2
                 and all(row["complete"] and row["response_sent_bytes"]==row["response_prepared_bytes"] for row in provider.rows),"PROVIDER_EXACT_COMPLETION")
            a.write_new(evidence/"PROVIDER.json",provider_record)
            out["typed_request"]=provider.rows[0]["projection"];out["full_body_request"]=provider.rows[1]["projection"]
            out["builtin_reads"]=1;result["requested_builtin_reads"]+=1
            out["provider"]={"accepted_sockets":2,"semantic_requests":2,"listener_closed":True,"thread_joined":True,"responses_fully_sent":True}
            phase=family.upper()+"_CLOSE";out["capture"]=capture_public(native.close());out["runtime_scope"]=native.readback
            a.quiescent(u)
            out["native_protocol"],unused=p.wire_projection(native.events,sends,ctx,thread_id,turn_id,True)
            phase=family.upper()+"_BOOKENDS";core_bookend();case_bookend(family,case)
            aliases_closed=alias_snapshot(home,native.launch_dir,args.expected_uid,args.expected_gid,a,False)
            a.write_new(evidence/"ALIASES_AFTER_CLOSE.json",aliases_closed);out["arg0_aliases_closed"]=True
            helpers_after=helper_snapshot(native.launch_dir,home,native.environment,args.expected_uid,args.expected_gid,h,a)
            need(helpers_after==helpers,"HELPERS_CHANGED_AFTER_CLOSE");a.write_new(evidence/"HELPERS_AFTER_CLOSE.json",helpers_after)
            package_after=package_census(effective,matrix,args.expected_uid,args.expected_gid,a)
            a.write_new(evidence/"PACKAGE_AFTER_CLOSE.json",{"archive":archive_row,"image":package_census(image,matrix,args.expected_uid,args.expected_gid,a),"effective":package_after})
            a.write_new(evidence/"CONFIG_AFTER_CLOSE.json",config_snapshot(home,expected_config,family=="canonical",args.expected_uid,args.expected_gid,a))
            out.update(package_after=package_public(family,package_after),package_unchanged=True,helper_bookends_unchanged=True,config_unchanged=True,status="FULL_GOVERNOR_NATIVE_RETURN_OBSERVED")
            receive_progress(case)
            need(out["rpc_frames_attempted"]==out["rpc_frames_complete"]==len(p.RPC_METHODS[family])
                 and out["native_builtin_started_count"]==out["native_builtin_completed_count"]==1
                 and out["builtin_read_response_complete"],"EXACT_NATIVE_REQUEST_AND_TOOL_POPULATION")
            a.write_new(evidence/"CASE_RESULT.json",out)
    except BaseException as exc:
        fail(exc,phase)
        if cases:
            last=next(reversed(cases.values()));last.get("public",{})["failure"]=failure_row(exc,phase)
            last.get("public",{})["status"]="FAILED_OR_PARTIAL"
    finally:
        if a is not None and private is not None and private.exists():
            for family,case in cases.items():
                provider=case.get("provider");native=case.get("native");out=case.get("public",{})
                if provider is not None:
                    try:provider.close()
                    except BaseException as exc:fail(exc,family.upper()+"_PROVIDER_CLEANUP")
                    try:
                        path=case["evidence"]/"PROVIDER.json"
                        if not path.exists():a.write_new(path,provider.record())
                    except BaseException as exc:fail(exc,"PROVIDER_RETENTION")
                if native is not None:
                    try:
                        if not native.closed:native.close()
                    except BaseException as exc:fail(exc,family.upper()+"_NATIVE_CLEANUP")
                    out["capture"]=capture_public(native.capture);out["runtime_scope"]=native.readback
                receive_progress(case)
                try:
                    path=case["evidence"]/"CASE_RESULT.json"
                    if not path.exists():a.write_new(path,out)
                except BaseException as exc:fail(exc,"CASE_RETENTION")
            result["requested_rpc_count"]=sum(case["public"]["rpc_frames_attempted"] for case in cases.values())
            result["requested_builtin_reads"]=sum(case["public"]["builtin_reads"] for case in cases.values())
            try:a.quiescent(u);result["cleanup"]["global_echild_after_close"]=True
            except BaseException as exc:fail(exc,"GLOBAL_AFTER_CLOSE")
            result["cleanup"]["all_native_closed"]=len(cases)==2 and all(c.get("native") is not None and c["native"].closed and c["native"].capture is not None
                 and c["native"].capture["cleanup"].get("echild") is True and c["native"].readback is not None
                 and c["native"].readback["launch_directory_empty"] for c in cases.values())
            result["cleanup"]["all_provider_closed"]=len(cases)==2 and all(c.get("provider") is not None and c["provider"].closed and c["provider"].joined for c in cases.values())
            # No executable finally after a refusal. The closing Git site is five real Git queries.
            if safe and result["failure"] is None and result["cleanup"]["global_echild_after_close"]:
                try:
                    phase="CLOSING_GIT_ADMISSION";core_bookend()
                    for family,case in cases.items():case_bookend(family,case)
                    need(deadline-time.monotonic()>=35,"CLOSING_EXECUTABLE_BUDGET_UNAVAILABLE")
                    a.quiescent(u)
                    git_after,unused=h.git_startup_guard(gate_home,False,source)
                    need(git_after==git_before,"GIT_BOOKEND_CHANGED");a.write_new(private/"GIT_AFTER.json",git_after)
                    core_bookend();a.quiescent(u)
                    phase="CURRENTNESS_AFTER";receipt=a.currentness_capture(args,source,gate_home,private,u,records,deadline,"gate-after")
                    need(receipt==result["currentness_receipt_sha256"],"CURRENTNESS_RECEIPT_CHANGED")
                    result["currentness_after"]=True;result["git_unchanged"]=True
                except BaseException as exc:fail(exc,phase)
            try:
                if source_before is not None:
                    core_bookend();result["source_after"]=True;result["runtime_after"]=True
                    a.write_new(private/"SOURCE_AFTER.json",{"inputs":source_inputs(source,source_pins,args.expected_uid,a),"store":h.source_store_guard(source)})
                    a.write_new(private/"RUNTIME_AFTER.json",a.runtime_guard(binary,args.expected_uid))
                a.write_new(private/"CURRENTNESS_COMMANDS.json",records)
                payload_rows=payload_owners(payloads,cases,args.expected_uid,args.expected_gid,a)
                a.write_new(private/"PAYLOAD_OWNERS.json",payload_rows)
                runtime_rows=runtime_owner_rows(runtime_root,args.expected_uid,args.expected_gid,a)
                result["cleanup"]["runtime_owner_sha256"]=a.write_new(private/"RUNTIME_OWNER.json",runtime_rows)
                result["cleanup"]["runtime_copy_files_retained"]=sum(row["kind"]=="REGULAR" for row in runtime_rows)
                seal={"schema":"dg17.codex.content.private-seal.v1","members":metadata_rows(private,cases,args.expected_uid,args.expected_gid,a)}
                result["cleanup"]["private_seal_sha256"]=a.write_new(private/"PRIVATE_EVIDENCE_SEAL.json",seal)
                a.quiescent(u);result["cleanup"]["global_echild_after_seal"]=True
                need(metadata_rows(private,cases,args.expected_uid,args.expected_gid,a)==seal["members"],"PRIVATE_SEAL_CHANGED")
                for family,case in cases.items():
                    if case.get("config_before") is not None:case_bookend(family,case)
                need(runtime_owner_rows(runtime_root,args.expected_uid,args.expected_gid,a)==runtime_rows,"RUNTIME_OWNER_CHANGED")
                need(payload_owners(payloads,cases,args.expected_uid,args.expected_gid,a)==payload_rows,"PAYLOAD_OWNER_CHANGED")
                core_bookend();need(time.monotonic()<=deadline,"INNER_DEADLINE_EXCEEDED")
                result["cleanup"]["private_seal_unchanged"]=True
            except BaseException as exc:fail(exc,"FINAL_DATA_RECEIVING")
    success=(result["failure"] is None and result["currentness_after"] and result["source_after"] and result["runtime_after"]
        and len(result["cases"])==2 and all(case["status"]=="FULL_GOVERNOR_NATIVE_RETURN_OBSERVED" for case in result["cases"])
        and result["requested_rpc_count"]==12 and result["requested_builtin_reads"]==2 and not result["unstarted_families"]
        and all(result["cleanup"][key] for key in ("all_native_closed","all_provider_closed","global_echild_after_close","global_echild_after_seal","private_seal_unchanged"))
        and result["cleanup"]["runtime_copy_files_retained"]==0)
    result["status"]="OBSERVED_TWO_FAMILY_FULL_GOVERNOR_CONTENT" if success else "FAILED_OR_UNRECEIVED"
    raw=encoded(result);need(len(raw)<=PUBLIC_LIMIT,"PUBLIC_OUTPUT_BOUND")
    if result_path is not None and result_path.parent.exists():
        fd=os.open(result_path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
        with os.fdopen(fd,"wb") as stream:stream.write(raw)
    return result

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ("source","episode","binary","controller","receipt","parent-netns","canonical-archive","standalone-archive"):
        parser.add_argument("--"+name,required=True)
    for name in ("expected-uid","expected-gid"):parser.add_argument("--"+name,type=int,required=True)
    args=parser.parse_args()
    def interrupted(signum,frame):raise Refusal("HOST_INTERRUPTED")
    signal.signal(signal.SIGTERM,interrupted);signal.signal(signal.SIGINT,interrupted)
    result=run(args);sys.stdout.buffer.write(encoded(result));sys.stdout.buffer.flush()
    return 0 if result["status"]=="OBSERVED_TWO_FAMILY_FULL_GOVERNOR_CONTENT" else 1

if __name__=="__main__":raise SystemExit(main())
