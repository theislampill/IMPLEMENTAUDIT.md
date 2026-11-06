#!/usr/bin/env python3
"""Windows10 request-bound preparation and one-shot admission. No inherent grant.

The accepted Campaign remains the effect owner. This layer requires an actual
held host, independent review and a separately published root GO. Public records
are closed projections; raw errors, commands and measurement remain private.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import time
import traceback

SOURCE_COMMIT = "8ee4ae44d67eb7ac8e8c7d8530c455ae1768605b"
SOURCE_TREE = "0da374609f7fea2463a2926f3603b976620bd10e"
OWNER_SHA256 = "1764b6f78ec473c7f2765993c117ff55d7d206d7522415ff4e531f335d126bcd"
REPOSITORY = "theislampill/IMPLEMENTAUDIT.md"
BRANCH = "pro/dg18-isolated-windows10-20261106"
CONTROL_BRANCH = "pro/dg18-isolated-windows10-control-20261106"
PREFIX = "qualification/dg18-isolated-windows10"
WORKFLOW = ".github/workflows/dg18-isolated-windows10.yml"
REVIEWER = "/root/windows10_review"
HOLD_SECONDS = 1200
OUTER_COMPLETION_SECONDS = 1200
MAX_DOCUMENT = 65536
MAX_STATE = 1048576
MAX_FILE = 33554432
MAX_MEASUREMENT = 16777216
PHASES = frozenset(("UNKNOWN","PREPARE_BINDING","PREPARATION_RECORDED","WAIT_START",
                   "CONTROL_POLL","CONTROL_FETCH","CONTROL_RECEIVE","GO_VALIDATION",
                   "GRANT_CONSUMPTION","PRIVATE_INVOCATION","FINAL_RECHECK","OUTER_JOB","TERMINAL_RECORD"))
ERROR_CLASSES = frozenset(("UNSPECIFIED","PREDICATE_REFUSED","FILE_IO_FAILURE","GIT_TIMEOUT",
                          "JOB_MEASUREMENT_FAILURE","UNEXPECTED_FAILURE"))
CURRENT_PHASE = "UNKNOWN"
LIMITS = {"elapsed_ms":60000,"peak_aggregate_job_committed_bytes":201326592,
          "baseline_subtracted_bytes":0,"descendants_included":True}
GIT_CANDIDATES = (r"C:\Program Files\Git\mingw64\bin\git.exe",
                  r"C:\Program Files\Git\ucrt64\bin\git.exe")
BASH = r"C:\Program Files\Git\bin\bash.exe"

class Refusal(RuntimeError):
    """A closed admission predicate was not established."""

def require(condition, reason):
    if not condition:
        raise Refusal(reason)

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def canonical(value):
    return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=False,allow_nan=False)+"\n").encode("utf-8")

def parse_document(raw, maximum=MAX_DOCUMENT):
    require(type(raw) is bytes and len(raw)<=maximum,"document budget/type")
    def pairs(items):
        result={}
        for key,value in items:
            require(key not in result,"duplicate JSON member")
            result[key]=value
        return result
    def invalid(value):
        raise Refusal("nonfinite JSON number")
    try:
        result=json.loads(raw.decode("utf-8"),object_pairs_hook=pairs,parse_constant=invalid)
    except (UnicodeError,ValueError,TypeError) as exc:
        raise Refusal("invalid JSON document") from exc
    require(type(result) is dict,"JSON object required")
    def finite(value):
        if type(value) is float:
            require(math.isfinite(value),"nonfinite JSON number")
        elif type(value) is dict:
            for child in value.values():finite(child)
        elif type(value) is list:
            for child in value:finite(child)
    finite(result)
    return result

def physical(path):
    p=Path(path).absolute()
    require(".." not in p.parts,"parent traversal")
    for node in (p,*p.parents):
        info=node.lstat()
        require(not stat.S_ISLNK(info.st_mode) and not getattr(info,"st_file_attributes",0)&0x400,
                "symlink/reparse path")
    return p.resolve(strict=True)

def read_regular(path, maximum=MAX_FILE):
    p=physical(path)
    def stamp(info):
        return [info.st_dev,info.st_ino,info.st_size,info.st_mtime_ns,info.st_ctime_ns]
    before=p.lstat()
    require(stat.S_ISREG(before.st_mode) and before.st_nlink==1 and before.st_size<=maximum,
            "regular unique bounded file required")
    with p.open("rb") as stream:
        opened=os.fstat(stream.fileno())
        require(stamp(opened)==stamp(before),"file replaced before opening")
        raw=stream.read(maximum+1)
        after=os.fstat(stream.fileno())
    current=p.lstat()
    require(len(raw)<=maximum and stamp(before)==stamp(after)==stamp(current),"file changed during read")
    return raw,{"path":str(p),"bytes":len(raw),"sha256":digest(raw),"physical":stamp(current)}

def fingerprint(path):
    return read_regular(path)[1]

def read_document(path, maximum=MAX_DOCUMENT):
    return parse_document(read_regular(path,maximum)[0],maximum)

def save(path,value):
    raw=value if type(value) is bytes else canonical(value)
    with Path(path).open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())

def check_fresh(preparation,wall_ns=None,mono_ns=None):
    wall_ns=time.time_ns() if wall_ns is None else wall_ns
    mono_ns=time.perf_counter_ns() if mono_ns is None else mono_ns
    names=("issued_wall_ns","issued_mono_ns","expires_wall_ns","expires_mono_ns")
    require(all(type(preparation.get(k)) is int and preparation[k]>0 for k in names),"clock fields")
    require(type(wall_ns) is int and type(mono_ns) is int,"clock observation types")
    iw,im,ew,em=(preparation[k] for k in names)
    require(ew-iw==em-im==HOLD_SECONDS*1000000000,"immutable freshness interval")
    require(iw<=wall_ns<ew and im<=mono_ns<em,"preparation expired or clock moved backwards")
    require(abs((wall_ns-iw)-(mono_ns-im))<=30000000000,"wall/monotonic clock divergence")

def exact(value,expected,reason):
    require(canonical(value)==canonical(expected),reason)

def hex_value(value,n):
    return type(value) is str and re.fullmatch("[0-9a-f]{"+str(n)+"}",value) is not None

def validate_go(preparation,review,go):
    common={k:preparation[k] for k in ("run_id","attempt","workflow_commit","source_commit",
                                      "source_tree","bindings_sha256")}
    expected_review={"schema":"dg18.windows10.host-review.v1","reviewer":REVIEWER,
                     "independent":True,"verdict":"PASS","findings":[],
                     "preparation_sha256":digest(canonical(preparation)),
                     "original_acceptance":False,**common}
    exact(review,expected_review,"independent exact host review required")
    require(hex_value(go.get("resource_receipt_sha256"),64) and hex_value(go.get("candidate_seal_sha256"),64),
            "actual candidate/resource receipt bindings required")
    expected_go={"schema":"dg18.windows10.root-go.v1","root_author":"/root","decision":"GO_ONCE",
                 "owner_continuation_sha256":OWNER_SHA256,"nonce":preparation["nonce"],
                 "preparation_sha256":digest(canonical(preparation)),
                 "review_sha256":digest(canonical(review)),
                 "candidate_seal_sha256":go["candidate_seal_sha256"],
                 "resource_receipt_sha256":go["resource_receipt_sha256"],
                 "resources_rechecked":True,"native_campaigns":1,"inference":False,"replay":False,
                 "automatic_retry":False,"original_acceptance":False,"original_limits":LIMITS,**common}
    exact(go,expected_go,"exact root one-shot GO required")

def private_invocation(packet,hold,reference,consumed):
    require(type(reference) is str and re.fullmatch(
        r"https://github\.com/theislampill/IMPLEMENTAUDIT\.md/blob/[0-9a-f]{40}/windows10/[0-9]{1,20}/1/ROOT_GO\.json#sha256=[0-9a-f]{64}",
        reference) is not None,"external operation reference")
    packet=physical(packet);hold=physical(hold)
    require(read_regular(packet/"entitlement-reference.txt",32)[0]==b"UNGRANTED\n","sealed entitlement changed")
    save(hold/"CONSUMED.json",consumed)
    invocation=hold/"private-invocation"
    invocation.mkdir(exist_ok=False)
    for name in ("prepare_and_execute.py","native_checks.py","SOURCE_MANIFEST.json"):
        save(invocation/name,read_regular(packet/name)[0])
    save(invocation/"entitlement-reference.txt",(reference+"\n").encode())
    return invocation

def failure_result(preparation,consumed,phase="UNKNOWN",error_class="UNSPECIFIED",predicate_sha256=None):
    require(type(consumed) is bool,"consumption type")
    return {"schema":"dg18.windows10.admission-result.v1","status":"ADMISSION_FAILURE",
            "run_id":preparation["run_id"],"attempt":preparation["attempt"],
            "preparation_sha256":digest(canonical(preparation)),
            "bindings_sha256":preparation["bindings_sha256"],"consumed":consumed,
            "effect_reach":"UNKNOWN" if consumed else "NOT_DISPATCHED",
            "outer_job_complete":False,"cleanup_complete":False,"adapter_exit_code":None,
            "outer_measurement_sha256":None,"phase":phase,"error_class":error_class,
            "predicate_sha256":predicate_sha256,
            "original_acceptance":False,"automatic_retry":False}

def project_result(preparation,result,consumed):
    expected=failure_result(preparation,consumed)
    require(set(result)==set(expected),"public result field population")
    require(type(result["phase"]) is str and result["phase"] in PHASES,"public phase vocabulary")
    for key in ("schema","run_id","attempt","preparation_sha256","bindings_sha256","consumed",
                "original_acceptance","automatic_retry"):
        exact({"v":result[key]},{"v":expected[key]},"public result request/type binding")
    require(type(result["outer_job_complete"]) is bool and type(result["cleanup_complete"]) is bool,
            "public completion types")
    if result["status"]=="ADMISSION_FAILURE":
        require(type(result["error_class"]) is str and result["error_class"] in ERROR_CLASSES,"public failure class")
        require(hex_value(result["predicate_sha256"],64) if result["error_class"]=="PREDICATE_REFUSED"
                else result["predicate_sha256"] is None,"public predicate fingerprint")
        expected=failure_result(preparation,consumed,result["phase"],result["error_class"],result["predicate_sha256"])
        exact(result,expected,"failure projection must preserve uncertainty")
    else:
        require(result["status"] in ("ADAPTER_RETURNED","ADAPTER_FAILED") and consumed is True,
                "unrecognized terminal outcome")
        require(result["effect_reach"]=="STARTED" and result["outer_job_complete"] is True
                and result["cleanup_complete"] is True,"terminal containment not established")
        require(result["phase"]=="TERMINAL_RECORD" and result["error_class"] is None
                and result["predicate_sha256"] is None and hex_value(result["outer_measurement_sha256"],64),
                "terminal measurement identity required")
        code=result["adapter_exit_code"]
        require(type(code) is int and 0<=code<=4294967295,"terminal exit code")
        require((code==0)==(result["status"]=="ADAPTER_RETURNED"),"terminal outcome contradicts exit")
    return result

def classify_failure(exc):
    if type(exc) is Refusal:
        return {"error_class":"PREDICATE_REFUSED","predicate_sha256":digest(str(exc).encode("utf-8"))}
    if isinstance(exc,subprocess.TimeoutExpired):name="GIT_TIMEOUT"
    elif isinstance(exc,OSError):name="FILE_IO_FAILURE"
    elif type(exc).__name__=="MeasurementError":name="JOB_MEASUREMENT_FAILURE"
    else:name="UNEXPECTED_FAILURE"
    return {"error_class":name,"predicate_sha256":None}

def mark_phase(paths,name):
    global CURRENT_PHASE
    require(name in PHASES,"phase vocabulary")
    CURRENT_PHASE=name
    target=paths["hold"]/"PHASE.json"
    if target.exists():read_regular(target,MAX_DOCUMENT)
    next_path=paths["hold"]/"PHASE.next.json"
    save(next_path,{"schema":"dg18.windows10.phase.v1","phase":name,"hold_name":paths["hold"].name})
    os.replace(next_path,target)

def campaign_command(state,paths):
    return [state["context"]["python"],"-I","-X","utf8","-B",
            str(paths["hold"]/"private-invocation/prepare_and_execute.py"),
            "--source",str(paths["source"]),"--python",state["context"]["python"],"--output",str(paths["out"])]

def check_measurement(result,raw,command,cwd):
    require(digest(raw)==result["outer_measurement_sha256"],"retained outer measurement digest differs")
    record=parse_document(raw,MAX_MEASUREMENT)
    require(record.get("status")=="COMPLETE_UNADMITTED" and record.get("complete_memory_scope_valid") is True
            and record.get("cleanup_complete") is True and type(record.get("exit_code")) is int
            and record["exit_code"]==result["adapter_exit_code"],"retained outer measurement incomplete")
    exact(record.get("command"),command,"retained outer command differs")
    require(record.get("cwd")==cwd,"retained outer working directory differs")
    return record

def host_context():
    require(os.name=="nt" and sys.platform=="win32","actual Windows required before allocation")
    require(sys.implementation.name=="cpython" and sys.version_info[:3]==(3,12,10)
            and sys.maxsize==2**63-1,"physical CPython3.12.10 x64 required")
    fixed={"GITHUB_ACTIONS":"true","GITHUB_REPOSITORY":REPOSITORY,"GITHUB_EVENT_NAME":"push",
           "GITHUB_REF":"refs/heads/"+BRANCH,"GITHUB_RUN_ATTEMPT":"1","RUNNER_OS":"Windows",
           "RUNNER_ARCH":"X64","RUNNER_ENVIRONMENT":"github-hosted"}
    require(all(os.environ.get(k)==v for k,v in fixed.items()),"exact hosted workflow context required")
    run=os.environ.get("GITHUB_RUN_ID","");commit=os.environ.get("GITHUB_SHA","")
    require(re.fullmatch("[0-9]{1,20}",run) and hex_value(commit,40),"workflow/run identity")
    selected=physical(os.environ.get("DG18_PHYSICAL_PYTHON",""))
    require(selected.samefile(sys.executable),"running interpreter differs from selected physical Python")
    return {"run_id":run,"attempt":"1","workflow_commit":commit,"python":str(selected),
            "workspace":str(physical(os.environ["GITHUB_WORKSPACE"])),
            "temp":str(physical(os.environ["RUNNER_TEMP"]))}


def child_environment(state,paths):
    ctx=state["context"];python=Path(ctx["python"])
    git=Path(state["bindings"]["tools"]["git"]["path"]);git_root=git.parents[2]
    system=Path(os.environ.get("SystemRoot",r"C:\Windows"))
    env={"SystemRoot":str(system),"WINDIR":str(system),"ProgramFiles":str(Path(BASH).parents[2]),
         "PATHEXT":".COM;.EXE;.BAT;.CMD","PATH":os.pathsep.join(
             [str(python.parent),str(git.parent),str(git_root/"cmd"),str(git_root/"bin"),
              str(git_root/"usr/bin"),str(system/"System32")]),
         "TEMP":str(paths["hold"]/"tmp"),"TMP":str(paths["hold"]/"tmp"),
         "GIT_CONFIG_NOSYSTEM":"1","GIT_CONFIG_SYSTEM":os.devnull,
         "GIT_CONFIG_GLOBAL":os.devnull,"GIT_OPTIONAL_LOCKS":"0","GIT_TERMINAL_PROMPT":"0",
         "PYTHONDONTWRITEBYTECODE":"1","IMPLEMENTAUDIT_PYTHON":str(python),
         "LC_ALL":"C","LANG":"C","MSYS2_ARG_CONV_EXCL":"*",
         "GITHUB_ACTIONS":"true","GITHUB_REPOSITORY":REPOSITORY,"GITHUB_EVENT_NAME":"push",
         "GITHUB_REF":"refs/heads/"+BRANCH,"GITHUB_RUN_ATTEMPT":"1",
         "GITHUB_RUN_ID":ctx["run_id"],"GITHUB_SHA":ctx["workflow_commit"],
         "GITHUB_WORKSPACE":ctx["workspace"],"RUNNER_TEMP":ctx["temp"],
         "RUNNER_OS":"Windows","RUNNER_ARCH":"X64","RUNNER_ENVIRONMENT":"github-hosted",
         "DG18_PHYSICAL_PYTHON":str(python)}
    return env

def resolve_paths(ctx,source,packet):
    workspace=physical(ctx["workspace"]);temp=physical(ctx["temp"])
    source=physical(source);packet=physical(packet)
    require(source==physical(workspace/"qualified-source"),"source checkout path differs")
    require(packet==physical(workspace/"packet"/PREFIX),"qualification packet path differs")
    packet_repo=physical(workspace/"packet")
    require(not source.is_relative_to(packet_repo) and not packet_repo.is_relative_to(source),
            "source and packet must be separate")
    name=ctx["run_id"]+"-1"
    hold=temp/("dg18-iw10-hold-"+name);out=temp/("dg18-iw10-"+name)
    require(not any(hold.is_relative_to(p) or out.is_relative_to(p) for p in (source,packet_repo)),
            "hold/output must be separated")
    return {"source":source,"packet":packet,"packet_repo":packet_repo,
            "hold":hold,"out":out,"control":hold/"control.git"}

def discover_tools(ctx):
    git=next((Path(p) for p in GIT_CANDIDATES if Path(p).is_file()),None)
    require(git is not None,"allowlisted direct Git image unavailable")
    return {"python":fingerprint(ctx["python"]),"git":fingerprint(git),"bash":fingerprint(BASH)}

def ntfs(path):
    import ctypes as C
    from ctypes import wintypes as W
    kernel=C.WinDLL("kernel32",use_last_error=True)
    get_root=kernel.GetVolumePathNameW
    get_root.argtypes=(W.LPCWSTR,W.LPWSTR,W.DWORD);get_root.restype=W.BOOL
    get_volume=kernel.GetVolumeInformationW
    get_volume.argtypes=(W.LPCWSTR,W.LPWSTR,W.DWORD,C.POINTER(W.DWORD),C.POINTER(W.DWORD),
                         C.POINTER(W.DWORD),W.LPWSTR,W.DWORD);get_volume.restype=W.BOOL
    get_type=kernel.GetDriveTypeW;get_type.argtypes=(W.LPCWSTR,);get_type.restype=W.UINT
    root=C.create_unicode_buffer(32768);fs=C.create_unicode_buffer(64)
    serial=W.DWORD();component=W.DWORD();flags=W.DWORD()
    require(bool(get_root(str(physical(path)),root,len(root))),"volume root unavailable")
    require(bool(get_volume(root.value,None,0,C.byref(serial),C.byref(component),C.byref(flags),fs,len(fs))),
            "volume information unavailable")
    drive_type=int(get_type(root.value))
    require(fs.value=="NTFS" and drive_type==3,"fixed local NTFS volume required")
    return {"root":root.value,"filesystem":"NTFS","drive_type":drive_type,"serial":serial.value}

def run_git(state,paths,cwd,*arguments,maximum=2097152):
    git=state["bindings"]["tools"]["git"]
    exact(fingerprint(git["path"]),git,"held direct Git changed before invocation")
    command=[git["path"],"-c","credential.helper=","-c","core.hooksPath=NUL",
             "-c","gc.auto=0","-c","maintenance.auto=false","-c","init.templateDir=",
             "-C",str(cwd),*map(str,arguments)]
    result=subprocess.run(command,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,
                          stderr=subprocess.DEVNULL,env=child_environment(state,paths),timeout=30,check=False)
    require(result.returncode==0 and len(result.stdout)<=maximum,"bounded Git observation failed")
    return result.stdout

def git_tree(raw):
    result={}
    for record in raw.split(b"\0"):
        if not record:continue
        header,name=record.split(b"\t",1)
        mode,kind,oid=header.decode("ascii").split(" ")
        path=name.decode("utf-8")
        require(mode in ("100644","100755") and kind=="blob" and hex_value(oid,40),
                "unexpected tree leaf type")
        require(path and not path.startswith("/") and "\\" not in path and
                all(part not in ("",".","..") for part in path.split("/")) and path not in result,
                "unexpected tree path")
        result[path]={"mode":mode,"oid":oid}
    return result

def parents(raw):
    header=raw.split(b"\n\n",1)[0]
    values=[line[7:].decode("ascii") for line in header.splitlines() if line.startswith(b"parent ")]
    require(all(hex_value(v,40) for v in values),"invalid commit parent")
    return values

def blob(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()

def bind_snapshot(ctx,paths):
    require(not paths["out"].exists(),"Campaign output already exists")
    tools=discover_tools(ctx);probe={"context":ctx,"bindings":{"tools":tools}}
    code_path=paths["packet"]/"CODE_MANIFEST.json"
    code_raw,code_identity=read_regular(code_path,MAX_DOCUMENT)
    code_doc=parse_document(code_raw)
    require(set(code_doc)=={"schema","source_commit","source_tree","members"} and
            code_doc["schema"]=="dg18.windows10.code-manifest.v1" and
            code_doc["source_commit"]==SOURCE_COMMIT and code_doc["source_tree"]==SOURCE_TREE,
            "code manifest identity/schema")
    expected_paths={PREFIX+"/"+n for n in ("prepare_and_execute.py","native_checks.py","SOURCE_MANIFEST.json",
                                           "entitlement-reference.txt","held_admission.py")}|{WORKFLOW}
    rows=code_doc["members"]
    require(type(rows) is list and len(rows)==6 and {r.get("path") for r in rows}==expected_paths,
            "code manifest population")
    require({q.name for q in paths["packet"].iterdir()}==
            {"CODE_MANIFEST.json","prepare_and_execute.py","native_checks.py","SOURCE_MANIFEST.json",
             "entitlement-reference.txt","held_admission.py"},"packet directory population")
    code={};additions={}
    for row in rows:
        require(set(row)=={"path","bytes","sha256","git_blob_oid","mode"} and row["mode"]=="100644",
                "code manifest row schema")
        raw,identity=read_regular(paths["packet_repo"]/row["path"])
        require(type(row["bytes"]) is int and identity["bytes"]==row["bytes"] and
                identity["sha256"]==row["sha256"] and blob(raw)==row["git_blob_oid"],"code body differs")
        code[row["path"]]=identity
        additions[row["path"]]={"mode":"100644","oid":blob(raw)}
    require(read_regular(paths["packet"]/"entitlement-reference.txt",32)[0]==b"UNGRANTED\n",
            "sealed packet must remain UNGRANTED")
    manifest=read_document(paths["packet"]/"SOURCE_MANIFEST.json")
    require(manifest.get("source_commit")==SOURCE_COMMIT and manifest.get("source_tree")==SOURCE_TREE
            and manifest.get("schema")=="r5.windows-fresh-campaign-source-manifest.v1",
            "selected source identity/schema")
    selected=manifest.get("members")
    require(type(selected) is list and len(selected)==99 and
            len({row.get("path") for row in selected})==99,"selected source population")
    source_head=run_git(probe,paths,paths["source"],"rev-parse","HEAD").decode().strip()
    source_tree=run_git(probe,paths,paths["source"],"rev-parse","HEAD^{tree}").decode().strip()
    require(source_head==SOURCE_COMMIT and source_tree==SOURCE_TREE,"actual source commit/tree")
    packet_head=run_git(probe,paths,paths["packet_repo"],"rev-parse","HEAD").decode().strip()
    require(packet_head==ctx["workflow_commit"],"actual workflow commit")
    require(parents(run_git(probe,paths,paths["packet_repo"],"cat-file","commit","HEAD"))==[SOURCE_COMMIT],
            "workflow sole parent differs")
    for repo in (paths["source"],paths["packet_repo"]):
        require(run_git(probe,paths,repo,"status","--porcelain=v1","--untracked-files=all","--ignored")==b"",
                "checkout has tracked/untracked/ignored changes")
    base=git_tree(run_git(probe,paths,paths["source"],"ls-tree","-r","-z","HEAD"))
    require(len(base)==1759,"source tree population")
    packet_tree=git_tree(run_git(probe,paths,paths["packet_repo"],"ls-tree","-r","-z","HEAD"))
    additions[PREFIX+"/CODE_MANIFEST.json"]={"mode":"100644","oid":blob(code_raw)}
    require(not set(base)&set(additions) and packet_tree=={**base,**additions},
            "workflow tree must be exact source plus seven files")
    received={}
    for row in selected:
        require(set(row)=={"path","bytes","sha256","git_blob_oid","git_mode"},"selected source row schema")
        path=row["path"]
        require(path in base and base[path]=={"mode":row["git_mode"],"oid":row["git_blob_oid"]},
                "selected source row differs from actual Git tree")
        raw,identity=read_regular(paths["source"]/path)
        require(type(row["bytes"]) is int and len(raw)==row["bytes"] and digest(raw)==row["sha256"]
                and blob(raw)==row["git_blob_oid"],"selected source bytes differ")
        received[path]=identity
    require({p for p in base if p.startswith("skills/")}==
            {p for p in received if p.startswith("skills/")},"all skills closure differs")
    return {"context":ctx,"paths":{k:str(v) for k,v in paths.items()},
            "tools":tools,"code":code,"code_manifest":code_identity,"source":received,
            "base_tree":base,"packet_tree":packet_tree,
            "volumes":{k:ntfs(paths[k]) for k in ("source","packet_repo","hold")}}

def prepare(source,packet):
    import secrets
    ctx=host_context();paths=resolve_paths(ctx,source,packet)
    paths["hold"].mkdir(exist_ok=False)
    (paths["hold"]/"tmp").mkdir(exist_ok=False)
    mark_phase(paths,"PREPARE_BINDING")
    bindings=bind_snapshot(ctx,paths)
    iw=time.time_ns();im=time.perf_counter_ns()
    p={"schema":"dg18.windows10.preparation.v1","run_id":ctx["run_id"],"attempt":"1",
       "workflow_commit":ctx["workflow_commit"],"source_commit":SOURCE_COMMIT,"source_tree":SOURCE_TREE,
       "bindings_sha256":digest(canonical(bindings)),"nonce":secrets.token_hex(32),
       "issued_wall_ns":iw,"issued_mono_ns":im,"expires_wall_ns":iw+HOLD_SECONDS*1000000000,
       "expires_mono_ns":im+HOLD_SECONDS*1000000000,"native_started":False,"original_acceptance":False,
       "python_version":"3.12.10","python_architecture":"x64","platform":"Windows",
       "filesystems":["NTFS"],"source_members":99,"code_manifest_sha256":bindings["code_manifest"]["sha256"],
       "tools_sha256":{k:v["sha256"] for k,v in bindings["tools"].items()},
       "original_limits":LIMITS,"inference":False}
    state={"schema":"dg18.windows10.private-state.v1","context":ctx,"preparation":p,"bindings":bindings}
    require(len(canonical(state))<=MAX_STATE and len(canonical(p))<=MAX_DOCUMENT,"preparation record budget")
    save(paths["hold"]/"PRIVATE_STATE.json",state)
    save(paths["hold"]/"PREPARATION.json",p)
    mark_phase(paths,"PREPARATION_RECORDED")
    check_fresh(p)
    return p

def verify_held(state,paths):
    require(state.get("schema")=="dg18.windows10.private-state.v1","private state schema")
    p=state["preparation"];check_fresh(p)
    exact(host_context(),state["context"],"held workflow host context changed")
    exact(read_document(paths["hold"]/"PREPARATION.json"),p,"preparation file changed")
    require(digest(canonical(state["bindings"]))==p["bindings_sha256"],"private bindings changed")
    current=bind_snapshot(state["context"],paths)
    exact(current,state["bindings"],"physical tools/source/code/tree changed during hold")
    check_fresh(p)

def remote_head(state,paths):
    ref="refs/heads/"+CONTROL_BRANCH
    raw=run_git(state,paths,paths["hold"],"ls-remote","--heads",
                "https://github.com/"+REPOSITORY+".git",ref,maximum=256)
    if not raw:return None
    fields=raw.decode("ascii").strip().split()
    require(len(fields)==2 and hex_value(fields[0],40) and fields[1]==ref,"control reference population")
    return fields[0]

def check_control_tree(base,tree,commit_parents,run_id):
    require(commit_parents==[SOURCE_COMMIT],"control sole parent")
    prefix="windows10/"+run_id+"/1/"
    require(all(tree.get(k)==v for k,v in base.items()),"control changed the base source")
    added=set(tree)-set(base)
    go={prefix+n for n in ("PREPARATION.json","HOST_REVIEW.json","ROOT_GO.json")}
    stop={prefix+"STOP.json"}
    require(added in (go,stop),"control file population/request")
    require(all(tree[k]["mode"]=="100644" and hex_value(tree[k]["oid"],40) for k in added),
            "control file mode/identity")
    return "GO" if added==go else "STOP"

def check_control_records(preparation,documents):
    require(set(documents)=={"PREPARATION.json","HOST_REVIEW.json","ROOT_GO.json"},"control document population")
    exact(parse_document(documents["PREPARATION.json"]),preparation,"control preparation differs")
    review=parse_document(documents["HOST_REVIEW.json"]);go=parse_document(documents["ROOT_GO.json"])
    validate_go(preparation,review,go)
    return review,go

def load_job(state,paths):
    from types import SimpleNamespace
    path=paths["source"]/"scripts/r0039-windows-job.py"
    raw,identity=read_regular(path)
    exact(identity,state["bindings"]["source"]["scripts/r0039-windows-job.py"],"outer Job helper changed")
    namespace={"__name__":"dg18_windows10_outer_job","__file__":str(path),"__package__":None}
    exec(compile(raw,str(path),"exec"),namespace)
    return SimpleNamespace(measure=namespace["measure"])

def dispatch(state,paths,commit,review,go):
    require(not (paths["hold"]/"CONSUMED.json").exists(),"grant already consumed")
    p=state["preparation"];check_fresh(p)
    require(hex_value(commit,40),"control commit identity")
    mark_phase(paths,"GO_VALIDATION")
    verify_held(state,paths)
    validate_go(p,review,go)
    require(remote_head(state,paths)==commit,"control reference changed")
    check_fresh(p)
    require(not (paths["hold"]/"CONSUMED.json").exists(),"grant already consumed")
    save(paths["hold"]/"HOST_REVIEW.json",review)
    save(paths["hold"]/"ROOT_GO.json",go)
    consumed={"schema":"dg18.windows10.consumed.v1","run_id":p["run_id"],"attempt":"1",
              "workflow_commit":p["workflow_commit"],"preparation_sha256":digest(canonical(p)),
              "GO_sha256":digest(canonical(go)),"control_commit":commit,"nonce":p["nonce"],
              "automatic_retry":False}
    ref="https://github.com/"+REPOSITORY+"/blob/"+commit+"/windows10/"+p["run_id"]+"/1/ROOT_GO.json#sha256="+consumed["GO_sha256"]
    mark_phase(paths,"GRANT_CONSUMPTION")
    invocation=private_invocation(paths["packet"],paths["hold"],ref,consumed)
    mark_phase(paths,"PRIVATE_INVOCATION")
    for name in ("prepare_and_execute.py","native_checks.py","SOURCE_MANIFEST.json"):
        raw,_=read_regular(invocation/name);expected=state["bindings"]["code"][PREFIX+"/"+name]
        require(len(raw)==expected["bytes"] and digest(raw)==expected["sha256"],"private invocation bytes differ")
    save(paths["hold"]/"INVOCATION.json",{"command_scope":"ONE_ACCEPTED_CAMPAIGN","entitlement_reference":ref,
                                         "consumed":consumed,"original_limits":LIMITS})
    mark_phase(paths,"FINAL_RECHECK")
    verify_held(state,paths)
    check_fresh(p)
    job=load_job(state,paths)
    check_fresh(p)
    command=campaign_command(state,paths)
    environment=child_environment(state,paths)
    mark_phase(paths,"OUTER_JOB")
    check_fresh(p)
    record=job.measure(command,paths["hold"],environment,paths["hold"]/"outer-job",
                       diagnostic_timeout_seconds=OUTER_COMPLETION_SECONDS)
    require(record.get("status")=="COMPLETE_UNADMITTED" and record.get("complete_memory_scope_valid") is True
            and record.get("cleanup_complete") is True and type(record.get("exit_code")) is int,
            "outer Job terminal census/cleanup not established")
    result=failure_result(p,True)
    raw=read_regular(paths["hold"]/"outer-job/measurement.json",MAX_MEASUREMENT)[0]
    result.update(status="ADAPTER_RETURNED" if record["exit_code"]==0 else "ADAPTER_FAILED",
                  effect_reach="STARTED",outer_job_complete=True,cleanup_complete=True,
                  adapter_exit_code=record["exit_code"],outer_measurement_sha256=digest(raw),
                  phase="TERMINAL_RECORD",error_class=None,predicate_sha256=None)
    exact(check_measurement(result,raw,command,str(paths["hold"])),record,"returned/stored outer measurement differs")
    project_result(p,result,True)
    mark_phase(paths,"TERMINAL_RECORD")
    save(paths["hold"]/"ADMISSION_RESULT.json",result)
    return result

def wait_and_dispatch(source,packet):
    ctx=host_context();paths=resolve_paths(ctx,source,packet)
    state=read_document(paths["hold"]/"PRIVATE_STATE.json",MAX_STATE)
    mark_phase(paths,"WAIT_START")
    verify_held(state,paths);p=state["preparation"]
    require(not paths["control"].exists() and not (paths["hold"]/"CONSUMED.json").exists(),"wait episode already allocated")
    run_git(state,paths,paths["hold"],"init","--bare",str(paths["control"]))
    while True:
        mark_phase(paths,"CONTROL_POLL")
        check_fresh(p);commit=remote_head(state,paths);check_fresh(p)
        if commit is None:
            time.sleep(min(15,max(0.01,(p["expires_mono_ns"]-time.perf_counter_ns())/1000000000)))
            continue
        mark_phase(paths,"CONTROL_FETCH")
        run_git(state,paths,paths["control"],"fetch","--filter=blob:none","--no-tags","--depth=1",
                "https://github.com/"+REPOSITORY+".git","refs/heads/"+CONTROL_BRANCH)
        check_fresh(p)
        fetched=run_git(state,paths,paths["control"],"rev-parse","FETCH_HEAD").decode().strip()
        require(fetched==commit,"control changed during fetch")
        tree=git_tree(run_git(state,paths,paths["control"],"ls-tree","-r","-z",commit))
        parent=parents(run_git(state,paths,paths["control"],"cat-file","commit",commit))
        mode=check_control_tree(state["bindings"]["base_tree"],tree,parent,p["run_id"])
        prefix="windows10/"+p["run_id"]+"/1/"
        if mode=="STOP":
            stop=parse_document(run_git(state,paths,paths["control"],"show",commit+":"+prefix+"STOP.json",maximum=MAX_DOCUMENT))
            exact(stop,{"schema":"dg18.windows10.stop.v1","decision":"STOP","root_author":"/root",
                        "run_id":p["run_id"],"attempt":"1","preparation_sha256":digest(canonical(p))},
                  "stop request identity")
            save(paths["hold"]/"STOP_RECEIVED.json",stop)
            raise Refusal("root STOP received")
        names=("PREPARATION.json","HOST_REVIEW.json","ROOT_GO.json")
        mark_phase(paths,"CONTROL_RECEIVE")
        documents={n:run_git(state,paths,paths["control"],"show",commit+":"+prefix+n,maximum=MAX_DOCUMENT) for n in names}
        review,go=check_control_records(p,documents)
        return dispatch(state,paths,commit,review,go)

def export_result(source,packet):
    ctx=host_context();paths=resolve_paths(ctx,source,packet);hold=physical(paths["hold"])
    target=hold/"public-admission"
    require(not target.exists(),"admission export already attempted")
    failure={"phase":"UNKNOWN","error_class":"UNSPECIFIED","predicate_sha256":None}
    if (hold/"FAILURE_CONTEXT.json").exists():
        observed=read_document(hold/"FAILURE_CONTEXT.json")
        require(set(observed)=={"schema","run_id","attempt","workflow_commit","phase","error_class","predicate_sha256"}
                and observed["schema"]=="dg18.windows10.failure-context.v1"
                and observed["run_id"]==ctx["run_id"] and observed["attempt"]=="1"
                and observed["workflow_commit"]==ctx["workflow_commit"],"failure context request/schema")
        require(type(observed["phase"]) is str and observed["phase"] in PHASES
                and type(observed["error_class"]) is str and observed["error_class"] in ERROR_CLASSES,
                "failure context vocabulary")
        require(hex_value(observed["predicate_sha256"],64) if observed["error_class"]=="PREDICATE_REFUSED"
                else observed["predicate_sha256"] is None,"failure context predicate fingerprint")
        failure={k:observed[k] for k in failure}
    if (hold/"PREPARATION.json").exists():
        p=read_document(hold/"PREPARATION.json")
        require(p.get("run_id")==ctx["run_id"] and p.get("attempt")=="1" and
                p.get("workflow_commit")==ctx["workflow_commit"] and p.get("source_commit")==SOURCE_COMMIT
                and p.get("source_tree")==SOURCE_TREE,"export preparation request")
        consumed=(hold/"CONSUMED.json").exists()
        if consumed:
            c=read_document(hold/"CONSUMED.json");go=read_document(hold/"ROOT_GO.json")
            require(c.get("preparation_sha256")==digest(canonical(p)) and c.get("GO_sha256")==digest(canonical(go))
                    and c.get("run_id")==p["run_id"] and c.get("workflow_commit")==p["workflow_commit"],
                    "export consumption binding")
        result=read_document(hold/"ADMISSION_RESULT.json") if (hold/"ADMISSION_RESULT.json").exists() else failure_result(p,consumed,**failure)
        result=project_result(p,result,consumed)
        if result["status"] in ("ADAPTER_RETURNED","ADAPTER_FAILED"):
            state=read_document(hold/"PRIVATE_STATE.json",MAX_STATE)
            exact(state["context"],ctx,"terminal export host context differs")
            exact(state["preparation"],p,"terminal export preparation differs")
            require(digest(canonical(state["bindings"]))==p["bindings_sha256"],"terminal export bindings differ")
            raw=read_regular(hold/"outer-job/measurement.json",MAX_MEASUREMENT)[0]
            check_measurement(result,raw,campaign_command(state,paths),str(hold))
    else:
        result={"schema":"dg18.windows10.preparation-refusal.v1","run_id":ctx["run_id"],"attempt":"1",
                "workflow_commit":ctx["workflow_commit"],"source_commit":SOURCE_COMMIT,"source_tree":SOURCE_TREE,
                "status":"PREPARATION_NOT_ESTABLISHED","effect_reach":"UNKNOWN",
                "original_acceptance":False,"automatic_retry":False,**failure}
    target.mkdir(exist_ok=False);save(target/"ADMISSION.json",result)
    return result

def retain_failure(source,packet):
    observed_exception=sys.exception()
    try:
        ctx=host_context();paths=resolve_paths(ctx,source,packet)
        if paths["hold"].is_dir():
            if not (paths["hold"]/"PRIVATE_EXCEPTION.txt").exists():
                save(paths["hold"]/"PRIVATE_EXCEPTION.txt",traceback.format_exc().encode("utf-8"))
            failure={"phase":CURRENT_PHASE,**classify_failure(observed_exception)}
            if not (paths["hold"]/"FAILURE_CONTEXT.json").exists():
                save(paths["hold"]/"FAILURE_CONTEXT.json",{"schema":"dg18.windows10.failure-context.v1",
                     "run_id":ctx["run_id"],"attempt":"1","workflow_commit":ctx["workflow_commit"],**failure})
            if (paths["hold"]/"PREPARATION.json").exists() and not (paths["hold"]/"ADMISSION_RESULT.json").exists():
                p=read_document(paths["hold"]/"PREPARATION.json")
                save(paths["hold"]/"ADMISSION_RESULT.json",failure_result(p,(paths["hold"]/"CONSUMED.json").exists(),**failure))
    except BaseException:
        pass

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("action",choices=("prepare","wait","export"))
    parser.add_argument("--source",type=Path,required=True)
    args=parser.parse_args();packet=Path(__file__).resolve().parent
    try:
        if args.action=="prepare":
            prepare(args.source,packet);print("DG18_WINDOWS10_PREPARED")
        elif args.action=="wait":
            result=wait_and_dispatch(args.source,packet)
            print("DG18_WINDOWS10_ADAPTER_RECORDED")
            if result["adapter_exit_code"]!=0:return 1
        else:
            export_result(args.source,packet);print("DG18_WINDOWS10_ADMISSION_EXPORTED")
        return 0
    except BaseException:
        retain_failure(args.source,packet)
        print("DG18_WINDOWS10_REFUSED")
        return 1

if __name__=="__main__":
    raise SystemExit(main())
