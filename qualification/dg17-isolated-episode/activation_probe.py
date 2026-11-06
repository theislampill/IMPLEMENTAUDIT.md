#!/usr/bin/env python3
"""DG17 separately admitted hosted local source-candidate activation.
Author preparation only. No local execution, model, thread, auth or trigger call.
Large exact image/cache owners are separate from the bounded metadata owner.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, os, re, signal, stat, sys, time, tomllib
from pathlib import Path

SOURCE_COMMIT="0d57929be5bd15682b4e9da2c0209d5dff307843"
SOURCE_TREE="ee316c27250ec422d35a1ea965182ebddf7a5da0"
MANIFEST_SHA="ed6a601d3a66997218195202cb5513363b5410b98489762324095a9030c261b4"
ADMISSION_SHA="9456e39cf3be3254b4c25c74716a1b87ba5f2accd6bf196db061e326c7a50277"
UTILITY_SHA="429c6b50cef6ef6352a0c812ce9fcf386cc852156ba54c2d1419088c8f89f85c"
VERSION="0.167.0-alpha.4"
BINARY_BYTES=324012616
BINARY_SHA="57c94ea520df28beb76955316c5c48f672550fe42c6cff7003badb76e1ee10d8"
FILE_COUNT=1755
DIR_COUNT=418
PAYLOAD_BYTES=165855954
PLUGIN_ID="implementaudit@implementaudit"
CACHE_REL="plugins/cache/implementaudit/implementaudit/0.4.0"
SELECTOR=".claude-plugin/marketplace.json:implementaudit:./"
METHODS=("initialize","plugin/install","plugin/read","skills/list","hooks/list")
SKILLS=("implementaudit","audit-state","audit-assess","audit-implement","audit-andon")
NAME_MAP={
 "implementaudit:implementaudit":"implementaudit",
 "implementaudit:audit-state":"audit-state",
 "implementaudit:audit-assess":"audit-assess",
 "implementaudit:audit-implement":"audit-implement",
 "implementaudit:audit-andon":"audit-andon",
}
METADATA_FILE_BYTES=8388608
METADATA_TOTAL_BYTES=33554432
METADATA_ENTRY_COUNT=512
PUBLIC_BYTES=32768
EMPTY_SHA=hashlib.sha256(b"").hexdigest()

class Refusal(RuntimeError):pass
def need(ok,code):
    if not ok:raise Refusal(code)
def encoded(value):
    return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=True,allow_nan=False)+"\n").encode()
def sha(raw):return hashlib.sha256(raw).hexdigest()
def unique(pairs):
    value={}
    for key,item in pairs:
        need(key not in value,"DUPLICATE_JSON_KEY")
        value[key]=item
    return value
def parsed(raw):
    def nonfinite(unused):raise Refusal("NONFINITE_JSON_VALUE")
    return json.loads(raw,object_pairs_hook=unique,parse_constant=nonfinite)
def identity(info):
    return {"device":info.st_dev,"inode":info.st_ino,"mode":stat.S_IMODE(info.st_mode),
            "uid":info.st_uid,"gid":info.st_gid,"links":info.st_nlink,"bytes":info.st_size,
            "mtime_ns":info.st_mtime_ns,"ctime_ns":info.st_ctime_ns}
def physical_dir(path,uid,gid,private=False):
    info=path.lstat()
    need(path.is_absolute() and path.resolve(strict=True)==path and stat.S_ISDIR(info.st_mode)
         and info.st_uid==uid and info.st_gid==gid and not info.st_mode&0o022
         and (not private or stat.S_IMODE(info.st_mode)==0o700),"OWNED_DIRECTORY_SHAPE")
    return identity(info)
def regular_bytes(path,limit,uid=None,expected=None,copy_to=None):
    """No-follow stable file read, optionally into a newly owned image member."""
    before=path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and 0<=before.st_size<=limit,
         "REGULAR_FILE_SHAPE")
    if uid is not None:need(before.st_uid==uid and not before.st_mode&0o022,"REGULAR_FILE_OWNER")
    fd=os.open(path,os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW)
    out=None;data=bytearray();h=hashlib.sha256();size=0
    try:
        need(identity(os.fstat(fd))==identity(before),"FILE_OPEN_IDENTITY")
        if copy_to is not None:
            out=os.open(copy_to,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_CLOEXEC|os.O_NOFOLLOW,
                        stat.S_IMODE(before.st_mode))
        while True:
            chunk=os.read(fd,1048576)
            if not chunk:break
            size+=len(chunk);need(size<=limit,"REGULAR_FILE_BOUND");h.update(chunk)
            if expected is None and copy_to is None:data.extend(chunk)
            if out is not None:
                view=memoryview(chunk)
                while view:
                    wrote=os.write(out,view);need(wrote>0,"IMAGE_WRITE_FAILED");view=view[wrote:]
        need(identity(os.fstat(fd))==identity(before) and identity(path.lstat())==identity(before)
             and size==before.st_size,"FILE_CHANGED_DURING_READ")
        if out is not None:
            os.fchmod(out,stat.S_IMODE(before.st_mode));os.fsync(out)
        if expected is not None:
            need(size==expected["bytes"] and h.hexdigest()==expected["sha256"],"FROZEN_FILE_BYTES")
        return bytes(data),{"bytes":size,"sha256":h.hexdigest(),"identity":identity(before)}
    finally:
        if out is not None:os.close(out)
        os.close(fd)
def write_new(path,value):
    raw=encoded(value);need(len(raw)<=METADATA_FILE_BYTES,"METADATA_WRITE_BOUND")
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_CLOEXEC|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,"wb") as f:f.write(raw);f.flush();os.fsync(f.fileno())
    return sha(raw)
def dependency(root,name,expected,module_name):
    raw,row=regular_bytes(root/name,1048576)
    need(row["sha256"]==expected and module_name not in sys.modules,"DEPENDENCY_PIN")
    spec=importlib.util.spec_from_file_location(module_name,root/name)
    module=importlib.util.module_from_spec(spec);sys.modules[module_name]=module
    spec.loader.exec_module(module)
    return module
def manifest_input(root):
    raw,row=regular_bytes(root/"SOURCE_MANIFEST.json",1048576)
    need(row["sha256"]==MANIFEST_SHA,"SOURCE_MANIFEST_PIN")
    m=parsed(raw)
    need(m["expected_tree"]==SOURCE_TREE and m["file_count"]==FILE_COUNT
         and m["total_bytes"]==PAYLOAD_BYTES and len(m["members"])==FILE_COUNT,
         "SOURCE_MANIFEST_SUBJECT")
    files={};dirs=set()
    for entry in m["members"]:
        name=entry["path"];path=Path(name)
        need(type(name) is str and path.as_posix()==name and not path.is_absolute()
             and all(p not in ("",".","..") for p in path.parts) and len(path.parts)<=9
             and path.parts[0] not in (".git",".IMPLEMENTAUDIT") and name not in files
             and entry["mode"] in ("100644","100755") and type(entry["bytes"]) is int
             and 0<=entry["bytes"]<=30022077
             and re.fullmatch("[0-9a-f]{64}",entry["sha256"]) is not None,
             "SOURCE_MANIFEST_POPULATION")
        files[name]=entry
        dirs.update(p.as_posix() for p in path.parents if p!=Path("."))
    need(len(files)==FILE_COUNT and len(dirs)==DIR_COUNT
         and sum(row["bytes"] for row in files.values())==PAYLOAD_BYTES,
         "SOURCE_MANIFEST_TOTAL")
    return files,dirs
def frozen_census(root,files,dirs,uid,gid,source=False):
    """Complete explicit enumeration: no DirEntry classification or silent OSError."""
    root_row=physical_dir(root,uid,gid)
    rows=[];observed_files=set();observed_dirs=set();pending=[root]
    while pending:
        parent=pending.pop();before=parent.lstat()
        need(stat.S_ISDIR(before.st_mode) and before.st_uid==uid and before.st_gid==gid
             and not before.st_mode&0o022 and parent.resolve(strict=True)==parent,
             "FROZEN_DIRECTORY_SHAPE")
        with os.scandir(parent) as stream:entries=list(stream)
        need(identity(parent.lstat())==identity(before),"FROZEN_DIRECTORY_CHANGED")
        for entry in entries:
            path=parent/entry.name;info=path.lstat();rel=path.relative_to(root).as_posix()
            if source and parent==root and entry.name in (".git",".IMPLEMENTAUDIT"):
                need(stat.S_ISDIR(info.st_mode) and info.st_uid==uid and info.st_gid==gid
                     and not info.st_mode&0o022 and path.resolve(strict=True)==path,
                     "SOURCE_EXCLUSION_NOT_OWNED_DIRECTORY")
                continue
            need(len(rows)<FILE_COUNT+DIR_COUNT,"FROZEN_POPULATION_LIMIT")
            if stat.S_ISDIR(info.st_mode):
                need(rel in dirs and stat.S_IMODE(info.st_mode)==0o755
                     and info.st_uid==uid and info.st_gid==gid,"FROZEN_DIRECTORY_POPULATION")
                observed_dirs.add(rel);rows.append({"path":rel,"kind":"DIRECTORY","identity":identity(info)})
                pending.append(path)
            else:
                need(rel in files and stat.S_ISREG(info.st_mode),"FROZEN_NONREGULAR_OR_EXTRA")
                expected=files[rel]
                need(info.st_uid==uid and info.st_gid==gid and stat.S_IMODE(info.st_mode)==
                     (0o755 if expected["mode"]=="100755" else 0o644),"FROZEN_MEMBER_MODE_OR_OWNER")
                _,readback=regular_bytes(path,expected["bytes"],uid,expected=expected)
                rows.append({"path":rel,"kind":"REGULAR",**readback});observed_files.add(rel)
    need(observed_files==set(files) and observed_dirs==dirs,"FROZEN_MISSING_POPULATION")
    need(identity(root.lstat())==root_row,"FROZEN_ROOT_CHANGED")
    return {"root":root_row,"rows":sorted(rows,key=lambda row:row["path"])}
def physical_store(source,uid,gid):
    """Complete data-only Git-store identity and byte census, with stable reads."""
    root=source/".git";root_row=physical_dir(root,uid,gid);rows=[];pending=[root];directories=[];total=0
    while pending:
        parent=pending.pop();before=parent.lstat();directories.append((parent,identity(before)))
        need(stat.S_ISDIR(before.st_mode) and parent.resolve(strict=True)==parent,"STORE_DIRECTORY_SHAPE")
        with os.scandir(parent) as stream:entries=list(stream)
        need(identity(parent.lstat())==identity(before),"STORE_DIRECTORY_CHANGED")
        for entry in entries:
            path=parent/entry.name;info=path.lstat();relative=path.relative_to(root);rel=relative.as_posix()
            need(len(rows)<65536 and len(relative.parts)<=32 and len(rel)<=4096 and
                 info.st_uid==uid and info.st_gid==gid and not info.st_mode&0o022 and
                 (stat.S_ISDIR(info.st_mode) or (stat.S_ISREG(info.st_mode) and info.st_nlink==1)),
                 "STORE_PHYSICAL_POPULATION")
            need(rel not in ("commondir","gitdir","config.worktree","worktrees",
                 "objects/info/alternates","objects/info/http-alternates"),"STORE_REDIRECTION")
            if rel.startswith("hooks/"):need(stat.S_ISREG(info.st_mode) and rel.endswith(".sample"),"STORE_ACTIVE_HOOK")
            row={"path":rel,"kind":"DIRECTORY" if stat.S_ISDIR(info.st_mode) else "REGULAR",
                 "identity":identity(info)}
            if stat.S_ISDIR(info.st_mode):pending.append(path)
            else:
                need(0<=info.st_size<=536870912 and total+info.st_size<=536870912,"STORE_BYTE_BOUND")
                row["sha256"]=file_digest(path)
                need(identity(path.lstat())==identity(info),"STORE_MEMBER_CHANGED")
                total+=info.st_size
            rows.append(row)
    head,_=regular_bytes(root/"HEAD",64,uid)
    need(head==(SOURCE_COMMIT+"\n").encode(),"SOURCE_DETACHED_HEAD_DIFFERS")
    need(identity(root.lstat())==root_row and all(identity(path.lstat())==observed for path,observed in directories),
         "STORE_ROOT_OR_DIRECTORY_CHANGED")
    return {"root":root_row,"rows":sorted(rows,key=lambda row:row["path"])}
def make_image(source,image,files,dirs,uid,gid):
    need(not os.path.lexists(image),"SOURCE_IMAGE_NOT_FRESH")
    image.mkdir(mode=0o755)
    for rel in sorted(dirs,key=lambda x:(len(Path(x).parts),x)):
        (image/rel).mkdir(mode=0o755)
    for rel,expected in sorted(files.items()):
        regular_bytes(source/rel,expected["bytes"],uid,expected=expected,copy_to=image/rel)
    return frozen_census(image,files,dirs,uid,gid)
def frozen_summary(snapshot):
    files=[row for row in snapshot["rows"] if row["kind"]=="REGULAR"]
    return {"files":len(files),"directories":len(snapshot["rows"])-len(files),
            "bytes":sum(row["bytes"] for row in files),"manifest_sha256":MANIFEST_SHA,
            "physical_census_sha256":sha(encoded(snapshot)),"complete_exact_population":True}
def startup_absence(source,image,neutral,home):
    for root in (source,image,neutral):
        for ancestor in (root,*root.parents):
            for name in ("config.toml","hooks.json","managed_config.toml","requirements.toml"):
                need(not os.path.lexists(ancestor/".codex"/name),"UNREVIEWED_PROJECT_STARTUP_LAYER")
    for name in ("config.toml","managed_config.toml","requirements.toml","hooks.json"):
        need(not os.path.lexists(Path("/etc/codex")/name),"UNREVIEWED_SYSTEM_STARTUP_LAYER")
    for name in ("auth.json","auth.json.tmp","managed_config.toml","requirements.toml","hooks.json",".gitconfig"):
        need(not os.path.lexists(home/name),"UNREVIEWED_NATIVE_HOME_LAYER")
    need(not os.path.lexists(home/".config/git/config"),"NATIVE_GLOBAL_GIT_CONFIG")
    for rel in ("plugin.json",".mcp.json",".app.json","hooks/hooks.json","commands",
                ".codex-plugin/migrated-command-skills"):
        need(not os.path.lexists(image/rel),"CANDIDATE_UNREVIEWED_ACTIVE_COMPONENT")
    need(not any(neutral.iterdir()),"NEUTRAL_CWD_CHANGED")
    return True
def config_readback(home,uid,gid):
    path=home/"config.toml";raw,row=regular_bytes(path,4096,uid)
    need(path.resolve(strict=True)==path and row["identity"]["gid"]==gid
         and row["identity"]["mode"] in (0o600,0o644),"NATIVE_CONFIG_FILE_SHAPE")
    value=tomllib.loads(raw.decode("utf-8"))
    need(value=={"plugins":{PLUGIN_ID:{"enabled":True}}} and value["plugins"][PLUGIN_ID]["enabled"] is True,
         "NATIVE_CONFIG_EXTRA_OR_DISABLED")
    return {"profile":"SOLE_LOCAL_PLUGIN_ENABLED_V1","bytes":len(raw),"sha256":sha(raw),
            "identity":row["identity"],"enabled":True,"entry_count":1}
def metadata_rows(evidence,home,cache,uid,gid):
    rows=[];total=0
    for owner,root in (("evidence",evidence),("native-home",home)):
        physical_dir(root,uid,gid,private=True)
        pending=[root]
        while pending:
            parent=pending.pop();before=parent.lstat()
            with os.scandir(parent) as stream:entries=list(stream)
            need(identity(parent.lstat())==identity(before),"METADATA_DIRECTORY_CHANGED")
            for entry in entries:
                path=parent/entry.name
                if path==evidence/"PRIVATE_EVIDENCE_SEAL.json":continue
                info=path.lstat();rel=owner+"/"+path.relative_to(root).as_posix()
                need(len(rows)<METADATA_ENTRY_COUNT and len(Path(rel).parts)<=18
                     and info.st_uid==uid and info.st_gid==gid
                     and (not (stat.S_ISDIR(info.st_mode) or stat.S_ISREG(info.st_mode))
                          or not info.st_mode&0o022),
                     "METADATA_POPULATION_OR_OWNER")
                if path==cache:
                    need(stat.S_ISDIR(info.st_mode) and path.resolve(strict=True)==path,"CACHE_OWNER_BOUNDARY")
                    rows.append({"path":rel,"kind":"EXACT_PAYLOAD_OWNER","identity":identity(info)})
                elif stat.S_ISDIR(info.st_mode):
                    rows.append({"path":rel,"kind":"DIRECTORY","identity":identity(info)});pending.append(path)
                elif stat.S_ISREG(info.st_mode):
                    _,member=regular_bytes(path,METADATA_FILE_BYTES,uid)
                    total+=member["bytes"];need(total<=METADATA_TOTAL_BYTES,"METADATA_AGGREGATE_BOUND")
                    rows.append({"path":rel,"kind":"REGULAR",**member})
                else:
                    rows.append({"path":rel,"kind":"NONREGULAR","identity":identity(info)})
    return sorted(rows,key=lambda row:row["path"])
def file_digest(path):
    before=path.lstat();need(stat.S_ISREG(before.st_mode) and before.st_nlink==1
         and 0<=before.st_size<=536870912,"DIGEST_FILE_SHAPE")
    fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_CLOEXEC);h=hashlib.sha256();size=0
    try:
        need(identity(os.fstat(fd))==identity(before),"DIGEST_OPEN_CHANGED")
        while True:
            raw=os.read(fd,1048576)
            if not raw:break
            size+=len(raw);need(size<=before.st_size,"DIGEST_READ_BOUND");h.update(raw)
        need(size==before.st_size and identity(os.fstat(fd))==identity(before)
             and identity(path.lstat())==identity(before),"DIGEST_CHANGED")
        return h.hexdigest()
    finally:os.close(fd)
def quiescent(u):
    need(u.children()==[],"GLOBAL_OWNED_CHILDREN_REMAIN")
    try:pid,status=os.waitpid(-1,os.WNOHANG|0x40000000)
    except ChildProcessError:return True
    raise Refusal("GLOBAL_ECHILD_NOT_ESTABLISHED")
def runtime_guard(binary,uid):
    _,row=regular_bytes(binary,BINARY_BYTES,uid,expected={"bytes":BINARY_BYTES,"sha256":BINARY_SHA})
    need(binary.resolve(strict=True)==binary and row["identity"]["mode"]==0o700,"RUNTIME_FILE_SHAPE")
    return row
def executable_bookend(h):
    return {name:h.executable_identity(Path("/usr/bin")/name) for name in ("python3","bash","env")}
def git_metadata_equal(h,home,source,previous):
    """Data only. Admit exact prior resolver/tool/config/store identities before Git."""
    binary,helper_path,resolution=h.git_system_paths()
    need(resolution==previous["resolver"] and h.executable_identity(Path(binary))==previous["git"]
         and h.root_path_identity(Path("/usr/lib/git-core"))==previous["libexec"]
         and {n:h.executable_identity(Path("/usr/lib/git-core")/n) for n in previous["helpers"]}==previous["helpers"]
         and h.git_home_guard(home,False)==previous["home"]
         and h.source_store_guard(source)==previous["source_store"],"GIT_METADATA_CHANGED")
    old=previous["system_config"];base={k:v for k,v in old.items() if k not in {"bytes","sha256","mtime_ns","ctime_ns"}}
    need(h.root_path_identity(h.SYSTEM_GIT_CONFIG,absent_ok=True)==base,"GIT_SYSTEM_IDENTITY_CHANGED")
    if old["present"]:
        info=h.SYSTEM_GIT_CONFIG.lstat()
        need(info.st_size==old["bytes"] and info.st_mtime_ns==old["mtime_ns"]
             and info.st_ctime_ns==old["ctime_ns"] and file_digest(h.SYSTEM_GIT_CONFIG)==old["sha256"],
             "GIT_SYSTEM_BYTES_CHANGED")
    return True

def payload_owner_guard(payloads,image,home,neutral,uid,gid):
    physical_dir(payloads,uid,gid,private=True)
    with os.scandir(payloads) as stream:entries=list(stream)
    need({e.name for e in entries}=={"source-image","native-home","neutral"},"PAYLOAD_OWNER_POPULATION")
    rows={}
    for name,path in (("source-image",image),("native-home",home),("neutral",neutral)):
        observed=physical_dir(path,uid,gid,private=name!="source-image")
        rows[name]={key:observed[key] for key in ("device","inode","mode","uid","gid")}
    need(not any(neutral.iterdir()),"NEUTRAL_CWD_NOT_EMPTY")
    return rows
def requests(image,neutral):
    return [
      {"id":1,"method":"initialize","params":{"clientInfo":{"name":"dg17_t12_activation","version":"1.0.0"},
                                            "capabilities":{"experimentalApi":True}}},
      {"method":"initialized"},
      {"id":2,"method":"plugin/install","params":{"pluginName":"implementaudit",
                "marketplacePath":str(image/".claude-plugin/marketplace.json")}},
      {"id":3,"method":"plugin/read","params":{"pluginName":"implementaudit",
                "marketplacePath":str(image/".claude-plugin/marketplace.json")}},
      {"id":4,"method":"skills/list","params":{"cwds":[str(neutral)],"forceReload":True}},
      {"id":5,"method":"hooks/list","params":{"cwds":[str(neutral)]}},
    ]
def protocol_projection(events,wanted,complete=False):
    need(type(events) is list and len(events)<=64,"PROTOCOL_EVENT_BOUND")
    sends=[];responses={};skills_changed=0;remote=[];started=0;terminated=0;seen_request_ids=set()
    for index,event in enumerate(events):
        need(type(event) is dict and set(event)=={"sequence","monotonic_ns","direction","value"}
             and type(event["sequence"]) is int and event["sequence"]==index+1
             and type(event["monotonic_ns"]) is int and event["monotonic_ns"]>=0,"PROTOCOL_RECORD_SHAPE")
        direction=event["direction"];value=event["value"]
        if direction=="send":
            need(type(value) is dict and len(sends)<len(wanted) and value==wanted[len(sends)],
                 "NONADMITTED_OUTBOUND_FRAME")
            sends.append(value)
            if "id" in value:seen_request_ids.add(value["id"])
        elif direction=="recv_raw":
            need(type(value) is str and len(value.encode())<=65536,"PROTOCOL_LINE_BOUND")
            message=parsed(value)
            need(type(message) is dict,"PROTOCOL_MESSAGE_SHAPE")
            if "id" in message:
                need(set(message)=={"id","result"} and type(message["id"]) is int
                     and message["id"] in seen_request_ids and message["id"] not in responses,
                     "SERVER_REQUEST_ERROR_OR_UNBOUND_RESPONSE")
                responses[message["id"]]=message["result"]
            else:
                need(set(message)=={"method","params","emittedAtMs"} and type(message["emittedAtMs"]) is int and 0<=message["emittedAtMs"]<=9223372036854775807,"NOTIFICATION_SHAPE")
                method=message["method"];params=message["params"]
                if method=="skills/changed":
                    need(params=={} and type(params) is dict,"SKILLS_NOTIFICATION_SHAPE")
                    skills_changed+=1;need(skills_changed<=16,"SKILLS_NOTIFICATION_BOUND")
                elif method=="remoteControl/status/changed":
                    need(type(params) is dict and {"status","installationId","serverName"}<=set(params)
                         <={"status","installationId","serverName","environmentId"}
                         and params["status"]=="disabled" and params.get("environmentId") is None
                         and all(type(params[k]) is str and 1<=len(params[k].encode())<=256
                                 for k in ("installationId","serverName")),
                         "REMOTE_CONTROL_NOTIFICATION_UNADMITTED")
                    remote.append(sha(encoded(params)));need(len(remote)<=16,"REMOTE_NOTIFICATION_BOUND")
                else:raise Refusal("UNADMITTED_NOTIFICATION")
        elif direction=="lifecycle":
            need(type(value) is dict and value.get("event") in ("started","terminated"),
                 "UNADMITTED_LIFECYCLE_RECORD")
            if value["event"]=="started":started+=1
            else:terminated+=1
        else:raise Refusal("UNADMITTED_PROTOCOL_RECORD")
    need(started==1 and terminated<=1,"LIFECYCLE_RECORD_POPULATION")
    if complete:
        need(sends==wanted and set(responses)=={1,2,3,4,5} and terminated==1,
             "PROTOCOL_EXACT_POPULATION")
    return {"skills_changed_count":skills_changed,"remote_control_disabled_count":len(remote),
            "remote_control_payload_sha256":remote,"unknown_frames":0,"server_requests":0,
            "nonadmitted_outbound":0,"response_count":len(responses),"wire_complete":complete},responses
def initialize_projection(response,home):
    need(type(response) is dict and set(response)=={"userAgent","codexHome","platformFamily","platformOs"}
         and response["codexHome"]==str(home) and response["platformFamily"]=="unix"
         and response["platformOs"]=="linux" and type(response["userAgent"]) is str
         and VERSION in response["userAgent"] and len(response["userAgent"])<=1024,
         "INITIALIZE_IDENTITY_DIFFERS")
    return True
def install_projection(response):
    need(type(response) is dict and set(response)=={"authPolicy","appsNeedingAuth"}
         and response["authPolicy"]=="ON_INSTALL" and type(response["appsNeedingAuth"]) is list
         and response["appsNeedingAuth"]==[],"INSTALL_RESPONSE_UNADMITTED")
    return {"status":"LOCAL_INSTALL_RESPONSE_OBSERVED","auth_policy":"ON_INSTALL","apps_needing_auth_count":0}
def skill_projection(row,root,files,cached=False):
    need(type(row) is dict and type(row.get("name")) is str and type(row.get("enabled")) is bool,
         "SKILL_METADATA_SHAPE")
    name=NAME_MAP.get(row["name"])
    if name is None:return None
    rel="skills/"+name+"/SKILL.md"
    need(row.get("path")==str(root/rel) and row["enabled"] is True,"SKILL_PATH_OR_ENABLED_DIFFERS")
    if cached:need(row.get("pluginId")==PLUGIN_ID,"SKILL_PLUGIN_ATTRIBUTION_DIFFERS")
    return {"name":name,"path":rel,"sha256":files[rel]["sha256"],"enabled":True,
            "exact_selected_root":True,"plugin_attribution_matches":cached}
def catalog_projection(response,image,files):
    need(type(response) is dict and set(response)=={"plugin"} and type(response["plugin"]) is dict,
         "PLUGIN_READ_SHAPE")
    detail=response["plugin"];summary=detail.get("summary")
    need(type(summary) is dict and summary.get("id")==PLUGIN_ID and summary.get("name")=="implementaudit"
         and summary.get("installed") is True and summary.get("enabled") is True
         and summary.get("authPolicy")=="ON_INSTALL" and summary.get("source")=={"type":"local","path":str(image)}
         and detail.get("marketplacePath")==str(image/".claude-plugin/marketplace.json")
         and detail.get("marketplaceName")=="implementaudit","PLUGIN_LOCAL_SOURCE_OR_STATE")
    for name in ("apps","appTemplates","mcpServers","hooks"):
        need(type(detail.get(name)) is list and detail[name]==[],"PLUGIN_UNREVIEWED_ACTIVE_COMPONENT")
    need(type(detail.get("skills")) is list and len(detail["skills"])==5,"PLUGIN_SKILL_POPULATION")
    rows=[skill_projection(row,image,files) for row in detail["skills"]]
    need(all(row is not None for row in rows) and {row["name"] for row in rows}==set(SKILLS),
         "PLUGIN_FIVE_SKILL_POPULATION")
    return {"status":"SOURCE_CANDIDATE_INSTALLED_ENABLED","id":PLUGIN_ID,"installed":True,"enabled":True,
            "source_image_path_bound":True,"five_exact_skill_paths":True,
            "skills":sorted(rows,key=lambda row:row["name"]),"other_skill_count":0,
            "declared_hook_count":0,"declared_app_count":0,"declared_mcp_count":0}
def skills_projection(response,neutral,cache,files):
    need(type(response) is dict and set(response)=={"data"} and type(response["data"]) is list
         and len(response["data"])==1,"SKILLS_RESPONSE_SHAPE")
    data=response["data"][0]
    need(type(data) is dict and set(data)=={"cwd","skills","errors"} and data["cwd"]==str(neutral)
         and type(data["skills"]) is list and len(data["skills"])<=128
         and type(data["errors"]) is list and data["errors"]==[],"SKILLS_RESPONSE_SCOPE")
    rows=[];others=0
    for item in data["skills"]:
        row=skill_projection(item,cache,files,True)
        if row is None:
            need(item.get("pluginId")!=PLUGIN_ID and type(item.get("path")) is str,
                 "UNDECLARED_PLUGIN_SKILL")
            need(not Path(item["path"]).is_relative_to(cache),"UNATTRIBUTED_CACHE_SKILL")
            others+=1
        else:rows.append(row)
    need(len(rows)==5 and {row["name"] for row in rows}==set(SKILLS),"EFFECTIVE_FIVE_SKILLS_MISSING")
    return {"status":"CACHE_BACKED_ENABLED_SKILL_METADATA","skills":sorted(rows,key=lambda row:row["name"]),
            "other_skill_count":others,"other_skills_attributed_to_candidate":False,
            "error_count":0,"thread_content_loaded":False}
def hooks_projection(response,neutral):
    need(type(response) is dict and set(response)=={"data"} and type(response["data"]) is list
         and len(response["data"])==1,"HOOKS_RESPONSE_SHAPE")
    data=response["data"][0]
    need(type(data) is dict and set(data)=={"cwd","hooks","errors","warnings"}
         and data["cwd"]==str(neutral) and all(type(data.get(k)) is list and data[k]==[]
         for k in ("hooks","errors","warnings")),"HOOKS_RESPONSE_SCOPE")
    return {"status":"EMPTY_CONFIGURED_HOOK_METADATA","hook_count":0,"error_count":0,"warning_count":0,
            "loaded_thread_hooks_observed":False,"hook_delivery_exercised":False}
def currentness_capture(args,source,gate_home,private,u,records,deadline,label):
    quiescent(u)
    env={**u.safe_environment(),"HOME":str(gate_home),"TMPDIR":str(private)}
    argv=["/usr/bin/env","-i",*[k+"="+v for k,v in sorted(env.items())],
          "/usr/bin/bash",str(source/"skills/implementaudit/scripts/claim-run.sh"),
          "--require-current-continuity",args.controller]
    stdout=b"";stderr=b"";failure=None;start=len(records)
    try:
        rc,stdout,stderr=u.capture(label,argv,records,deadline,seconds=20)
    except BaseException as exc:
        failure=exc;captured=getattr(exc,"captured",{})
        stdout=captured.get("stdout",b"");stderr=captured.get("stderr",b"")
    finally:
        if len(records)>start:
            retained=False
            try:
                for suffix,raw in (("stdout",stdout),("stderr",stderr)):
                    need(type(raw) is bytes and len(raw)<=32768,"GATE_CAPTURE_BOUND")
                    fd=os.open(private/(label+"."+suffix),os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
                    with os.fdopen(fd,"wb") as f:f.write(raw)
                retained=True
            finally:
                records[-1].update(private_streams_retained=retained,retention_failure=not retained)
                write_new(private/(label+".capture.json"),[records[-1]])
    if failure is not None:raise failure
    need(len(records)==start+1 and rc==0 and stdout==(args.receipt+"\n").encode() and stderr==b""
         and records[-1].get("streams_complete") is True
         and records[-1].get("cleanup",{}).get("echild") is True,"CURRENTNESS_GATE_REFUSED")
    quiescent(u)
    return sha(stdout)
def safe_failure(exc,phase):
    code=str(exc)
    safe=type(exc).__name__=="Refusal" and re.fullmatch("[A-Z][A-Z0-9_]{0,95}",code) is not None
    return {"phase":phase,"code":code if safe else "OPERATION_EXCEPTION",
            "exception_type":type(exc).__name__ if type(exc).__name__ in
            {"Refusal","RuntimeError","TimeoutError","OSError","PermissionError","ValueError","KeyError",
             "TypeError","FileNotFoundError","ProcessLookupError","ChildProcessError","EOFError",
             "KeyboardInterrupt","SystemExit","Empty"} else "Exception"}
def clean_snapshot(row):
    return type(row) is dict and row.get("full_session_scope_available") is True and row.get("launch_directory_empty") is True and all(type(row.get(k)) is int and row[k]==0 for k in ("living_owned_processes","owned_zombies","uncertain_owned_candidates"))

def run(args):
    result={
      "schema":"dg17.t12.local-source-activation.v1","status":"NOT_EXECUTED",
      "source_commit":SOURCE_COMMIT,"source_tree":SOURCE_TREE,
      "runtime_version":VERSION,"runtime_sha256":BINARY_SHA,"runtime_bytes":BINARY_BYTES,
      "selector":SELECTOR,"plugin_id":PLUGIN_ID,"cache_relative_root":CACHE_REL,
      "source_identity_verified":False,"source_after_verified":False,"runtime_identity_verified":False,
      "runtime_reported_version_matches":False,"native_process_started":False,
      "currentness_before":False,"currentness_after":False,"executable_route_sound":False,
      "offline":None,"git_startup_admission":None,"calls":[],"install":None,"catalog":None,
      "configured_skills":None,"configured_hooks":None,"notifications":None,
      "payloads":{"source_image_before":None,"source_image_after_close":None,
                  "native_cache_after_install":None,"native_cache_after_close":None,
                  "source_image_unchanged":False,"cache_unchanged":False,
                  "after_seal_unchanged":False,"declared_full_payload_bytes":PAYLOAD_BYTES*2},
      "config":{"absent_before_install":False,"after_install":None,"after_close":None,
                "unchanged":False,"after_seal_unchanged":False},
      "metadata":{"seal_sha256":None,"files":0,"entries":0,"bytes":0,"unchanged":False,
                  "per_file_bound":METADATA_FILE_BYTES,"aggregate_bound":METADATA_TOTAL_BYTES,
                  "entry_bound":METADATA_ENTRY_COUNT},
      "cleanup":{"close_returned":False,"parent_returncode":None,"reader_joined":False,
                 "transport_remaining_owned_count":None,"close_error_type":None,"containment":None,
                 "after_close":None,"after_seal":None,"global_quiescence_after_close":False,
                 "global_quiescence_after_seal":False},
      "failure":None,"supplemental_failures":[],"additional_failure_count":0,
      "original_acceptance_awarded":False,"independent_receiving":"NOT_PERFORMED",
      "built_archive_binding_proven":False,"canonical_git_marketplace_qualified":False,
      "model_inference_proven":False,"prompt_independent_routing_proven":False,
      "thread_content_loaded":False,"lifecycle_trigger_delivery_proven":False,
    }
    phase="PRECONDITIONS";safe_route=False
    h=u=modules=native=None;private=home=cache=image=neutral=payloads=result_path=None
    source=packet=gate_home=binary=None;files=dirs=None
    source_before=store_before=image_before=cache_installed=config_installed=None
    runtime_before=tools_before=git_before=owner_before=None
    rpc_results={};gate_records=[];deadline=time.monotonic()+145
    def fail(exc,label):
        nonlocal safe_route
        safe_route=False;row=safe_failure(exc,label)
        if result["failure"] is None:result["failure"]=row
        elif len(result["supplemental_failures"])<8:result["supplemental_failures"].append(row)
        else:result["additional_failure_count"]+=1
    def guarded_data(label,operation):
        try:return operation()
        except BaseException as exc:fail(exc,label);return None
    def source_and_runtime_bookend():
        need(frozen_census(source,files,dirs,args.expected_uid,args.expected_gid,True)==source_before,
             "SOURCE_BOOKEND_DIFFERS")
        need(physical_store(source,args.expected_uid,args.expected_gid)==store_before,"STORE_BOOKEND_DIFFERS")
        need(runtime_guard(binary,args.expected_uid)==runtime_before,"RUNTIME_BOOKEND_DIFFERS")
        need(executable_bookend(h)==tools_before,"EXECUTABLE_BOOKEND_DIFFERS")
        need(startup_absence(source,image,neutral,home),"STARTUP_BOOKEND_DIFFERS")
        need(payload_owner_guard(payloads,image,home,neutral,args.expected_uid,args.expected_gid)==owner_before,
             "PAYLOAD_OWNER_IDENTITY_DIFFERS")
        return True
    def exact_payload_bookend(label):
        image_now=frozen_census(image,files,dirs,args.expected_uid,args.expected_gid)
        need(image_now==image_before,"IMAGE_BOOKEND_DIFFERS")
        cache_now=frozen_census(cache,files,dirs,args.expected_uid,args.expected_gid)
        need(cache_now==cache_installed,"CACHE_BOOKEND_DIFFERS")
        config_now=config_readback(home,args.expected_uid,args.expected_gid)
        need(config_now==config_installed,"CONFIG_BOOKEND_DIFFERS")
        return image_now,cache_now,config_now
    try:
        packet=Path(__file__).resolve(strict=True).parent
        h=dependency(packet,"catalogue_probe.py",ADMISSION_SHA,"dg17_activation_admission")
        u=dependency(packet,"host_utility.py",UTILITY_SHA,"dg17_activation_utility")
        result["offline"]=h.offline_guard(args)
        need(re.fullmatch("[a-z0-9][a-z0-9-]{0,95}",args.controller) is not None and
             re.fullmatch(r"refs/implementaudit/continuity-receipts/"+re.escape(args.controller)
                          +r"/G[0-9]{4}@[0-9a-f]{40}",args.receipt) is not None,
             "CONTINUITY_ARGUMENT_SHAPE")
        source=Path(args.source);episode=Path(args.episode);binary=Path(args.binary)
        physical_dir(source,args.expected_uid,args.expected_gid)
        physical_dir(episode,args.expected_uid,args.expected_gid,True)
        physical_dir(episode/"private",args.expected_uid,args.expected_gid,True)
        gate_home=episode/"home";physical_dir(gate_home,args.expected_uid,args.expected_gid,True)
        need(source.resolve(strict=True)==source and episode.resolve(strict=True)==episode
             and not source.is_relative_to(episode) and not episode.is_relative_to(source),
             "SOURCE_EPISODE_OVERLAP")
        private=episode/"private/native-activation";payloads=episode/"payloads"
        result_path=episode/"private/ACTIVATION_RESULT.json"
        need(not any(os.path.lexists(p) for p in (private,payloads,result_path)),"ACTIVATION_NOT_FRESH")
        private.mkdir(mode=0o700);payloads.mkdir(mode=0o700)
        home=payloads/"native-home";home.mkdir(mode=0o700)
        neutral=payloads/"neutral";neutral.mkdir(mode=0o700)
        image=payloads/"source-image";cache=home/CACHE_REL
        need(signal.getsignal(signal.SIGCHLD)==signal.SIG_DFL,"CHILD_REAP_POLICY")
        os.chdir(source)
        files,dirs=manifest_input(packet)
        phase="SOURCE_BEFORE"
        source_before=frozen_census(source,files,dirs,args.expected_uid,args.expected_gid,True)
        store_before=physical_store(source,args.expected_uid,args.expected_gid)
        h.source_store_guard(source)
        runtime_before=runtime_guard(binary,args.expected_uid);tools_before=executable_bookend(h)
        result["source_identity_verified"]=True;result["runtime_identity_verified"]=True
        write_new(private/"SOURCE_BEFORE.json",source_before)
        write_new(private/"SOURCE_STORE_BEFORE.json",store_before)
        phase="CURRENTNESS_BEFORE"
        currentness_capture(args,source,gate_home,private,u,gate_records,deadline,"gate-before")
        result["currentness_before"]=True
        phase="IMAGE_CONSTRUCTION"
        image_before=make_image(source,image,files,dirs,args.expected_uid,args.expected_gid)
        owner_before=payload_owner_guard(payloads,image,home,neutral,args.expected_uid,args.expected_gid)
        startup_absence(source,image,neutral,home)
        need(not os.path.lexists(home/"config.toml") and not os.path.lexists(home/"plugins"),
             "NATIVE_INSTALL_PRESTATE_NOT_EMPTY")
        result["config"]["absent_before_install"]=True
        result["payloads"]["source_image_before"]=frozen_summary(image_before)
        write_new(private/"IMAGE_BEFORE.json",image_before)
        write_new(private/"PAYLOAD_OWNERS_BEFORE.json",owner_before)
        phase="GIT_ADMISSION_BEFORE"
        source_and_runtime_bookend()
        need(frozen_census(image,files,dirs,args.expected_uid,args.expected_gid)==image_before,
             "IMAGE_CHANGED_BEFORE_GIT_ADMISSION")
        quiescent(u)
        git_before,result["git_startup_admission"]=h.git_startup_guard(home,True,source)
        quiescent(u)
        need(result["git_startup_admission"]["system_config_state"]=="EMPTY"
             and result["git_startup_admission"]["system_config_entries"]==0
             and result["git_startup_admission"]["system_config_bytes"]==0
             and result["git_startup_admission"]["system_config_sha256"]==EMPTY_SHA,
             "CAPSULE_EMPTY_GIT_CONFIG_REQUIRED")
        write_new(private/"GIT_ADMISSION_BEFORE.json",git_before)
        source_and_runtime_bookend()
        need(frozen_census(image,files,dirs,args.expected_uid,args.expected_gid)==image_before,
             "IMAGE_CHANGED_BEFORE_NATIVE")
        git_metadata_equal(h,home,source,git_before);quiescent(u)
        modules=h.load_transports(packet)
        phase="NATIVE_CONSTRUCTOR";safe_route=True
        native_type=modules["native_transport"].Native
        native=native_type.__new__(native_type)
        native_type.__init__(native,binary,home,neutral,private/"transport",extra=h.EXTRA)
        result["native_process_started"]=True
        need(native.binary_sha256==BINARY_SHA,"NATIVE_LAUNCH_COPY_DIFFERS")
        wanted=requests(image,neutral)
        for request in (row for row in wanted if "id" in row):
            method=request["method"];phase=method
            need(time.monotonic()<deadline,"INNER_DEADLINE")
            if method=="plugin/install":
                need(not os.path.lexists(home/"config.toml") and not os.path.lexists(cache),
                     "INSTALL_PRESTATE_CHANGED")
                need(frozen_census(image,files,dirs,args.expected_uid,args.expected_gid)==image_before,
                     "IMAGE_CHANGED_BEFORE_INSTALL")
                startup_absence(source,image,neutral,home)
            response=native.rpc(method,request["params"],timeout=min(20,max(0.1,deadline-time.monotonic())))
            rpc_results[method]=response
            result["calls"].append({"method":method,"status":"RPC_RETURNED"})
            if method=="initialize":
                initialize_projection(response,home)
                result["runtime_reported_version_matches"]=True
                native.send({"method":"initialized"})
            elif method=="plugin/install":
                result["install"]=install_projection(response)
                cache_installed=frozen_census(cache,files,dirs,args.expected_uid,args.expected_gid)
                config_installed=config_readback(home,args.expected_uid,args.expected_gid)
                result["payloads"]["native_cache_after_install"]=frozen_summary(cache_installed)
                result["config"]["after_install"]={k:v for k,v in config_installed.items() if k!="identity"}
                write_new(private/"CACHE_AFTER_INSTALL.json",cache_installed)
                write_new(private/"CONFIG_AFTER_INSTALL.json",config_installed)
            elif method=="plugin/read":
                result["catalog"]=catalog_projection(response,image,files)
            elif method=="skills/list":
                result["configured_skills"]=skills_projection(response,neutral,cache,files)
            else:
                result["configured_hooks"]=hooks_projection(response,neutral)
            with native.lock:events=list(native.events)
            protocol_projection(events,wanted)
            result["calls"][-1]["status"]="OBSERVED"
        phase="RPC_COMPLETE"
    except BaseException as exc:
        fail(exc,phase)
    finally:
        if native is not None:
            result["native_process_started"]=hasattr(native,"proc")
            try:
                if hasattr(native,"reader") and hasattr(native,"process_identity"):
                    try:closed=native.close()
                    except BaseException as close_error:
                        result["cleanup"]["close_error_type"]=safe_failure(close_error,"CLOSE")["exception_type"]
                        raise
                    result["cleanup"]["close_returned"]=True
                    result["cleanup"].update(parent_returncode=closed["returncode"],
                      reader_joined=closed["reader_joined"],
                      transport_remaining_owned_count=len(closed["remaining_owned_processes"]))
                    need(closed["returncode"]==0 and closed["reader_joined"] is True
                         and not closed["remaining_owned_processes"] and closed["launch_directory_empty"] is True,
                         "NATIVE_CLOSE_INCOMPLETE")
                else:
                    result["cleanup"]["containment"]=h.contain_known_parent(native)
                    raise Refusal("NATIVE_CONSTRUCTOR_INCOMPLETE")
            except BaseException as exc:
                fail(exc,"NATIVE_CLOSE")
                try:result["cleanup"]["containment"]=h.contain_known_parent(native)
                except BaseException as contain_error:
                    result["cleanup"]["containment"]={"status":"CONTAINMENT_REFUSED","signals_sent":0}
                    fail(contain_error,"KNOWN_PARENT_CONTAINMENT")
            if not result["cleanup"]["close_returned"] or not result["cleanup"]["reader_joined"]:
                reader=getattr(native,"reader",None)
                if reader is not None:
                    try:reader.join(timeout=3)
                    except BaseException as exc:fail(exc,"READER_JOIN")
                for name in ("capture","stderr"):
                    stream=getattr(native,name,None)
                    if stream is not None and not stream.closed:
                        try:stream.close()
                        except BaseException as exc:fail(exc,"STREAM_CLOSE")
            snap=guarded_data("AFTER_CLOSE_OBSERVATION",lambda:h.independent_readback(native,modules))
            result["cleanup"]["after_close"]=snap
            if not clean_snapshot(snap):fail(Refusal("AFTER_CLOSE_NOT_QUIESCENT"),"AFTER_CLOSE_OBSERVATION")
            if guarded_data("GLOBAL_AFTER_CLOSE",lambda:quiescent(u)):
                result["cleanup"]["global_quiescence_after_close"]=True
            try:
                events=list(getattr(native,"events",[]))
                result["notifications"],responses=protocol_projection(events,requests(image,neutral),True)
                need(rpc_results=={METHODS[i-1]:responses[i] for i in range(1,6)},
                     "RPC_CAPTURE_BINDING_DIFFERS")
            except BaseException as exc:fail(exc,"PROTOCOL_RECEIVING")
        if source_before is not None and owner_before is not None:
            if guarded_data("SOURCE_RUNTIME_AFTER_CLOSE",source_and_runtime_bookend):
                result["source_after_verified"]=True
                guarded_data("SOURCE_AFTER_RETAIN",lambda:write_new(private/"SOURCE_AFTER.json",source_before))
                guarded_data("STORE_AFTER_RETAIN",lambda:write_new(private/"SOURCE_STORE_AFTER.json",store_before))
        if cache_installed is not None and config_installed is not None:
            after=guarded_data("PAYLOADS_AFTER_CLOSE",lambda:exact_payload_bookend("AFTER_CLOSE"))
            if after is not None:
                image_after,cache_after,config_after=after
                result["payloads"].update(source_image_after_close=frozen_summary(image_after),
                  native_cache_after_close=frozen_summary(cache_after),source_image_unchanged=True,cache_unchanged=True)
                result["config"].update(after_close={k:v for k,v in config_after.items() if k!="identity"},unchanged=True)
                guarded_data("IMAGE_AFTER_RETAIN",lambda:write_new(private/"IMAGE_AFTER_CLOSE.json",image_after))
                guarded_data("CACHE_AFTER_RETAIN",lambda:write_new(private/"CACHE_AFTER_CLOSE.json",cache_after))
                guarded_data("CONFIG_AFTER_RETAIN",lambda:write_new(private/"CONFIG_AFTER_CLOSE.json",config_after))
        # Executable closing gates are reachable only on an uninterrupted sound route.
        # Failed metadata/custody/currentness never becomes a reason to run another helper.
        if safe_route and git_before is not None and result["source_after_verified"] and result["config"]["unchanged"]:
            try:
                phase="GIT_ADMISSION_AFTER"
                source_and_runtime_bookend();exact_payload_bookend("BEFORE_CLOSING_GIT")
                git_metadata_equal(h,home,source,git_before)
                quiescent(u)
                git_after,after_public=h.git_startup_guard(home,False,source)
                quiescent(u)
                need(git_after==git_before,"GIT_ADMISSION_CHANGED")
                write_new(private/"GIT_ADMISSION_AFTER.json",git_after)
                result["git_startup_admission"].update(after_passed=True,identities_unchanged=True,
                    after_identity_sha256=after_public["before_identity_sha256"])
                phase="CURRENTNESS_AFTER"
                source_and_runtime_bookend();exact_payload_bookend("BEFORE_CLOSING_CURRENTNESS")
                git_metadata_equal(h,home,source,git_before);quiescent(u)
                currentness_capture(args,source,gate_home,private,u,gate_records,deadline,"gate-after")
                result["currentness_after"]=True
                # Remaining closure is data-only: no third Git helper or extra currentness command.
                source_and_runtime_bookend();exact_payload_bookend("AFTER_CLOSING_CURRENTNESS")
                git_metadata_equal(h,home,source,git_before);quiescent(u)
            except BaseException as exc:fail(exc,phase)
        if private is not None:
            guarded_data("RPC_RESULTS_RETAIN",lambda:write_new(private/"RPC_RESULTS.json",rpc_results))
            guarded_data("GATE_COMMANDS_RETAIN",lambda:write_new(private/"GATE_COMMANDS.json",gate_records))
        if private is not None and home is not None and cache is not None:
            try:
                rows=metadata_rows(private,home,cache,args.expected_uid,args.expected_gid)
                seal={"schema":"dg17.activation.small-evidence-seal.v1","files":rows,
                      "separate_payload_owners":["source-image",CACHE_REL],
                      "full_payload_manifest_sha256":MANIFEST_SHA}
                total=sum(row.get("bytes",0) for row in rows if row["kind"]=="REGULAR")
                need(total+len(encoded(seal))<=METADATA_TOTAL_BYTES,"METADATA_WITH_SEAL_BOUND")
                seal_sha=write_new(private/"PRIVATE_EVIDENCE_SEAL.json",seal)
                result["metadata"].update(seal_sha256=seal_sha,files=sum(r["kind"]=="REGULAR" for r in rows),
                    entries=len(rows),bytes=total+len(encoded(seal)))
                if native is not None:
                    result["cleanup"]["after_seal"]=h.independent_readback(native,modules)
                    need(clean_snapshot(result["cleanup"]["after_seal"]),"AFTER_SEAL_NOT_QUIESCENT")
                    quiescent(u);result["cleanup"]["global_quiescence_after_seal"]=True
                if cache_installed is not None:
                    exact_payload_bookend("AFTER_SEAL")
                    result["payloads"]["after_seal_unchanged"]=True
                    result["config"]["after_seal_unchanged"]=True
                if source_before is not None and owner_before is not None:source_and_runtime_bookend()
                need(metadata_rows(private,home,cache,args.expected_uid,args.expected_gid)==rows
                     and file_digest(private/"PRIVATE_EVIDENCE_SEAL.json")==seal_sha,"SMALL_EVIDENCE_CHANGED")
                result["metadata"]["unchanged"]=True
            except BaseException as exc:fail(exc,"DATA_SEAL_CLOSURE")
        result["executable_route_sound"]=safe_route
        flags=("source_identity_verified","source_after_verified","runtime_identity_verified",
               "runtime_reported_version_matches","native_process_started","currentness_before",
               "currentness_after","executable_route_sound")
        clean=result["cleanup"]
        git=result["git_startup_admission"] or {}
        success=(result["failure"] is None and not result["supplemental_failures"]
          and all(result[k] is True for k in flags)
          and result["calls"]==[{"method":m,"status":"OBSERVED"} for m in METHODS]
          and all(result[k] is not None for k in ("install","catalog","configured_skills","configured_hooks","notifications"))
          and result["notifications"]["wire_complete"] is True
          and git.get("after_passed") is True and git.get("identities_unchanged") is True
          and git.get("before_identity_sha256")==git.get("after_identity_sha256")
          and all(result["payloads"][k] is True for k in ("source_image_unchanged","cache_unchanged","after_seal_unchanged"))
          and all(result["config"][k] is True for k in ("absent_before_install","unchanged","after_seal_unchanged"))
          and result["metadata"]["unchanged"] is True and clean["close_returned"] is True
          and clean["reader_joined"] is True and clean["parent_returncode"]==0
          and clean["transport_remaining_owned_count"]==0 and clean["close_error_type"] is None
          and clean["containment"] is None and clean_snapshot(clean["after_close"]) and clean_snapshot(clean["after_seal"])
          and clean["global_quiescence_after_close"] is True and clean["global_quiescence_after_seal"] is True)
        result["status"]="OBSERVED_LOCAL_INSTALL_AND_CACHE_DISCOVERY" if success else "INCOMPLETE_OR_FAILED"
        raw=encoded(result);need(len(raw)<=PUBLIC_BYTES,"PUBLIC_RESULT_BOUND")
        if result_path is not None:
            fd=os.open(result_path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
            with os.fdopen(fd,"wb") as f:f.write(raw);f.flush();os.fsync(f.fileno())
        sys.stdout.buffer.write(raw);sys.stdout.buffer.flush()
    return 0 if result["status"]=="OBSERVED_LOCAL_INSTALL_AND_CACHE_DISCOVERY" else 1

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ("source","episode","binary","controller","receipt","parent-netns"):
        parser.add_argument("--"+name,required=True)
    parser.add_argument("--expected-uid",type=int,required=True)
    parser.add_argument("--expected-gid",type=int,required=True)
    args=parser.parse_args()
    def interrupted(signum,frame):raise Refusal("HOST_INTERRUPTED")
    signal.signal(signal.SIGTERM,interrupted)
    return run(args)

if __name__=="__main__":
    sys.exit(main())
