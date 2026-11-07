#!/usr/bin/env python3
"""Windows20 request-bound preparation and one-shot admission. No inherent grant.

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
BRANCH = "pro/dg18-isolated-windows20-20261107"
CONTROL_BRANCH = "pro/dg18-isolated-windows20-control-20261107"
PREFIX = "qualification/dg18-isolated-windows20"
WORKFLOW = ".github/workflows/dg18-isolated-windows20.yml"
REVIEWER = "/root/windows10_review"
HOLD_SECONDS = 1200
OUTER_COMPLETION_SECONDS = 1200
MAX_DOCUMENT = 65536
MAX_STATE = 1048576
MAX_FILE = 33554432
MAX_MEASUREMENT = 16777216
PHASES = frozenset(("UNKNOWN","PREPARE_CUSTODY","PREPARE_BINDING","PREPARATION_RECORDED","WAIT_START",
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

# Closed shape metadata only. These constants grant no source or native authority.
SHAPE_CONDITIONS=("REGULAR_FILE","UNIQUE_LINK","NONNEGATIVE_SIZE","WITHIN_EXISTING_BOUND","NONREPARSE")
SHAPE_STAGES=("PATH_BEFORE","HANDLE_OPEN","HANDLE_AFTER","PATH_AFTER")
SHAPE_ROLES={"TOOL_PYTHON":None,"TOOL_GIT":None,"TOOL_BASH":None,
             "CODE_MANIFEST":None,"CODE_MEMBER":6,"SOURCE_MANIFEST":None,
             "SEALED_ENTITLEMENT":None,"SELECTED_SOURCE":99,
             "CONTROL_RECORD":None,"INTERNAL_RECORD":None}
SHAPE_SOURCE_MANIFEST_SHA256="c45268bda9879ad04a961565e6bb57ddf0ab197a17e4324da63d367b94ac8b64"
SHAPE_MAX_BYTES=4096
DIAGNOSTIC_WRAPPER_SHA256=None

def shape_codebook():
    return {"schema":"dg18.windows20.shape-codebook.v1","conditions":list(SHAPE_CONDITIONS),
            "stages":list(SHAPE_STAGES),"roles":SHAPE_ROLES,
            "manifest_index":"ZERO_BASED_IN_EXACT_PUBLIC_MANIFEST",
            "source_manifest_sha256":SHAPE_SOURCE_MANIFEST_SHA256,
            "source_commit":SOURCE_COMMIT,"source_tree":SOURCE_TREE,
            "diagnostic_bytes":SHAPE_MAX_BYTES,"authority":"NONE"}

def validate_shape_selector(role,manifest_index):
    require(type(role) is str and role in SHAPE_ROLES,"shape caller role")
    count=SHAPE_ROLES[role]
    require(manifest_index is None if count is None else
            type(manifest_index) is int and 0<=manifest_index<count,"shape manifest index")

def validate_shape_observation(value,error_class,predicate_sha256):
    predicates={digest(("read_regular:"+stage+":file_shape").encode("ascii")):stage
                for stage in SHAPE_STAGES}
    if value is None:
        require(predicate_sha256 not in predicates,"shape observation required")
        return None
    require(error_class=="PREDICATE_REFUSED" and predicate_sha256 in predicates,
            "shape predicate classification")
    require(type(value) is dict and set(value)=={"schema","stage","role","manifest_index","conditions"}
            and value["schema"]=="dg18.windows20.file-shape-observation.v1","shape observation schema")
    require(type(value["stage"]) is str and value["stage"]==predicates[predicate_sha256],
            "shape stage/predicate binding")
    validate_shape_selector(value["role"],value["manifest_index"])
    conditions=value["conditions"]
    require(type(conditions) is dict and set(conditions)==set(SHAPE_CONDITIONS)
            and all(type(conditions[k]) is bool for k in SHAPE_CONDITIONS),"shape Boolean population")
    require(not all(conditions.values()),"shape failure conjunction")
    require(conditions["NONNEGATIVE_SIZE"] or conditions["WITHIN_EXISTING_BOUND"],
            "shape size predicate contradiction")
    return {"schema":value["schema"],"stage":value["stage"],"role":value["role"],
            "manifest_index":value["manifest_index"],"conditions":dict(conditions)}

def shape_binding(ctx,phase):
    require(type(ctx.get("run_id")) is str and re.fullmatch("[0-9]{1,20}",ctx["run_id"])
            and ctx.get("attempt")=="1" and hex_value(ctx.get("workflow_commit"),40),
            "shape request identity")
    require(type(phase) is str and phase in PHASES,"shape phase")
    require(hex_value(DIAGNOSTIC_WRAPPER_SHA256,64),"shape reviewed wrapper pin")
    return {"schema":"dg18.windows20.bound-shape-diagnostic.v1","run_id":ctx["run_id"],
            "attempt":"1","workflow_commit":ctx["workflow_commit"],
            "source_commit":SOURCE_COMMIT,"source_tree":SOURCE_TREE,"phase":phase,
            "wrapper_sha256":DIAGNOSTIC_WRAPPER_SHA256,
            "shape_codebook_sha256":digest(canonical(shape_codebook()))}

def bind_shape_observation(observation,ctx,phase,error_class,predicate_sha256):
    value=validate_shape_observation(observation,error_class,predicate_sha256)
    if value is None:return None
    result={**shape_binding(ctx,phase),"observation":value}
    require(len(canonical(result))<=SHAPE_MAX_BYTES,"shape diagnostic byte bound")
    return result

def validate_shape_diagnostic(value,ctx,phase,error_class,predicate_sha256):
    if value is None:
        validate_shape_observation(None,error_class,predicate_sha256)
        return None
    expected=shape_binding(ctx,phase)
    require(type(value) is dict and set(value)==set(expected)|{"observation"},
            "shape diagnostic field population")
    exact({k:value[k] for k in expected},expected,"shape diagnostic request/code binding")
    observation=validate_shape_observation(value["observation"],error_class,predicate_sha256)
    require(observation is not None,"shape diagnostic observation absent")
    result={**expected,"observation":observation}
    require(len(canonical(result))<=SHAPE_MAX_BYTES,"shape diagnostic byte bound")
    return result

# Closed observation at the existing staged-copy refusal; never an admission grant.
STAGED_COPY_CALLS=("KERNEL_FIRST","KERNEL_PARTIAL","INSTALLED")
STAGED_COPY_PREDICATE_SHA256="420473a322b381abb751a722f5835cad4d157cea49514325504225ccb67b38cb"
STAGED_COPY_MAX_BYTES=2048

# Compare only the two immutable descriptors already captured by held snapshots.
PERMISSION_COMPONENT_FIELDS=(("OWNER",0x01),("GROUP",0x02),("DACL",0x04),
    ("LABEL",0x10),("ATTRIBUTE",0x20),("SCOPE",0x40))
PERMISSION_COMPONENT_CONTROLS=(("DACL_PRESENT",0x0004),("DACL_AUTO_INHERIT_REQ",0x0100),
    ("DACL_AUTO_INHERITED",0x0400),("DACL_PROTECTED",0x1000),("SACL_PRESENT",0x0010),
    ("SACL_AUTO_INHERIT_REQ",0x0200),("SACL_AUTO_INHERITED",0x0800),("SACL_PROTECTED",0x2000),("ALL",0xffff))
PERMISSION_COMPONENT_METHOD="CAPTURED_SDDL_STRINGS_AND_CONTROL_BITS"

# Invocation-owned observer failure data. No raw exception is published.
PERMISSION_OBSERVER_LAYOUT={
    "OBSERVER_CALL":"EMPTY","CAPTURED_INPUT":"EMPTY","CONTROL_BIND":"EMPTY",
    "CONTROL_BUFFER":"CONTROL_SIDE","CONTROL_CALL":"CONTROL_SIDE","CONTROL_FORMAT":"CONTROL_SIDE",
    "CONTROL_COMPARE":"CONTROL_RESULT","FIELD_CALL":"FIELD_SIDE","FIELD_INPUT":"FIELD_SIDE",
    "STRING_BUFFER":"FIELD_SIDE","STRING_CALL":"FIELD_SIDE","STRING_BOUND":"FIELD_SIDE",
    "STRING_SCAN":"FIELD_SIDE","STRING_READ":"FIELD_SIDE","STRING_VALUE":"FIELD_SIDE",
    "STRING_FREE":"FIELD_SIDE","FIELD_COMPARE":"FIELD_COMPARE",
    "RESULT_VALIDATE":"COMPLETE","RESULT_RECEIVE":"COMPLETE"}
PERMISSION_OBSERVER_API_ROWS=(
    ("CONTROL_CALL","GET_CONTROL","SECURITY",((87,"ERROR_INVALID_PARAMETER"),(1305,"ERROR_UNKNOWN_REVISION"))),
    ("STRING_CALL","CONVERT_SDDL","SECURITY_STRING",((87,"ERROR_INVALID_PARAMETER"),(1305,"ERROR_UNKNOWN_REVISION"),
        (1332,"ERROR_NONE_MAPPED"),(1336,"ERROR_INVALID_ACL"))),
    ("STRING_FREE","LOCAL_FREE","FREE_SECURITY",()))
PERMISSION_OBSERVER_PREDICATES={
    "DESCRIPTOR_BOUND":("permission component descriptor bound",("CAPTURED_INPUT","FIELD_INPUT")),
    "FIXED_FIELD":("permission component fixed field",("FIELD_INPUT",)),
    "CAPTURED_FORMAT":("permission component captured descriptor format",("CONTROL_FORMAT",)),
    "STRING_BOUND":("permission component string bound",("STRING_BOUND",)),
    "STRING_TERMINATION":("permission component string termination",("STRING_SCAN",)),
    "STRING_COMPLETE":("permission component complete string",("STRING_VALUE",)),
    "RESULT_SCHEMA":("permission component schema",("RESULT_VALIDATE","RESULT_RECEIVE")),
    "RESULT_METHOD":("permission component method",("RESULT_VALIDATE","RESULT_RECEIVE")),
    "RESULT_POPULATION":("permission component closed population",("RESULT_VALIDATE","RESULT_RECEIVE")),
    "RESULT_BOOLEAN":("permission component Boolean population",("RESULT_VALIDATE","RESULT_RECEIVE"))}

def permission_observer_codebook():
    return {"schema":"dg18.windows20.permission-observer-codebook.v1",
            "phases":dict(PERMISSION_OBSERVER_LAYOUT),"sides":["ORIGIN","STAGE"],
            "components":[name for name,mask in PERMISSION_COMPONENT_FIELDS],
            "apis":[{"phase":phase,"api":api,"operation":operation,"codes":{str(number):label for number,label in codes}}
                    for phase,api,operation,codes in PERMISSION_OBSERVER_API_ROWS],
            "other_native_code":"OTHER_RECORDED_CODE; VALID_EXISTING_INTEGER_ONLY",
            "predicates":{token:{"literal":reason,"sha256":digest(reason.encode()),"phases":list(phases)}
                          for token,(reason,phases) in PERMISSION_OBSERVER_PREDICATES.items()},
            "unavailable":None,"exception_ownership":"EXACT_ESCAPING_EXCEPTION_IN_THIS_TRACE",
            "partial_completion":"TWO_CONTROL_QUERIES_AND_FORMATS; BOTH_FIELD_STRINGS_AND_SUCCESSFUL_FREES",
            "prior_inner_fault_if_superseded":"NOT_RECONSTRUCTED; ESCAPING_FAILURE_ONLY",
            "additional_native_calls":0,"authority":"NONE"}

def validate_permission_observer_failure(value):
    if value is None:return None
    require(type(value) is dict and set(value)=={"schema","phase","component","side","error_class","api","code","predicate","partial"}
            and value["schema"]=="dg18.windows20.permission-observer-failure.v1","permission observer schema")
    phase=value["phase"];component=value["component"];side=value["side"]
    require(type(phase) is str and phase in PERMISSION_OBSERVER_LAYOUT,"permission observer phase")
    layout=PERMISSION_OBSERVER_LAYOUT[phase];names=[name for name,mask in PERMISSION_COMPONENT_FIELDS]
    if layout in ("FIELD_SIDE","FIELD_COMPARE"):
        require(type(component) is str and component in names,"permission observer component")
    else:require(component is None,"permission observer absent component")
    if layout in ("CONTROL_SIDE","FIELD_SIDE"):
        require(type(side) is str and side in ("ORIGIN","STAGE"),"permission observer side")
    else:require(side is None,"permission observer absent side")
    partial=value["partial"]
    require(type(partial) is dict and set(partial)=={"fields","controls"},"permission observer partial schema")
    for population,rows in (("fields",PERMISSION_COMPONENT_FIELDS),("controls",PERMISSION_COMPONENT_CONTROLS)):
        require(type(partial[population]) is dict and set(partial[population])=={name for name,mask in rows},
                "permission observer partial population")
        require(all(item is None or type(item) is bool for item in partial[population].values()),
                "permission observer partial Boolean or null")
    fields=partial["fields"];controls=partial["controls"]
    empty_controls=all(item is None for item in controls.values())
    complete_controls=all(type(item) is bool for item in controls.values())
    require(empty_controls or complete_controls,"permission observer complete control pair")
    if complete_controls and controls["ALL"]:
        require(all(controls.values()),"permission observer control consistency")
    if layout in ("EMPTY","CONTROL_SIDE"):
        require(empty_controls and all(item is None for item in fields.values()),"permission observer empty prefix")
    elif layout=="CONTROL_RESULT":
        require(all(item is None for item in fields.values()),"permission observer control prefix")
    elif layout in ("FIELD_SIDE","FIELD_COMPARE"):
        index=names.index(component)
        require(complete_controls and all(type(fields[name]) is bool if i<index else fields[name] is None
                for i,name in enumerate(names)),"permission observer field prefix")
    else:
        require(complete_controls and all(type(item) is bool for item in fields.values()),"permission observer complete prefix")
    kind=value["error_class"];api=value["api"];code=value["code"];predicate=value["predicate"]
    require(type(kind) is str and kind in ("API_REFUSED","PREDICATE_REFUSED","UNEXPECTED_FAILURE"),
            "permission observer error class")
    if kind=="API_REFUSED":
        rows=[row for row in PERMISSION_OBSERVER_API_ROWS if row[0]==phase]
        require(len(rows)==1 and type(api) is str and api==rows[0][1] and type(code) is str
                and code in {label for number,label in rows[0][3]}|{"OTHER_RECORDED_CODE"}
                and predicate is None,"permission observer API code binding")
    elif kind=="PREDICATE_REFUSED":
        require(api is None and code is None and type(predicate) is str and predicate in PERMISSION_OBSERVER_PREDICATES
                and phase in PERMISSION_OBSERVER_PREDICATES[predicate][1],"permission observer predicate binding")
    else:require(api is None and code is None and predicate is None,"permission observer unexpected payload")
    return {"schema":value["schema"],"phase":phase,"component":component,"side":side,"error_class":kind,
            "api":api,"code":code,"predicate":predicate,"partial":{"fields":dict(fields),"controls":dict(controls)}}

class PermissionObserverTrace:
    __slots__=("available","fields","controls","escaping","failure")
    def __init__(self):
        self.available=True
        self.fields={name:None for name,mask in PERMISSION_COMPONENT_FIELDS}
        self.controls={name:None for name,mask in PERMISSION_COMPONENT_CONTROLS}
        self.escaping=None;self.failure=None

def disable_permission_observer(observer):
    try:
        if type(observer) is PermissionObserverTrace:
            observer.available=False;observer.failure=None;observer.escaping=None
    except BaseException:pass

def permission_observer_controls(observer,values):
    if observer is None:return
    try:
        require(type(observer) is PermissionObserverTrace and observer.available is True,"permission observer owned trace")
        require(type(values) is dict and set(values)==set(observer.controls) and all(type(item) is bool for item in values.values())
                and all(item is None for item in observer.controls.values()),"permission observer control completion")
        observer.controls=dict(values)
    except BaseException:disable_permission_observer(observer)

def permission_observer_field(observer,name,value):
    if observer is None:return
    try:
        require(type(observer) is PermissionObserverTrace and observer.available is True,"permission observer owned trace")
        names=[field for field,mask in PERMISSION_COMPONENT_FIELDS]
        require(type(name) is str and name in names and type(value) is bool,"permission observer field completion")
        index=names.index(name)
        require(all(type(observer.fields[field]) is bool if i<index else observer.fields[field] is None
                    for i,field in enumerate(names)),"permission observer completion order")
        observer.fields[name]=value
    except BaseException:disable_permission_observer(observer)

def capture_permission_observer_failure(observer,error,phase,component=None,side=None):
    # Only trusted exact types have their existing bounded attributes inspected.
    try:
        if type(observer) is not PermissionObserverTrace or observer.available is not True:return
        if observer.escaping is error:return
        require(issubclass(type(error),BaseException),"permission observer exception object")
        kind="UNEXPECTED_FAILURE";api=None;code=None;predicate=None
        if type(error) is CustodyApiError:
            rows=[row for row in PERMISSION_OBSERVER_API_ROWS if row[0]==phase]
            require(len(rows)==1 and type(error.operation) is str and error.operation==rows[0][2]
                    and type(error.native_error) is int and 0<=error.native_error<=0xffffffff,
                    "permission observer trusted native error")
            kind="API_REFUSED";api=rows[0][1];code=dict(rows[0][3]).get(error.native_error,"OTHER_RECORDED_CODE")
        elif type(error) is Refusal:
            require(type(error.args) is tuple and len(error.args)==1 and type(error.args[0]) is str,
                    "permission observer trusted predicate")
            tokens=[token for token,(reason,phases) in PERMISSION_OBSERVER_PREDICATES.items()
                    if error.args[0]==reason and phase in phases]
            require(len(tokens)==1,"permission observer trusted predicate")
            kind="PREDICATE_REFUSED";predicate=tokens[0]
        value=validate_permission_observer_failure({"schema":"dg18.windows20.permission-observer-failure.v1",
            "phase":phase,"component":component,"side":side,"error_class":kind,"api":api,"code":code,"predicate":predicate,
            "partial":{"fields":dict(observer.fields),"controls":dict(observer.controls)}})
        observer.failure=value;observer.escaping=error
    except BaseException:disable_permission_observer(observer)

def receive_permission_observer_failure(observer,error):
    try:
        if type(observer) is not PermissionObserverTrace or observer.available is not True or observer.escaping is not error:return None
        return validate_permission_observer_failure(observer.failure)
    except BaseException:return None


def permission_component_codebook():
    return {"schema":"dg18.windows20.permission-component-codebook.v1",
            "method":PERMISSION_COMPONENT_METHOD,"fields":dict(PERMISSION_COMPONENT_FIELDS),
            "controls":dict(PERMISSION_COMPONENT_CONTROLS),"security_fields":0x77,
            "input":"EXACT_ALREADY_CAPTURED_ORIGIN_AND_WRITTEN_STAGE_DESCRIPTORS",
            "site":"AFTER_ORIGINAL_FULL_PERMISSION_GUARD_REFUSAL_ONLY",
            "descriptor_bytes":[20,65536],"allocated_WCHAR_capacity":[1,32768],
            "maximum_string_conversions":12,"maximum_control_queries":2,
            "unavailable":None,"all_equal_interpretation":"FULL_MISMATCH_UNCLASSIFIED",
            "comparison":"EXACT_SELECTED_STRINGS_AND_MASKED_CONTROL_BITS; NO_NORMALIZATION",
            "scope":"OBSERVATION_ONLY; NO_PERMISSION_REREAD_SETTER_OR_AUTHORITY",
            "failure_codebook_sha256":digest(canonical(permission_observer_codebook()))}

def validate_permission_components(value):
    if value is None:return None
    require(type(value) is dict and set(value)=={"schema","method","fields","controls"}
            and value["schema"]=="dg18.windows20.permission-components.v1","permission component schema")
    require(type(value["method"]) is str and value["method"]==PERMISSION_COMPONENT_METHOD,
            "permission component method")
    expected={"fields":PERMISSION_COMPONENT_FIELDS,"controls":PERMISSION_COMPONENT_CONTROLS}
    for population,rows in expected.items():
        require(type(value[population]) is dict and set(value[population])=={name for name,mask in rows},
                "permission component closed population")
        require(all(type(item) is bool for item in value[population].values()),"permission component Boolean population")
    return {"schema":value["schema"],"method":value["method"],
            "fields":dict(value["fields"]),"controls":dict(value["controls"])}

def staged_copy_codebook():
    return {"schema":"dg18.windows20.staged-copy-codebook.v1","callsites":list(STAGED_COPY_CALLS),
            "conditions":["copy_equal","permissions_equal"],"predicate_sha256":STAGED_COPY_PREDICATE_SHA256,
            "site":"WRITTEN_STAGE_SNAPSHOT_BEFORE_REOPEN_AND_RENAMES",
            "source_commit":SOURCE_COMMIT,"source_tree":SOURCE_TREE,
            "source_manifest_sha256":SHAPE_SOURCE_MANIFEST_SHA256,
            "diagnostic_bytes":STAGED_COPY_MAX_BYTES,"authority":"NONE",
            "permission_component_codebook_sha256":digest(canonical(permission_component_codebook()))}

def validate_staged_copy_observation(value,error_class,predicate_sha256):
    if value is None:
        require(predicate_sha256!=STAGED_COPY_PREDICATE_SHA256,"staged copy observation required")
        return None
    require(error_class=="PREDICATE_REFUSED" and predicate_sha256==STAGED_COPY_PREDICATE_SHA256,
            "staged copy predicate classification")
    require(type(value) is dict and set(value)=={"schema","callsite","copy_equal","permissions_equal","permission_components","permission_component_failure"}
            and value["schema"]=="dg18.windows20.staged-copy-observation.v1","staged copy observation schema")
    require(type(value["callsite"]) is str and value["callsite"] in STAGED_COPY_CALLS,"staged copy caller role")
    require(type(value["copy_equal"]) is bool and type(value["permissions_equal"]) is bool,
            "staged copy Boolean population")
    require(not(value["copy_equal"] and value["permissions_equal"]),"staged copy failure conjunction")
    components=validate_permission_components(value["permission_components"])
    require(components is None or value["permissions_equal"] is False,"permission component full mismatch gate")
    observer_failure=validate_permission_observer_failure(value["permission_component_failure"])
    require(observer_failure is None or (components is None and value["permissions_equal"] is False),
            "permission observer failure gate")
    return {"schema":value["schema"],"callsite":value["callsite"],
            "copy_equal":value["copy_equal"],"permissions_equal":value["permissions_equal"],
            "permission_components":components,"permission_component_failure":observer_failure}

def observe_staged_copy(callsite,stage_raw,raw,written,before):
    # A malformed diagnostic input stays unqualified; never synthesize false.
    if type(stage_raw) is not bytes or type(raw) is not bytes or type(written) is not dict or type(before) is not dict:
        return None
    left=written.get("permissions_sha256");right=before.get("permissions_sha256")
    if not hex_value(left,64) or not hex_value(right,64):return None
    value={"schema":"dg18.windows20.staged-copy-observation.v1","callsite":callsite,
           "copy_equal":stage_raw==raw,"permissions_equal":left==right,"permission_components":None,
           "permission_component_failure":None}
    return validate_staged_copy_observation(value,"PREDICATE_REFUSED",STAGED_COPY_PREDICATE_SHA256)

def staged_copy_binding(ctx,phase):
    require(type(ctx.get("run_id")) is str and re.fullmatch("[0-9]{1,20}",ctx["run_id"])
            and ctx.get("attempt")=="1" and hex_value(ctx.get("workflow_commit"),40),"staged copy request identity")
    require(type(phase) is str and phase=="PREPARE_CUSTODY","staged copy phase")
    require(hex_value(DIAGNOSTIC_WRAPPER_SHA256,64),"staged copy reviewed wrapper pin")
    return {"schema":"dg18.windows20.bound-staged-copy-diagnostic.v1","run_id":ctx["run_id"],
            "attempt":"1","workflow_commit":ctx["workflow_commit"],
            "source_commit":SOURCE_COMMIT,"source_tree":SOURCE_TREE,"phase":phase,
            "wrapper_sha256":DIAGNOSTIC_WRAPPER_SHA256,
            "staged_copy_codebook_sha256":digest(canonical(staged_copy_codebook()))}

def bind_staged_copy_observation(observation,ctx,phase,error_class,predicate_sha256):
    value=validate_staged_copy_observation(observation,error_class,predicate_sha256)
    if value is None:return None
    result={**staged_copy_binding(ctx,phase),"observation":value}
    require(len(canonical(result))<=STAGED_COPY_MAX_BYTES,"staged copy diagnostic byte bound")
    return result

def validate_staged_copy_diagnostic(value,ctx,phase,error_class,predicate_sha256):
    if value is None:
        validate_staged_copy_observation(None,error_class,predicate_sha256)
        return None
    expected=staged_copy_binding(ctx,phase)
    require(type(value) is dict and set(value)==set(expected)|{"observation"},"staged copy diagnostic fields")
    exact({key:value[key] for key in expected},expected,"staged copy diagnostic request/code binding")
    observation=validate_staged_copy_observation(value["observation"],error_class,predicate_sha256)
    require(observation is not None,"staged copy diagnostic observation absent")
    result={**expected,"observation":observation}
    require(len(canonical(result))<=STAGED_COPY_MAX_BYTES,"staged copy diagnostic byte bound")
    return result

def validate_staged_copy_custody(value,custody,preparation):
    if value is None:return
    require(preparation is None and type(custody) is dict and custody["method"]=="MATERIALIZED"
            and custody["status"]=="REFUSED" and custody["error_class"]=="PREDICATE_REFUSED"
            and custody["api_operation"] is None,"staged copy custody refusal")
    require(type(custody["selected_index"]) is int and custody["selected_index"] in (0,1)
            and len(custody["assessment"])==2,"staged copy custody selection")
    method,index=select_git_policy([{"index":row["index"],"status":row["status"]} for row in custody["assessment"]])
    require((method,index)==("MATERIALIZED",custody["selected_index"]),"staged copy custody selection binding")
    expected={name:False for name in CUSTODY_CHECKS};expected["selection_bound"]=True
    installed=value["observation"]["callsite"]=="INSTALLED"
    if installed:expected.update(kernel_controls_passed=True,origin_current=True,same_volume=True)
    require(custody["stage"]==("ORIGIN_LOCKED" if installed else "SELECTION"),"staged copy callsite checkpoint")
    exact(custody["checks"],expected,"staged copy custody checkpoint")

def validate_admission_export(value,ctx,preparation,consumed):
    require(type(value) is dict and "shape_diagnostic" in value and "custody_diagnostic" in value,"admission diagnostic member")
    require("staged_copy_diagnostic" in value,"staged copy admission member")
    base={k:v for k,v in value.items() if k not in ("shape_diagnostic","custody_diagnostic","staged_copy_diagnostic")}
    if preparation is None:
        expected={"schema":"dg18.windows20.preparation-refusal.v1","run_id":ctx["run_id"],"attempt":"1",
                  "workflow_commit":ctx["workflow_commit"],"source_commit":SOURCE_COMMIT,
                  "source_tree":SOURCE_TREE,"status":"PREPARATION_NOT_ESTABLISHED",
                  "effect_reach":"UNKNOWN","original_acceptance":False,"automatic_retry":False}
        require(set(base)==set(expected)|{"phase","error_class","predicate_sha256"},
                "preparation refusal field population")
        exact({k:base[k] for k in expected},expected,"preparation refusal request/type binding")
        require(type(base["phase"]) is str and base["phase"] in PHASES
                and type(base["error_class"]) is str and base["error_class"] in ERROR_CLASSES,
                "preparation refusal vocabulary")
        require(hex_value(base["predicate_sha256"],64) if base["error_class"]=="PREDICATE_REFUSED"
                else base["predicate_sha256"] is None,"preparation refusal predicate")
    else:
        base=project_result(preparation,base,consumed)
    diagnostic=validate_shape_diagnostic(value["shape_diagnostic"],ctx,base["phase"],
                                         base["error_class"],base["predicate_sha256"])
    custody=validate_custody_projection(value["custody_diagnostic"],ctx,
        required=preparation is not None or base["phase"]=="PREPARE_CUSTODY")
    if preparation is not None:
        require(custody is not None and custody["status"]=="ESTABLISHED","custody preparation admission required")
        exact(custody,preparation["git_custody"],"custody preparation/export binding")
    staged=validate_staged_copy_diagnostic(value["staged_copy_diagnostic"],ctx,base["phase"],
        base["error_class"],base["predicate_sha256"])
    validate_staged_copy_custody(staged,custody,preparation)
    result={**base,"shape_diagnostic":diagnostic,"custody_diagnostic":custody,"staged_copy_diagnostic":staged}
    require(len(canonical(result))<=MAX_DOCUMENT,"admission export document bound")
    return result


# Windows20 prospective file-custody primitives. No API runs on import.
from contextlib import contextmanager, ExitStack

class CustodyApiError(Refusal):
    def __init__(self, operation, code):
        self.operation=operation
        self.native_error=int(code)
        self.custody_error=("ACCESS_DENIED" if code in (5,1314) else
                            "SHARING_REFUSED" if code in (32,33) else
                            "NAME_COLLISION" if code in (80,183) else "API_REFUSED")
        super().__init__("custody API "+operation)

class WindowsCustody:
    """Actual Windows APIs; the hosted fixture gate qualifies these before tool mutation."""
    SECURITY_FIELDS=0x77  # owner, group, DACL, mandatory label, resource attributes, CAP
    def __init__(self):
        require(os.name=="nt" and sys.platform=="win32"
                and sys.implementation.name=="cpython" and sys.version_info[:3]==(3,12,10)
                and sys.maxsize==2**63-1,"custody exact Windows runtime")
        import ctypes as C
        self.C=C;self.K=C.WinDLL("kernel32",use_last_error=True);self.A=C.WinDLL("advapi32",use_last_error=True)
        D=C.c_uint32;H=C.c_void_p;P=C.c_void_p;B=C.c_int;S=C.c_wchar_p
        def api(dll,name,args,result):
            f=getattr(dll,name);f.argtypes=args;f.restype=result;return f
        self.create=api(self.K,"CreateFileW",(S,D,D,P,D,D,H),H)
        self.close=api(self.K,"CloseHandle",(H,),B)
        self.info=api(self.K,"GetFileInformationByHandleEx",(H,C.c_int,P,D),B)
        self.setinfo=api(self.K,"SetFileInformationByHandle",(H,C.c_int,P,D),B)
        self.filetype=api(self.K,"GetFileType",(H,),D)
        self.finalname=api(self.K,"GetFinalPathNameByHandleW",(H,P,D,D),D)
        self.seek=api(self.K,"SetFilePointerEx",(H,C.c_int64,P,D),B)
        self.read=api(self.K,"ReadFile",(H,P,D,C.POINTER(D),P),B)
        self.write=api(self.K,"WriteFile",(H,P,D,C.POINTER(D),P),B)
        self.flush=api(self.K,"FlushFileBuffers",(H,),B)
        self.security=api(self.A,"GetKernelObjectSecurity",(H,D,P,D,C.POINTER(D)),B)
        self.sddl=api(self.A,"ConvertSecurityDescriptorToStringSecurityDescriptorW",(P,D,D,C.POINTER(P),C.POINTER(D)),B)
        self.localfree=api(self.K,"LocalFree",(P,),P)
        class Basic(C.Structure):
            _fields_=[("creation",C.c_int64),("access",C.c_int64),("write",C.c_int64),
                      ("change",C.c_int64),("attributes",D)]
        class Standard(C.Structure):
            _fields_=[("allocation",C.c_int64),("size",C.c_int64),("links",D),
                      ("pending",C.c_ubyte),("directory",C.c_ubyte)]
        class Identity(C.Structure):
            _fields_=[("volume",C.c_uint64),("file_id",C.c_ubyte*16)]
        class Tag(C.Structure):
            _fields_=[("attributes",D),("tag",D)]
        class Rename(C.Structure):
            _fields_=[("replace",C.c_ubyte),("root",H),("length",D),("name",C.c_wchar*1)]
        class SecurityAttributes(C.Structure):
            _fields_=[("length",D),("descriptor",P),("inherit",B)]
        self.Basic=Basic;self.Standard=Standard;self.Identity=Identity;self.Tag=Tag
        self.Rename=Rename;self.SecurityAttributes=SecurityAttributes
        require(C.sizeof(H)==8 and C.sizeof(C.c_wchar)==2 and C.sizeof(Basic)==40
                and C.sizeof(Standard)==24 and C.sizeof(Identity)==24
                and Rename.name.offset==20 and C.sizeof(SecurityAttributes)==24,
                "custody native ABI layout")
        self.invalid=C.c_void_p(-1).value

    def ok(self,value,operation):
        if not value:raise CustodyApiError(operation,self.C.get_last_error())
        return value

    def _open(self,path,access,share,disposition,flags,security=None,operation="OPEN_SOURCE"):
        C=self.C;holder=None;attrs=None
        if security is not None:
            require(type(security) is bytes and 20<=len(security)<=65536,"custody security descriptor bound")
            holder=C.create_string_buffer(security)
            attrs=self.SecurityAttributes(C.sizeof(self.SecurityAttributes),C.cast(holder,C.c_void_p),False)
        h=self.create(str(path),access,share,C.byref(attrs) if attrs is not None else None,disposition,flags,None)
        if h==self.invalid or h is None:raise CustodyApiError(operation,C.get_last_error())
        return h

    @contextmanager
    def opened(self,path,*,rename=False,directory=False):
        physical(path)
        access=(0x80|0x20000) if directory else (0x80000000|0x20000)
        if rename:access|=0x10000
        flags=0x00200000|(0x02000000 if directory else 0)
        h=self._open(path,access,3 if directory else 1,3,flags,
                     operation="OPEN_DIRECTORY" if directory else "OPEN_SOURCE")
        try:
            require(self.filetype(h)==1,"custody disk handle")
            self.path_matches(h,path)
            yield h
        finally:self.ok(self.close(h),"CLOSE")

    @contextmanager
    def created(self,path,security):
        require(not path.exists() and not path.is_symlink(),"custody stage name unused")
        h=self._open(path,0x80000000|0x40000000|0x10000|0x20000,1,1,0x80|0x00200000,security,"CREATE_STAGE")
        try:
            self.path_matches(h,path)
            yield h
        finally:self.ok(self.close(h),"CLOSE")

    def path_matches(self,h,path):
        C=self.C;buf=C.create_unicode_buffer(1024)
        n=self.finalname(h,buf,len(buf),0)
        self.ok(n,"FINAL_NAME")
        require(0<n<len(buf),"custody final path bound")
        import ntpath
        name=buf.value
        if name.startswith("\\\\?\\"):name=name[4:]
        require(ntpath.normcase(ntpath.normpath(name))==
                ntpath.normcase(ntpath.normpath(str(path))),"custody handle path identity")

    def query(self,h,kind,cls):
        operation={0:"QUERY_BASIC",1:"QUERY_STANDARD",18:"QUERY_ID",9:"QUERY_TAG"}[kind]
        value=cls();self.ok(self.info(h,kind,self.C.byref(value),self.C.sizeof(value)),operation)
        return value

    def metadata(self,h):
        basic=self.query(h,0,self.Basic);standard=self.query(h,1,self.Standard)
        identity=self.query(h,18,self.Identity);tag=self.query(h,9,self.Tag)
        require(basic.attributes==tag.attributes,"custody attribute API binding")
        return {"volume":int(identity.volume),"file_id":bytes(identity.file_id).hex(),
                "creation":int(basic.creation),"write":int(basic.write),"change":int(basic.change),
                "attributes":int(basic.attributes),"reparse_tag":int(tag.tag),"size":int(standard.size),
                "links":int(standard.links),"directory":bool(standard.directory),"pending":bool(standard.pending)}

    def file_shape(self,value,*,multiple=False):
        require(type(value) is dict and value["volume"]>0 and value["file_id"]!="0"*32
                and not value["directory"] and not value["pending"]
                and not value["attributes"]&0x400 and value["reparse_tag"]==0
                and 0<=value["size"]<=MAX_FILE
                and (value["links"]>1 if multiple else value["links"]>=1),
                "custody bounded physical origin")
        if multiple:
            # A copying route does not silently change encryption/compression/sparse/offline semantics.
            require(not value["attributes"]&~0xA1,"custody origin attributes supported")

    def permissions(self,h):
        C=self.C;needed=C.c_uint32()
        ok=self.security(h,self.SECURITY_FIELDS,None,0,C.byref(needed))
        if ok or C.get_last_error()!=122:raise CustodyApiError("SECURITY_SIZE",C.get_last_error())
        require(20<=needed.value<=65536,"custody permission descriptor size")
        buf=C.create_string_buffer(needed.value)
        self.ok(self.security(h,self.SECURITY_FIELDS,buf,len(buf),C.byref(needed)),"SECURITY")
        text=C.c_void_p();length=C.c_uint32()
        self.ok(self.sddl(buf,1,self.SECURITY_FIELDS,C.byref(text),C.byref(length)),"SECURITY_STRING")
        try:
            require(text.value is not None and 1<length.value<=32768,"custody permission string bound")
            # The API reports allocated WCHAR capacity, not logical SDDL length.
            # Receive only through the first terminator, within the checked buffer.
            units=C.cast(text,C.POINTER(C.c_wchar))
            for index in range(length.value):
                if units[index]=="\0":break
            else:raise Refusal("custody permission string termination")
            # Convert the whole bounded prefix so Windows UTF-16 pairs combine.
            value=C.wstring_at(text,index)
            require("\0" not in value and "O:" in value and "G:" in value and "D:" in value,
                    "custody complete permissions")
            return bytes(buf.raw[:needed.value]),digest(value.encode("utf-16-le"))
        finally:
            if self.localfree(text):raise CustodyApiError("FREE_SECURITY",C.get_last_error())

    def _captured_permission_string(self,descriptor,mask,*,observer=None,component=None,side=None):
        # Observer checkpoints consume only local values from the captured descriptor.
        observer_phase="FIELD_INPUT"
        try:
            require(type(descriptor) is bytes and 20<=len(descriptor)<=65536,
                    "permission component descriptor bound")
            require(type(mask) is int and mask in {value for name,value in PERMISSION_COMPONENT_FIELDS},
                    "permission component fixed field")
            observer_phase="STRING_BUFFER"
            C=self.C;buf=C.create_string_buffer(descriptor);text=C.c_void_p();length=C.c_uint32()
            observer_phase="STRING_CALL"
            self.ok(self.sddl(buf,1,mask,C.byref(text),C.byref(length)),"SECURITY_STRING")
            try:
                observer_phase="STRING_BOUND"
                require(text.value is not None and 1<=length.value<=32768,"permission component string bound")
                observer_phase="STRING_SCAN"
                units=C.cast(text,C.POINTER(C.c_wchar))
                for index in range(length.value):
                    if units[index]=="\0":break
                else:raise Refusal("permission component string termination")
                observer_phase="STRING_READ"
                value=C.wstring_at(text,index)
                observer_phase="STRING_VALUE"
                require("\0" not in value,"permission component complete string")
                return value
            except BaseException as observer_error:
                capture_permission_observer_failure(observer,observer_error,observer_phase,component,side)
                raise
            finally:
                observer_phase="STRING_FREE"
                try:
                    if text.value is not None and self.localfree(text):
                        raise CustodyApiError("FREE_SECURITY",C.get_last_error())
                except BaseException as observer_error:
                    capture_permission_observer_failure(observer,observer_error,observer_phase,component,side)
                    raise
        except BaseException as observer_error:
            capture_permission_observer_failure(observer,observer_error,observer_phase,component,side)
            raise

    def permission_component_equality(self,origin_descriptor,stage_descriptor,*,observer=None):
        # Same captured pair and native operations; partial observations are best effort.
        observer_phase="CAPTURED_INPUT";observer_component=None;observer_side=None
        try:
            require(all(type(value) is bytes and 20<=len(value)<=65536
                        for value in (origin_descriptor,stage_descriptor)),"permission component descriptor bound")
            observer_phase="CONTROL_BIND"
            C=self.C;P=C.c_void_p;W=C.c_uint16;D=C.c_uint32
            get_control=self.A.GetSecurityDescriptorControl
            get_control.argtypes=(P,C.POINTER(W),C.POINTER(D));get_control.restype=C.c_int
            controls=[]
            observer_side="ORIGIN"
            for descriptor in (origin_descriptor,stage_descriptor):
                observer_phase="CONTROL_BUFFER"
                buf=C.create_string_buffer(descriptor);control=W();revision=D()
                observer_phase="CONTROL_CALL"
                self.ok(get_control(buf,C.byref(control),C.byref(revision)),"SECURITY")
                observer_phase="CONTROL_FORMAT"
                require(revision.value==1 and control.value&0x8000,"permission component captured descriptor format")
                controls.append(int(control.value))
                observer_side="STAGE"
            observer_phase="CONTROL_COMPARE";observer_side=None
            permission_observer_controls(observer,{name:(controls[0]&mask)==(controls[1]&mask)
                                         for name,mask in PERMISSION_COMPONENT_CONTROLS})
            fields={}
            for name,mask in PERMISSION_COMPONENT_FIELDS:
                observer_phase="FIELD_CALL";observer_component=name;observer_side="ORIGIN"
                origin=self._captured_permission_string(origin_descriptor,mask,observer=observer,component=name,side="ORIGIN")
                observer_side="STAGE"
                stage=self._captured_permission_string(stage_descriptor,mask,observer=observer,component=name,side="STAGE")
                observer_phase="FIELD_COMPARE";observer_side=None
                fields[name]=origin==stage
                permission_observer_field(observer,name,fields[name])
            observer_phase="RESULT_VALIDATE";observer_component=None;observer_side=None
            return validate_permission_components({"schema":"dg18.windows20.permission-components.v1",
                "method":PERMISSION_COMPONENT_METHOD,"fields":fields,
                "controls":{name:(controls[0]&mask)==(controls[1]&mask)
                            for name,mask in PERMISSION_COMPONENT_CONTROLS}})
        except BaseException as observer_error:
            capture_permission_observer_failure(observer,observer_error,observer_phase,observer_component,observer_side)
            raise


    def default_stream_only(self,h,expected_size):
        import struct
        C=self.C;buf=C.create_string_buffer(65536)
        self.ok(self.info(h,7,buf,len(buf)),"STREAMS")
        next_offset,name_bytes,size,allocation=struct.unpack_from("<IIqq",buf.raw,0)
        require(next_offset==0 and 0<name_bytes<=512 and name_bytes%2==0
                and 24+name_bytes<=len(buf),"custody stream population")
        require(buf.raw[24:24+name_bytes].decode("utf-16-le")=="::$DATA"
                and size==expected_size and allocation>=size,"custody default stream only")

    def read_bytes(self,h,size):
        C=self.C;self.ok(self.seek(h,0,None,0),"SEEK")
        chunks=[];total=0
        while True:
            amount=min(1048576,MAX_FILE+1-total)
            require(amount>0,"custody image byte bound")
            buf=C.create_string_buffer(amount);got=C.c_uint32()
            self.ok(self.read(h,buf,amount,C.byref(got),None),"READ")
            require(got.value<=amount,"custody native read count")
            if not got.value:break
            chunks.append(buf.raw[:got.value]);total+=got.value
            require(total<=MAX_FILE,"custody image byte bound")
        raw=b"".join(chunks)
        require(len(raw)==size,"custody complete image read")
        return raw

    def snapshot(self,h,*,multiple=False):
        first=self.metadata(h);self.file_shape(first,multiple=multiple)
        sd,security=self.permissions(h);self.default_stream_only(h,first["size"])
        raw=self.read_bytes(h,first["size"])
        last=self.metadata(h);sd_after,security_after=self.permissions(h)
        self.default_stream_only(h,last["size"])
        exact(last,first,"custody handle changed while receiving")
        require(security_after==security and sd_after==sd,"custody permissions changed while receiving")
        return {"native":last,"bytes":len(raw),"sha256":digest(raw),"permissions_sha256":security},raw,sd

    def write_image(self,h,raw,origin):
        C=self.C
        require(type(raw) is bytes and 0<len(raw)<=MAX_FILE,"custody stage byte count")
        self.ok(self.seek(h,0,None,0),"SEEK")
        for start in range(0,len(raw),1048576):
            chunk=raw[start:start+1048576];buf=C.create_string_buffer(chunk);done=C.c_uint32()
            self.ok(self.write(h,buf,len(chunk),C.byref(done),None),"WRITE")
            require(done.value==len(chunk),"custody short stage write")
        self.ok(self.flush(h),"FLUSH")
        basic=self.Basic(origin["creation"],0,origin["write"],0,origin["attributes"])
        self.ok(self.setinfo(h,0,C.byref(basic),C.sizeof(basic)),"STAGE_ATTRIBUTES")
        self.ok(self.flush(h),"FLUSH")

    def rename_absent(self,h,path):
        C=self.C;raw=str(path).encode("utf-16-le")
        require(path.is_absolute() and 0<len(raw)<=480 and "\0" not in str(path),
                "custody rename destination")
        size=self.Rename.name.offset+len(raw)+2
        buf=C.create_string_buffer(max(size,C.sizeof(self.Rename)))
        value=C.cast(buf,C.POINTER(self.Rename)).contents
        value.replace=0;value.root=None;value.length=len(raw)
        C.memmove(C.addressof(buf)+self.Rename.name.offset,raw,len(raw))
        self.ok(self.setinfo(h,3,buf,size),"RENAME_ABSENT")
        self.path_matches(h,path)

    @contextmanager
    def directories(self,path):
        # Hold each ancestor against rename/delete. These handles do not grant write access.
        chain=list(reversed((path,*path.parents)))
        with ExitStack() as stack:
            before=[]
            for p in chain:
                h=stack.enter_context(self.opened(p,directory=True))
                v=self.metadata(h)
                require(v["directory"] and not v["pending"] and not v["attributes"]&0x400
                        and v["reparse_tag"]==0,"custody physical directory")
                sd,security=self.permissions(h)
                before.append((p,h,{"volume":v["volume"],"file_id":v["file_id"],
                                   "creation":v["creation"],"attributes":v["attributes"],
                                   "permissions_sha256":security}))
            yield
            for p,h,old in before:
                self.path_matches(h,p);v=self.metadata(h);sd,security=self.permissions(h)
                current={"volume":v["volume"],"file_id":v["file_id"],"creation":v["creation"],
                         "attributes":v["attributes"],"permissions_sha256":security}
                exact(current,old,"custody directory changed")

    def expect_write_denied(self,path):
        # Shared image WRITE exclusion is checked before the alias is held.
        h=self.create(str(path),0x40000000,7,None,3,0x00200000,None)
        if h!=self.invalid and h is not None:
            self.ok(self.close(h),"CLOSE")
            raise Refusal("custody kernel sharing control")
        require(self.C.get_last_error() in (32,33),"custody kernel expected sharing refusal")

    def expect_write_and_delete_denied(self,path):
        """Real kernel fixture: conflicting write/delete opens must be denied by held read handle."""
        for access in (0x40000000,0x10000):
            h=self.create(str(path),access,7,None,3,0x00200000,None)
            if h!=self.invalid and h is not None:
                self.ok(self.close(h),"CLOSE")
                raise Refusal("custody kernel sharing control")
            require(self.C.get_last_error() in (32,33),"custody kernel expected sharing refusal")


# Windows20 closed selection/provisioning policy; no launch or inherited entitlement.
CUSTODY_CHECKS=("selection_bound","original_guard_passed","support_unchanged",
                "kernel_controls_passed","origin_current","same_volume","copy_equal",
                "stage_single_link","permissions_equal","retired_identity_bound","installed_identity_bound")
CUSTODY_STAGES=("START","ASSESSMENT","SELECTION","FIXTURE_GATE","ORIGIN_LOCKED",
                "STAGED","ORIGIN_RENAME_INTENT","ORIGIN_RETIRED","INSTALL_RENAME_INTENT",
                "IMAGE_INSTALLED","POST_ADMITTED","COMPLETE")
CUSTODY_ERRORS=("ACCESS_DENIED","SHARING_REFUSED","NAME_COLLISION","API_REFUSED",
                "PREDICATE_REFUSED","FILE_IO_FAILURE","UNEXPECTED_FAILURE")
CUSTODY_OPERATIONS=("OPEN_SOURCE","OPEN_DIRECTORY","CREATE_STAGE","CLOSE","FINAL_NAME",
                    "QUERY_BASIC","QUERY_STANDARD","QUERY_ID","QUERY_TAG","SECURITY_SIZE",
                    "SECURITY","SECURITY_STRING","FREE_SECURITY","STREAMS","SEEK","READ",
                    "WRITE","FLUSH","STAGE_ATTRIBUTES","RENAME_ABSENT")
CUSTODY_KERNEL_CASES=("unheld_alias_write_denied","explicit_held_names_write_delete_denied",
                      "fresh_same_path_single_link",
                      "origin_alias_retired_identity","permissions_and_bytes_preserved",
                      "original_guard_after_transition","occupied_target_refused",
                      "partial_failure_retained_without_rollback")
CUSTODY_ADAPTER_SHA256="7f93f8134b7a093c01b7d482f999617710f26832dc0f55438399df335b3f587e"
CUSTODY_NATIVE_SHA256="add9bce3a9d1128680eed274e65abcd6a442eabf15fd8a8382b198b25765fcd9"
CUSTODY_STATES=("ABSENT","ADMITTED","MULTILINK_ONLY","REFUSED")
CUSTODY_REQUIRED={
    "EXISTING":("selection_bound","original_guard_passed","support_unchanged","installed_identity_bound"),
    "MATERIALIZED":CUSTODY_CHECKS}
CUSTODY_MAX_SUPPORT_FILES=256
CUSTODY_MAX_SUPPORT_BYTES=268435456

ASSESSMENT_PREDICATE_REASONS=('Campaign output already exists', 'JSON object required', 'actual Windows required before allocation', 'actual candidate/resource receipt bindings required', 'actual source commit/tree', 'actual workflow commit', 'admission diagnostic member', 'admission export already attempted', 'admission export document bound', 'all skills closure differs', 'bounded Git observation failed', 'checkout has tracked/untracked/ignored changes', 'clock fields', 'clock observation types', 'code body differs', 'code manifest identity/schema', 'code manifest population', 'code manifest row schema', 'consumption type', 'control changed during fetch', 'control changed the base source', 'control commit identity', 'control document population', 'control file mode/identity', 'control file population/request', 'control preparation differs', 'control reference changed', 'control reference population', 'control sole parent', 'custody API operation', 'custody assessment choice binding', 'custody assessment disposition', 'custody assessment population', 'custody assessment schema', 'custody attribute API binding', 'custody bounded physical origin', 'custody candidate population', 'custody candidate schema', 'custody closed error class', 'custody code differs', 'custody code manifest', 'custody code population', 'custody complete admission facts', 'custody complete image read', 'custody complete permissions', 'custody complete staged copy and permissions', 'custody default stream only', 'custody directory changed', 'custody disk handle', 'custody episode already exists', 'custody exact Windows runtime', 'custody exact allowlisted selection', 'custody existing selection changed', 'custody final path bound', 'custody fixture collision changed objects', 'custody fixture exact hardlink origin', 'custody fixture expected partial collision', 'custody fixture expected target collision', 'custody fixture held alias identity', 'custody fixture held alias image', 'custody fixture held alias image unchanged', 'custody fixture held alias unchanged', 'custody fixture held source image unchanged', 'custody fixture held source unchanged', 'custody fixture image/alias split', 'custody fixture overwrite was not refused', 'custody fixture partial collision not refused', 'custody fixture partial state not retained', 'custody fixture record bound', 'custody fresh stage identity', 'custody handle changed while receiving', 'custody handle path identity', 'custody image byte bound', 'custody immutable adapter', 'custody immutable native companion', 'custody immutable selected manifest', 'custody incomplete shape', 'custody installed bytes/link', 'custody installed image changed after close', 'custody journal bound', 'custody journal event', 'custody kernel controls require actual Windows', 'custody kernel expected sharing refusal', 'custody kernel sharing control', 'custody native ABI layout', 'custody native read count', 'custody native selected image changed', 'custody no eligible direct Git candidate', 'custody no unbound DLL redirection', 'custody observation required', 'custody observed origin changed before mutation', 'custody origin attributes supported', 'custody origin bytes before retirement', 'custody origin changed before retirement', 'custody owned staging names unused', 'custody permission descriptor size', 'custody permission string bound', 'custody permission string termination', 'custody permissions changed while receiving', 'custody physical directory', 'custody postadmission native image', 'custody preparation admission required', 'custody preparation/export binding', 'custody private event budget', 'custody private request/code binding', 'custody private selection', 'custody private selection schema', 'custody projection bound', 'custody projection fields', 'custody projection request/code binding', 'custody projection vocabulary', 'custody proof Boolean population', 'custody receiving complete', 'custody record digest', 'custody refusal shape', 'custody rename destination', 'custody renamed object identity/content/permissions', 'custody request identity', 'custody retired bytes', 'custody reviewed wrapper pin', 'custody same local volume', 'custody sealed entitlement changed', 'custody security descriptor bound', 'custody selected lease identity', 'custody selected ordinal', 'custody selected physical image changed', 'custody selected source binding', 'custody selected source differs', 'custody selection record bound', 'custody short stage write', 'custody stage byte count', 'custody stage name unused', 'custody staged identity/content/permissions after close', 'custody staging locality', 'custody stream population', 'custody support byte bound', 'custody support changed during hold', 'custody support closure changed', 'custody support directory changed while receiving', 'custody support directory population', 'custody support exclusion', 'custody support file bound', 'custody support lease identity', 'custody supported Git exec layout', 'custody wrapper literal differs', 'diagnostic workflow wrapper pin', 'document budget/type', 'duplicate JSON member', 'exact hosted workflow context required', 'exact root one-shot GO required', 'export consumption binding', 'export preparation request', 'external operation reference', 'failure context predicate fingerprint', 'failure context request/schema', 'failure context vocabulary', 'failure projection must preserve uncertainty', 'fixed local NTFS volume required', 'grant already consumed', 'held direct Git changed before invocation', 'held workflow host context changed', 'hold/output must be separated', 'immutable freshness interval', 'independent exact host review required', 'invalid JSON document', 'invalid commit parent', 'nonfinite JSON number', 'outer Job helper changed', 'outer Job terminal census/cleanup not established', 'packet directory population', 'parent traversal', 'permission component Boolean population', 'permission component captured descriptor format', 'permission component closed population', 'permission component complete string', 'permission component descriptor bound', 'permission component fixed field', 'permission component full mismatch gate', 'permission component method', 'permission component schema', 'permission component string bound', 'permission component string termination', 'permission observer API code binding', 'permission observer absent component', 'permission observer absent side', 'permission observer complete control pair', 'permission observer complete prefix', 'permission observer completion order', 'permission observer component', 'permission observer control completion', 'permission observer control consistency', 'permission observer control prefix', 'permission observer empty prefix', 'permission observer error class', 'permission observer exception object', 'permission observer failure gate', 'permission observer field completion', 'permission observer field prefix', 'permission observer owned trace', 'permission observer partial Boolean or null', 'permission observer partial population', 'permission observer partial schema', 'permission observer phase', 'permission observer predicate binding', 'permission observer schema', 'permission observer side', 'permission observer trusted native error', 'permission observer trusted predicate', 'permission observer unexpected payload', 'phase vocabulary', 'physical CPython3.12.10 x64 required', 'physical tools/source/code/tree changed during hold', 'preparation expired or clock moved backwards', 'preparation file changed', 'preparation record budget', 'preparation refusal field population', 'preparation refusal predicate', 'preparation refusal request/type binding', 'preparation refusal vocabulary', 'private bindings changed', 'private invocation bytes differ', 'private state schema', 'public completion types', 'public failure class', 'public phase vocabulary', 'public predicate fingerprint', 'public result field population', 'public result request/type binding', 'qualification packet path differs', 'read_regular:CROSS_FINAL:st_birthtime_ns', 'read_regular:CROSS_FINAL:st_dev', 'read_regular:CROSS_FINAL:st_file_attributes', 'read_regular:CROSS_FINAL:st_ino', 'read_regular:CROSS_FINAL:st_mode', 'read_regular:CROSS_FINAL:st_mtime_ns', 'read_regular:CROSS_FINAL:st_nlink', 'read_regular:CROSS_FINAL:st_reparse_tag', 'read_regular:CROSS_FINAL:st_size', 'read_regular:CROSS_OPEN:st_birthtime_ns', 'read_regular:CROSS_OPEN:st_dev', 'read_regular:CROSS_OPEN:st_file_attributes', 'read_regular:CROSS_OPEN:st_ino', 'read_regular:CROSS_OPEN:st_mode', 'read_regular:CROSS_OPEN:st_mtime_ns', 'read_regular:CROSS_OPEN:st_nlink', 'read_regular:CROSS_OPEN:st_reparse_tag', 'read_regular:CROSS_OPEN:st_size', 'read_regular:HANDLE_AFTER:file_shape', 'read_regular:HANDLE_OPEN:file_shape', 'read_regular:HANDLE_STABILITY:st_birthtime_ns', 'read_regular:HANDLE_STABILITY:st_ctime_ns', 'read_regular:HANDLE_STABILITY:st_dev', 'read_regular:HANDLE_STABILITY:st_file_attributes', 'read_regular:HANDLE_STABILITY:st_ino', 'read_regular:HANDLE_STABILITY:st_mode', 'read_regular:HANDLE_STABILITY:st_mtime_ns', 'read_regular:HANDLE_STABILITY:st_nlink', 'read_regular:HANDLE_STABILITY:st_reparse_tag', 'read_regular:HANDLE_STABILITY:st_size', 'read_regular:PATH_AFTER:file_shape', 'read_regular:PATH_BEFORE:file_shape', 'read_regular:PATH_STABILITY:st_birthtime_ns', 'read_regular:PATH_STABILITY:st_ctime_ns', 'read_regular:PATH_STABILITY:st_dev', 'read_regular:PATH_STABILITY:st_file_attributes', 'read_regular:PATH_STABILITY:st_ino', 'read_regular:PATH_STABILITY:st_mode', 'read_regular:PATH_STABILITY:st_mtime_ns', 'read_regular:PATH_STABILITY:st_nlink', 'read_regular:PATH_STABILITY:st_reparse_tag', 'read_regular:PATH_STABILITY:st_size', 'read_regular:READ_BYTE_COUNT', 'retained outer command differs', 'retained outer measurement digest differs', 'retained outer measurement incomplete', 'retained outer working directory differs', 'returned/stored outer measurement differs', 'root STOP received', 'running interpreter differs from selected physical Python', 'sealed entitlement changed', 'sealed packet must remain UNGRANTED', 'selected source bytes differ', 'selected source identity/schema', 'selected source population', 'selected source row differs from actual Git tree', 'selected source row schema', 'shape Boolean population', 'shape caller role', 'shape diagnostic byte bound', 'shape diagnostic field population', 'shape diagnostic observation absent', 'shape diagnostic request/code binding', 'shape failure conjunction', 'shape manifest index', 'shape observation required', 'shape observation schema', 'shape phase', 'shape predicate classification', 'shape request identity', 'shape reviewed wrapper pin', 'shape size predicate contradiction', 'shape stage/predicate binding', 'source and packet must be separate', 'source checkout path differs', 'source tree population', 'staged copy Boolean population', 'staged copy admission member', 'staged copy caller role', 'staged copy callsite checkpoint', 'staged copy custody checkpoint', 'staged copy custody refusal', 'staged copy custody selection', 'staged copy custody selection binding', 'staged copy diagnostic byte bound', 'staged copy diagnostic fields', 'staged copy diagnostic observation absent', 'staged copy diagnostic request/code binding', 'staged copy failure conjunction', 'staged copy observation required', 'staged copy observation schema', 'staged copy phase', 'staged copy predicate classification', 'staged copy request identity', 'staged copy reviewed wrapper pin', 'stop request identity', 'symlink/reparse path', 'terminal containment not established', 'terminal exit code', 'terminal export bindings differ', 'terminal export host context differs', 'terminal export preparation differs', 'terminal measurement identity required', 'terminal outcome contradicts exit', 'unclassified assessment predicate', 'unexpected tree leaf type', 'unexpected tree path', 'unrecognized terminal outcome', 'volume information unavailable', 'volume root unavailable', 'wait episode already allocated', 'wall/monotonic clock divergence', 'workflow sole parent differs', 'workflow tree must be exact source plus seven files', 'workflow/run identity')
ASSESSMENT_PREDICATES={digest(reason.encode("utf-8")):reason for reason in ASSESSMENT_PREDICATE_REASONS}


def assessment_failure(error,boundary):
    require(boundary in ("ORIGINAL_GUARD","NATIVE_SNAPSHOT"),"assessment failure boundary")
    kind=custody_error(error)
    predicate=None;shape=None
    if kind=="PREDICATE_REFUSED":
        reason=str(error)
        if reason not in ASSESSMENT_PREDICATE_REASONS:reason="unclassified assessment predicate"
        predicate=digest(reason.encode("utf-8"))
        shape=validate_shape_observation(getattr(error,"shape_observation",None),kind,predicate)
    result={"boundary":boundary,"predicate_sha256":predicate,"shape_observation":shape}
    return validate_assessment_failure(result,kind)

def validate_assessment_failure(value,error_class):
    require(type(value) is dict and set(value)=={"boundary","predicate_sha256","shape_observation"}
            and type(value["boundary"]) is str and value["boundary"] in ("ORIGINAL_GUARD","NATIVE_SNAPSHOT"),
            "assessment closed failure fields")
    predicate=value["predicate_sha256"]
    require(type(predicate) is str and predicate in ASSESSMENT_PREDICATES if error_class=="PREDICATE_REFUSED"
            else predicate is None,"assessment closed predicate classification")
    shape=value["shape_observation"]
    if shape is not None:
        require(value["boundary"]=="ORIGINAL_GUARD","assessment shape boundary")
        shape=validate_shape_observation(shape,error_class,predicate)
        require(shape["role"]=="TOOL_GIT" and shape["manifest_index"] is None,"assessment shape subject")
    else:
        validate_shape_observation(None,error_class,predicate)
    require(len(canonical(value))<=SHAPE_MAX_BYTES,"assessment failure byte bound")
    return value

def custody_codebook():
    return {"schema":"dg18.windows20.custody-codebook.v1","stages":list(CUSTODY_STAGES),
            "checks":list(CUSTODY_CHECKS),"errors":list(CUSTODY_ERRORS),
            "api_operations":list(CUSTODY_OPERATIONS),"kernel_case_population":list(CUSTODY_KERNEL_CASES),
            "staged_copy_codebook_sha256":digest(canonical(staged_copy_codebook())),
            "kernel_guard_scope":{"unheld_alias_write":"SOURCE_HOLDER_SHARED_IMAGE",
                                  "write_and_delete":"EACH_EXPLICITLY_HELD_NAME",
                                  "unheld_alias_delete":"NO_DENIAL_CLAIM"},
            "candidate_states":list(CUSTODY_STATES),"candidate_indices":[0,1],
            "assessment_failure_fields":["boundary","predicate_sha256","shape_observation"],
            "assessment_boundaries":["ORIGINAL_GUARD","NATIVE_SNAPSHOT"],
            "assessment_predicates_sha256":digest(canonical(ASSESSMENT_PREDICATES)),
            "method_requirements":{k:list(v) for k,v in CUSTODY_REQUIRED.items()},
            "source_commit":SOURCE_COMMIT,"source_tree":SOURCE_TREE,
            "image_bound":MAX_FILE,"support_file_bound":CUSTODY_MAX_SUPPORT_FILES,
            "support_total_bound":CUSTODY_MAX_SUPPORT_BYTES,
            "mutation":"EXACT_HANDLES_TWO_NONOVERWRITING_RENAMES_NO_ROLLBACK",
            "permissions":"OWNER_GROUP_DACL_LABEL_RESOURCE_ATTRIBUTES_CAP",
            "audit_SACL":"NO_FULL_REPLICATION_CLAIM; ORIGINAL_OBJECT_AUDIT_SACL_NOT_MODIFIED",
            "authority":"NONE"}

def custody_context(ctx):
    require(type(ctx.get("run_id")) is str and re.fullmatch("[0-9]{1,20}",ctx["run_id"])
            and ctx.get("attempt")=="1" and hex_value(ctx.get("workflow_commit"),40),
            "custody request identity")
    require(hex_value(DIAGNOSTIC_WRAPPER_SHA256,64),"custody reviewed wrapper pin")
    return {"run_id":ctx["run_id"],"attempt":"1","workflow_commit":ctx["workflow_commit"],
            "source_commit":SOURCE_COMMIT,"source_tree":SOURCE_TREE,
            "wrapper_sha256":DIAGNOSTIC_WRAPPER_SHA256,
            "custody_codebook_sha256":digest(canonical(custody_codebook()))}

def custody_error(error):
    if isinstance(error,CustodyApiError):return error.custody_error
    return ("PREDICATE_REFUSED" if isinstance(error,Refusal) else
            "FILE_IO_FAILURE" if isinstance(error,OSError) else "UNEXPECTED_FAILURE")

def validate_custody_projection(value,ctx,*,required=False):
    if value is None:
        require(not required,"custody observation required")
        return None
    context=custody_context(ctx)
    keys={"schema","context","status","method","selected_index","stage","assessment",
          "checks","error_class","api_operation","private_record_sha256"}
    require(type(value) is dict and set(value)==keys
            and value["schema"]=="dg18.windows20.custody-projection.v1","custody projection fields")
    exact(value["context"],context,"custody projection request/code binding")
    require(type(value["status"]) is str and value["status"] in ("INCOMPLETE","REFUSED","ESTABLISHED")
            and type(value["method"]) is str and value["method"] in ("NONE","EXISTING","MATERIALIZED")
            and type(value["stage"]) is str and value["stage"] in CUSTODY_STAGES,"custody projection vocabulary")
    require(value["selected_index"] is None or type(value["selected_index"]) is int
            and value["selected_index"] in (0,1),"custody selected ordinal")
    a=value["assessment"]
    require(type(a) is list and (not a or len(a)==2),"custody assessment population")
    for index,row in enumerate(a):
        require(type(row) is dict and set(row)=={"index","status","error_class","api_operation","failure"}
                and type(row["index"]) is int and row["index"]==index
                and row["status"] in CUSTODY_STATES
                and (row["error_class"] is None or type(row["error_class"]) is str
                     and row["error_class"] in CUSTODY_ERRORS)
                and (row["api_operation"] is None or type(row["api_operation"]) is str
                     and row["api_operation"] in CUSTODY_OPERATIONS),"custody assessment schema")
        require(row["error_class"] in CUSTODY_ERRORS if row["status"]=="REFUSED"
                else row["error_class"] is None and row["api_operation"] is None,
                "custody assessment disposition")
        if row["status"]=="REFUSED":
            validate_assessment_failure(row["failure"],row["error_class"])
        else:require(row["failure"] is None,"assessment nonfailure has no failure envelope")
    checks=value["checks"]
    require(type(checks) is dict and set(checks)==set(CUSTODY_CHECKS)
            and all(type(v) is bool for v in checks.values()),"custody proof Boolean population")
    require(value["error_class"] is None or type(value["error_class"]) is str
            and value["error_class"] in CUSTODY_ERRORS,"custody closed error class")
    require(value["api_operation"] is None or type(value["api_operation"]) is str
            and value["api_operation"] in CUSTODY_OPERATIONS,"custody API operation")
    record=value["private_record_sha256"]
    require(record is None or hex_value(record,64),"custody record digest")
    if value["status"]=="ESTABLISHED":
        require(value["stage"]=="COMPLETE" and value["method"] in CUSTODY_REQUIRED
                and type(value["selected_index"]) is int and len(a)==2
                and value["error_class"] is None and value["api_operation"] is None and hex_value(record,64)
                and all(checks[k] for k in CUSTODY_REQUIRED[value["method"]]),
                "custody complete admission facts")
        method,index=select_git_policy([{"index":r["index"],"status":r["status"]} for r in a])
        require((method,index)==(value["method"],value["selected_index"]),"custody assessment choice binding")
    elif value["status"]=="REFUSED":
        require(value["error_class"] in CUSTODY_ERRORS and record is None,"custody refusal shape")
    else:
        require(value["error_class"] is None and value["api_operation"] is None and record is None and value["stage"]!="COMPLETE",
                "custody incomplete shape")
    require(len(canonical(value))<=8192,"custody projection bound")
    return value

def select_git_policy(rows):
    require(type(rows) is list and len(rows)==2,"custody candidate population")
    for index,row in enumerate(rows):
        require(type(row) is dict and set(row)=={"index","status"} and type(row["index"]) is int
                and row["index"]==index and type(row["status"]) is str
                and row["status"] in CUSTODY_STATES,"custody candidate schema")
    for status,method in (("ADMITTED","EXISTING"),("MULTILINK_ONLY","MATERIALIZED")):
        for row in rows:
            if row["status"]==status:return method,row["index"]
    raise Refusal("custody no eligible direct Git candidate")

class CustodyJournal:
    def __init__(self,ctx,paths):
        self.ctx=ctx;self.paths=paths;self.ordinal=0
        self.value={"schema":"dg18.windows20.custody-projection.v1","context":custody_context(ctx),
                    "status":"INCOMPLETE","method":"NONE","selected_index":None,"stage":"START",
                    "assessment":[],"checks":{k:False for k in CUSTODY_CHECKS},
                    "error_class":None,"api_operation":None,"private_record_sha256":None}
        require(not (paths["hold"]/"GIT_SELECTION.json").exists()
                and not (paths["hold"]/"CUSTODY_PROGRESS.json").exists(),"custody episode already exists")
        self.emit("START")

    def emit(self,stage,detail=None,**checks):
        require(stage in CUSTODY_STAGES and set(checks)<=set(CUSTODY_CHECKS)
                and all(type(v) is bool for v in checks.values()),"custody journal event")
        self.ordinal+=1
        require(self.ordinal<=32,"custody journal bound")
        self.value["stage"]=stage;self.value["checks"].update(checks)
        private={"schema":"dg18.windows20.private-custody-event.v1","context":custody_context(self.ctx),
                 "ordinal":self.ordinal,"stage":stage,"details":detail}
        require(len(canonical(private))<=MAX_STATE,"custody private event budget")
        save(self.paths["hold"]/("CUSTODY_PRIVATE_%02d.json"%self.ordinal),private)
        self.persist()

    def persist(self):
        validate_custody_projection(self.value,self.ctx)
        target=self.paths["hold"]/"CUSTODY_PROGRESS.json"
        if target.exists():read_document(target)
        next_path=self.paths["hold"]/"CUSTODY_PROGRESS.next.json"
        save(next_path,self.value);os.replace(next_path,target)

    def refused(self,error):
        self.value.update(status="REFUSED",error_class=custody_error(error),
                          api_operation=getattr(error,"operation",None),private_record_sha256=None)
        self.persist()

    def complete(self,record):
        raw=canonical(record);require(len(raw)<=MAX_STATE,"custody selection record bound")
        save(self.paths["hold"]/"GIT_SELECTION.json",raw)
        self.value.update(status="ESTABLISHED",stage="COMPLETE",private_record_sha256=digest(raw))
        self.persist()

def same_renamed_object(before,after):
    # The documented metadata ChangeTime may change during our own rename.
    # No pre- or post-admission same-API comparison is relaxed.
    a={**before,"native":{k:v for k,v in before["native"].items() if k!="change"}}
    b={**after,"native":{k:v for k,v in after["native"].items() if k!="change"}}
    exact(b,a,"custody renamed object identity/content/permissions")

def materialize_same_path(api,target,work,expected,emit,*,callsite):
    """Maintenance pair; partial states are retained, never rolled back or accepted."""
    require(type(callsite) is str and callsite in STAGED_COPY_CALLS,"staged copy caller role")
    require(work.parent==target.parent or work.parent.parent==target.parent,
            "custody staging locality")
    staged=work/"stage.exe";retired=work/"retired-original.exe"
    require(not staged.exists() and not retired.exists()
            and not staged.is_symlink() and not retired.is_symlink(),"custody owned staging names unused")
    with api.directories(work):
        with api.opened(work,directory=True) as dh:
            volume=api.metadata(dh)["volume"]
        with api.opened(target,rename=True) as original:
            before,raw,descriptor=api.snapshot(original,multiple=True)
            exact(before,expected,"custody observed origin changed before mutation")
            require(before["native"]["volume"]==volume and len(raw)>0,"custody same local volume")
            emit("ORIGIN_LOCKED",{"origin":before},origin_current=True,same_volume=True)
            with api.created(staged,descriptor) as writer:
                created=api.metadata(writer)
                require(created["volume"]==volume and created["file_id"]!=before["native"]["file_id"]
                        and created["links"]==1,"custody fresh stage identity")
                api.write_image(writer,raw,before["native"])
                written,stage_raw,stage_sd=api.snapshot(writer)
                try:
                    require(stage_raw==raw and written["permissions_sha256"]==before["permissions_sha256"],
                            "custody complete staged copy and permissions")
                except Refusal as error:
                    try:
                        error.staged_copy_observation=observe_staged_copy(callsite,stage_raw,raw,written,before)
                        if error.staged_copy_observation is not None and error.staged_copy_observation["permissions_equal"] is False:
                            observer=PermissionObserverTrace()
                            observer_phase="OBSERVER_CALL"
                            try:
                                components=api.permission_component_equality(descriptor,stage_sd,observer=observer)
                                observer_phase="RESULT_RECEIVE"
                                error.staged_copy_observation["permission_components"]=validate_permission_components(components)
                            except BaseException as observer_error:
                                capture_permission_observer_failure(observer,observer_error,observer_phase)
                                error.staged_copy_observation["permission_component_failure"]=receive_permission_observer_failure(observer,observer_error)
                    except BaseException:
                        pass  # Observation failure cannot replace the original refusal.
                    raise
            # Reopen after the last write handle closes, before trusting stable timestamps.
            with api.opened(staged,rename=True) as replacement:
                stage,stage_raw,stage_sd=api.snapshot(replacement)
                require(stage["native"]["volume"]==volume
                        and stage["native"]["file_id"]==created["file_id"]
                        and stage["native"]["links"]==1 and stage_raw==raw
                        and stage["native"]["attributes"]==before["native"]["attributes"]
                        and stage["permissions_sha256"]==before["permissions_sha256"],
                        "custody staged identity/content/permissions after close")
                current,again,sd=api.snapshot(original,multiple=True)
                exact(current,before,"custody origin changed before retirement")
                require(again==raw,"custody origin bytes before retirement")
                emit("STAGED",{"stage":stage},copy_equal=True,stage_single_link=True,permissions_equal=True)
                # Both APIs bind the source by its retained handle and forbid target replacement.
                emit("ORIGIN_RENAME_INTENT",{"origin":before,"stage":stage})
                api.rename_absent(original,retired)
                retired_now,retired_raw,sd=api.snapshot(original,multiple=True)
                same_renamed_object(before,retired_now)
                require(retired_raw==raw,"custody retired bytes")
                emit("ORIGIN_RETIRED",{"retired":retired_now},retired_identity_bound=True)
                emit("INSTALL_RENAME_INTENT",{"retired":retired_now,"stage":stage})
                api.rename_absent(replacement,target)
                installed,installed_raw,sd=api.snapshot(replacement)
                same_renamed_object(stage,installed)
                require(installed_raw==raw and installed["native"]["links"]==1,"custody installed bytes/link")
                emit("IMAGE_INSTALLED",{"installed":installed},installed_identity_bound=True)
                record={"original":before,"stage":stage,"retired":retired_now,"installed":installed,
                        "retired_path":str(retired),"staged_path":str(staged),"target_path":str(target),
                        "transition":"TWO_NONOVERWRITING_HANDLE_RENAMES","atomic_pair_claim":False}
    # No mutation or retry follows any failure above. Post-admission is a separate original guard.
    return record


def inspect_git_candidates(api):
    rows=[];origins={};admitted={}
    for index,name in enumerate(GIT_CANDIDATES):
        path=Path(name);status="REFUSED";error_class=None;api_operation=None;failure=None
        try:
            raw,identity=read_regular(path,role="TOOL_GIT")
            admitted[index]=identity;status="ADMITTED"
        except FileNotFoundError:
            status="ABSENT"
        except Refusal as error:
            observation=getattr(error,"shape_observation",None)
            expected={"REGULAR_FILE":True,"UNIQUE_LINK":False,"NONNEGATIVE_SIZE":True,
                      "WITHIN_EXISTING_BOUND":True,"NONREPARSE":True}
            if (type(observation) is dict and observation.get("stage")=="PATH_BEFORE"
                    and observation.get("role")=="TOOL_GIT" and observation.get("conditions")==expected):
                try:
                    with api.opened(path) as h:
                        current,raw,sd=api.snapshot(h,multiple=True)
                    origins[index]=current;status="MULTILINK_ONLY"
                except Exception as native_error:
                    error_class=custody_error(native_error);api_operation=getattr(native_error,"operation",None)
                    failure=assessment_failure(native_error,"NATIVE_SNAPSHOT")
            else:
                error_class="PREDICATE_REFUSED"
                failure=assessment_failure(error,"ORIGINAL_GUARD")
        except OSError as error:
            error_class="FILE_IO_FAILURE"
            failure=assessment_failure(error,"ORIGINAL_GUARD")
        rows.append({"index":index,"status":status,"error_class":error_class,"api_operation":api_operation,
                     "failure":failure})
    return rows,origins,admitted

def support_snapshot(api,git,work_name):
    directory=physical(git.parent)
    require(work_name is None or re.fullmatch("dg18-iw20-custody-[0-9]{1,20}-1",work_name),
            "custody support exclusion")
    entries=sorted(p.name for p in directory.iterdir() if p.name not in (git.name,work_name))
    require(len(entries)<=4096 and len(entries)==len(set(n.casefold() for n in entries)),
            "custody support directory population")
    require(not any(n.casefold() in ("git.exe.local","git.exe.manifest.local") for n in entries),
            "custody no unbound DLL redirection")
    names=[n for n in entries if n.lower().endswith((".dll",".manifest"))]
    require(len(names)<=CUSTODY_MAX_SUPPORT_FILES,"custody support file bound")
    members={};total=0
    for name in names:
        with api.opened(directory/name) as h:
            value,raw,sd=api.snapshot(h)
        total+=len(raw);require(total<=CUSTODY_MAX_SUPPORT_BYTES,"custody support byte bound")
        members[name]=value
    require(entries==sorted(p.name for p in directory.iterdir() if p.name not in (git.name,work_name)),
            "custody support directory changed while receiving")
    return {"directory":str(directory),"entries":entries,"members":members,"bytes":total}

def held_name_sharing_controls(api,source,alias,raw):
    """Shared-data WRITE exclusion plus DELETE exclusion on each held name."""
    with api.opened(source,rename=True) as h:
        before,received,sd=api.snapshot(h,multiple=True)
        require(before["native"]["links"]==2 and received==raw,"custody fixture exact hardlink origin")
        api.expect_write_and_delete_denied(source)
        api.expect_write_denied(alias)
        # Link-name DELETE custody requires its own held name. Acquisition is
        # an actual compatibility gate, with no retry or weakened fallback.
        with api.opened(alias) as alias_handle:
            alias_pin,alias_raw,alias_sd=api.snapshot(alias_handle,multiple=True)
            exact(alias_pin,before,"custody fixture held alias identity")
            require(alias_raw==raw and alias_sd==sd,"custody fixture held alias image")
            api.expect_write_and_delete_denied(alias)
            alias_after,alias_raw_after,alias_sd_after=api.snapshot(alias_handle,multiple=True)
            exact(alias_after,alias_pin,"custody fixture held alias unchanged")
            require(alias_raw_after==alias_raw and alias_sd_after==alias_sd,
                    "custody fixture held alias image unchanged")
        after,received_after,sd_after=api.snapshot(h,multiple=True)
        exact(after,before,"custody fixture held source unchanged")
        require(received_after==received and sd_after==sd,"custody fixture held source image unchanged")
    return before

def kernel_custody_controls(api,root,ctx):
    """Actual Windows-owned fixtures only. Never called by Linux author controls."""
    require(os.name=="nt" and sys.platform=="win32","custody kernel controls require actual Windows")
    root.mkdir(exist_ok=False);ntfs(root)
    source=root/"origin.exe";alias=root/"alias.exe";exchange=root/"exchange"
    raw=b"DG18_WINDOWS20_OWNED_KERNEL_FIXTURE\n"*32
    save(source,raw);os.link(source,alias);exchange.mkdir(exist_ok=False)
    before=held_name_sharing_controls(api,source,alias,raw)
    events=[]
    def emit(stage,detail=None,**facts):events.append({"stage":stage,"detail":detail,"facts":facts})
    result=materialize_same_path(api,source,exchange,before,emit,callsite="KERNEL_FIRST")
    with api.opened(source) as h:current,received,sd=api.snapshot(h)
    with api.opened(alias) as h:other,received_alias,sd=api.snapshot(h,multiple=True)
    require(current["native"]["links"]==1 and received==received_alias==raw
            and current["native"]["file_id"]!=other["native"]["file_id"]
            and other["native"]["file_id"]==before["native"]["file_id"],"custody fixture image/alias split")
    read_regular(source,role="TOOL_GIT")
    occupied=root/"occupied.exe";save(occupied,b"OCCUPIED_UNCHANGED")
    with api.opened(source,rename=True) as h:
        try:api.rename_absent(h,occupied)
        except CustodyApiError as error:
            require(error.native_error in (80,183),"custody fixture expected target collision")
        else:raise Refusal("custody fixture overwrite was not refused")
    require(occupied.read_bytes()==b"OCCUPIED_UNCHANGED" and source.read_bytes()==raw,
            "custody fixture collision changed objects")
    # Force the inter-rename collision only in this isolated fixture.
    partial=root/"partial.exe";partial_alias=root/"partial-alias.exe";pwork=root/"partial-exchange"
    save(partial,raw);os.link(partial,partial_alias);pwork.mkdir(exist_ok=False)
    with api.opened(partial) as h:pin,received,sd=api.snapshot(h,multiple=True)
    partial_events=[]
    def partial_emit(stage,detail=None,**facts):
        partial_events.append({"stage":stage,"detail":detail,"facts":facts})
        if stage=="ORIGIN_RETIRED":save(partial,b"INTERMEDIATE_OCCUPANT_UNCHANGED")
    try:materialize_same_path(api,partial,pwork,pin,partial_emit,callsite="KERNEL_PARTIAL")
    except CustodyApiError as error:
        require(error.native_error in (80,183),"custody fixture expected partial collision")
    else:raise Refusal("custody fixture partial collision not refused")
    require(partial.read_bytes()==b"INTERMEDIATE_OCCUPANT_UNCHANGED"
            and (pwork/"retired-original.exe").read_bytes()==raw
            and (pwork/"stage.exe").read_bytes()==raw and partial_alias.read_bytes()==raw,
            "custody fixture partial state not retained")
    cases={name:True for name in CUSTODY_KERNEL_CASES}
    private={"schema":"dg18.windows20.kernel-custody-fixtures.v1","context":custody_context(ctx),
             "actual_windows":True,"cases":cases,"transition":result,"events":events,"partial_events":partial_events}
    require(len(canonical(private))<=MAX_STATE,"custody fixture record bound")
    save(root/"PRIVATE_KERNEL_RECEIPT.json",private)
    return {"schema":private["schema"],"context":private["context"],"actual_windows":True,
            "cases":cases,"private_receipt_sha256":digest(canonical(private))}

def custody_input_preflight(ctx,paths):
    # No Git invocation is used to receive these selected immutable bytes.
    manifest_raw=read_regular(paths["packet"]/"SOURCE_MANIFEST.json",MAX_DOCUMENT,role="SOURCE_MANIFEST")[0]
    require(digest(manifest_raw)==SHAPE_SOURCE_MANIFEST_SHA256,"custody immutable selected manifest")
    manifest=parse_document(manifest_raw)
    require(manifest.get("source_commit")==SOURCE_COMMIT and manifest.get("source_tree")==SOURCE_TREE
            and len(manifest.get("members",[]))==99,"custody selected source binding")
    for index,row in enumerate(manifest["members"]):
        raw,identity=read_regular(paths["source"]/row["path"],role="SELECTED_SOURCE",manifest_index=index)
        require(len(raw)==row["bytes"] and digest(raw)==row["sha256"] and blob(raw)==row["git_blob_oid"],
                "custody selected source differs")
    code=read_document(paths["packet"]/"CODE_MANIFEST.json",role="CODE_MANIFEST")
    require(code.get("schema")=="dg18.windows20.code-manifest.v1"
            and code.get("source_commit")==SOURCE_COMMIT and code.get("source_tree")==SOURCE_TREE
            and len(code.get("members",[]))==6,"custody code manifest")
    expected={PREFIX+"/"+n for n in ("held_admission.py","prepare_and_execute.py","native_checks.py",
              "SOURCE_MANIFEST.json","entitlement-reference.txt")}|{WORKFLOW}
    require({row.get("path") for row in code["members"]}==expected,"custody code population")
    for index,row in enumerate(code["members"]):
        raw,identity=read_regular(paths["packet_repo"]/row["path"],role="CODE_MEMBER",manifest_index=index)
        require(len(raw)==row["bytes"] and digest(raw)==row["sha256"] and blob(raw)==row["git_blob_oid"],
                "custody code differs")
        if row["path"]==PREFIX+"/prepare_and_execute.py":
            require(digest(raw)==CUSTODY_ADAPTER_SHA256,"custody immutable adapter")
        if row["path"]==PREFIX+"/native_checks.py":
            require(digest(raw)==CUSTODY_NATIVE_SHA256,"custody immutable native companion")
        if row["path"]==PREFIX+"/held_admission.py":
            require(digest(raw)==DIAGNOSTIC_WRAPPER_SHA256,"custody wrapper literal differs")
    require(read_regular(paths["packet"]/"entitlement-reference.txt",32,role="SEALED_ENTITLEMENT")[0]==b"UNGRANTED\n",
            "custody sealed entitlement changed")
    fingerprint(ctx["python"],role="TOOL_PYTHON");fingerprint(BASH,role="TOOL_BASH")

def prepare_git_custody(ctx,paths):
    journal=CustodyJournal(ctx,paths)
    try:
        custody_input_preflight(ctx,paths)
        api=WindowsCustody()
        assessment,origins,admitted=inspect_git_candidates(api)
        journal.value["assessment"]=assessment
        journal.emit("ASSESSMENT",{"origins":origins,"admitted":admitted})
        method,index=select_git_policy([{"index":r["index"],"status":r["status"]} for r in assessment])
        target=physical(GIT_CANDIDATES[index])
        journal.value.update(method=method,selected_index=index)
        journal.emit("SELECTION",selection_bound=True)
        work_name=None;kernel=None;provision=None
        with api.directories(target.parent):
            if method=="MATERIALIZED":
                work_name="dg18-iw20-custody-"+ctx["run_id"]+"-1"
                work=target.parent/work_name
                work.mkdir(exist_ok=False);ntfs(work)
                kernel=kernel_custody_controls(api,work/"kernel",ctx)
                journal.emit("FIXTURE_GATE",kernel,kernel_controls_passed=True)
                support_before=support_snapshot(api,target,work_name)
                provision=materialize_same_path(api,target,work,origins[index],journal.emit,callsite="INSTALLED")
            else:support_before=support_snapshot(api,target,None)
            raw,selected=read_regular(target,role="TOOL_GIT")
            with api.opened(target) as h:native,received,sd=api.snapshot(h)
            require(received==raw and native["native"]["links"]==1,"custody postadmission native image")
            if method=="MATERIALIZED":
                exact(native,provision["installed"],"custody installed image changed after close")
            else:exact(selected,admitted[index],"custody existing selection changed")
            support_after=support_snapshot(api,target,work_name)
            exact(support_after,support_before,"custody support closure changed")
            journal.emit("POST_ADMITTED",{"selected":selected,"native":native},
                         original_guard_passed=True,support_unchanged=True,installed_identity_bound=True)
        record={"schema":"dg18.windows20.private-git-selection.v1","context":custody_context(ctx),
                "method":method,"selected_index":index,"selected":selected,"native":native,
                "support":support_after,"work_name":work_name,"kernel_controls":kernel,"provisioning":provision}
        journal.complete(record)
        return record
    except BaseException as error:
        journal.refused(error)
        raise

def load_git_custody(ctx,paths):
    record=read_document(paths["hold"]/"GIT_SELECTION.json",MAX_STATE)
    require(type(record) is dict and set(record)=={"schema","context","method","selected_index","selected",
            "native","support","work_name","kernel_controls","provisioning"}
            and record["schema"]=="dg18.windows20.private-git-selection.v1","custody private selection schema")
    exact(record["context"],custody_context(ctx),"custody private request/code binding")
    require(record["method"] in CUSTODY_REQUIRED and type(record["selected_index"]) is int
            and record["selected_index"] in (0,1),"custody private selection")
    target=physical(GIT_CANDIDATES[record["selected_index"]])
    require(record["selected"]["path"]==str(target),"custody exact allowlisted selection")
    progress=validate_custody_projection(read_document(paths["hold"]/"CUSTODY_PROGRESS.json"),ctx,required=True)
    require(progress["status"]=="ESTABLISHED" and progress["selected_index"]==record["selected_index"]
            and progress["method"]==record["method"]
            and progress["private_record_sha256"]==digest(canonical(record)),"custody receiving complete")
    exact(fingerprint(target,role="TOOL_GIT"),record["selected"],"custody selected physical image changed")
    api=WindowsCustody()
    with api.opened(target) as h:now,raw,sd=api.snapshot(h)
    exact(now,record["native"],"custody native selected image changed")
    exact(support_snapshot(api,target,record["work_name"]),record["support"],"custody support changed during hold")
    return record,progress

@contextmanager
def custody_effect_lease(state,paths):
    """Hold read handles against write/delete while the original hold/GO/effect path runs."""
    record,progress=load_git_custody(state["context"],paths)
    api=WindowsCustody();target=Path(record["selected"]["path"])
    with ExitStack() as stack:
        stack.enter_context(api.directories(target.parent))
        chosen=stack.enter_context(api.opened(target))
        now,raw,sd=api.snapshot(chosen)
        exact(now,record["native"],"custody selected lease identity")
        for name,pin in record["support"]["members"].items():
            handle=stack.enter_context(api.opened(target.parent/name))
            current,raw,sd=api.snapshot(handle)
            exact(current,pin,"custody support lease identity")
        yield

def read_custody_projection(ctx,paths,*,required=False):
    path=paths["hold"]/"CUSTODY_PROGRESS.json"
    if not path.exists():return validate_custody_projection(None,ctx,required=required)
    return validate_custody_projection(read_document(path),ctx,required=required)



def physical(path):
    p=Path(path).absolute()
    require(".." not in p.parts,"parent traversal")
    for node in (p,*p.parents):
        info=node.lstat()
        require(not stat.S_ISLNK(info.st_mode) and not getattr(info,"st_file_attributes",0)&0x400,
                "symlink/reparse path")
    return p.resolve(strict=True)

def read_regular(path, maximum=MAX_FILE, *, role="INTERNAL_RECORD", manifest_index=None):
    validate_shape_selector(role,manifest_index)
    p=physical(path)
    fields=("st_dev","st_ino","st_size","st_mtime_ns","st_ctime_ns",
            "st_mode","st_nlink","st_birthtime_ns","st_file_attributes","st_reparse_tag")
    def stamp(info):
        return {name:getattr(info,name,None) for name in fields}
    def shape(info,stage):
        size=info.st_size
        conditions={"REGULAR_FILE":stat.S_ISREG(info.st_mode),
                    "UNIQUE_LINK":info.st_nlink==1,
                    "NONNEGATIVE_SIZE":size>=0,
                    "WITHIN_EXISTING_BOUND":size<=maximum,
                    "NONREPARSE":not getattr(info,"st_file_attributes",0)&0x400}
        reason="read_regular:"+stage+":file_shape"
        try:
            require(all(conditions.values()),reason)
        except Refusal as error:
            observation={"schema":"dg18.windows20.file-shape-observation.v1",
                         "stage":stage,"role":role,"manifest_index":manifest_index,
                         "conditions":conditions}
            error.shape_observation=validate_shape_observation(observation,"PREDICATE_REFUSED",
                                                               digest(reason.encode("ascii")))
            raise
    def same(left,right,stage):
        for field in fields:
            require(left[field]==right[field],"read_regular:"+stage+":"+field)
    def cross(path_info,handle_info,stage):
        named,handled=stamp(path_info),stamp(handle_info)
        # CPython3.12.10 win32_xstat uses CreationTime for ctime; fstat
        # uses ChangeTime. Each full same-API pair is checked separately.
        # Its path-only execute-bit rule applies exactly to these suffixes.
        if sys.platform=="win32" and str(p).lower().endswith((".exe",".bat",".cmd",".com")):
            handled["st_mode"]|=0o111
        for field in fields:
            if field!="st_ctime_ns":
                require(named[field]==handled[field],"read_regular:"+stage+":"+field)
    before=p.lstat();shape(before,"PATH_BEFORE")
    with p.open("rb") as stream:
        opened=os.fstat(stream.fileno());shape(opened,"HANDLE_OPEN")
        cross(before,opened,"CROSS_OPEN")
        raw=stream.read(maximum+1)
        after=os.fstat(stream.fileno());shape(after,"HANDLE_AFTER")
        current=p.lstat();shape(current,"PATH_AFTER")
        same(stamp(opened),stamp(after),"HANDLE_STABILITY")
        same(stamp(before),stamp(current),"PATH_STABILITY")
        cross(current,after,"CROSS_FINAL")
        require(len(raw)<=maximum and len(raw)==after.st_size,"read_regular:READ_BYTE_COUNT")
    return raw,{"path":str(p),"bytes":len(raw),"sha256":digest(raw),
                "physical":{"api":"fstat","fields":stamp(after)},
                "path_physical":{"api":"lstat","fields":stamp(current)}}


def fingerprint(path, *, role="INTERNAL_RECORD"):
    return read_regular(path,role=role)[1]

def read_document(path, maximum=MAX_DOCUMENT, *, role="CONTROL_RECORD"):
    return parse_document(read_regular(path,maximum,role=role)[0],maximum)

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
    expected_review={"schema":"dg18.windows20.host-review.v1","reviewer":REVIEWER,
                     "independent":True,"verdict":"PASS","findings":[],
                     "preparation_sha256":digest(canonical(preparation)),
                     "original_acceptance":False,**common}
    exact(review,expected_review,"independent exact host review required")
    require(hex_value(go.get("resource_receipt_sha256"),64) and hex_value(go.get("candidate_seal_sha256"),64),
            "actual candidate/resource receipt bindings required")
    expected_go={"schema":"dg18.windows20.root-go.v1","root_author":"/root","decision":"GO_ONCE",
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
        r"https://github\.com/theislampill/IMPLEMENTAUDIT\.md/blob/[0-9a-f]{40}/windows20/[0-9]{1,20}/1/ROOT_GO\.json#sha256=[0-9a-f]{64}",
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
    return {"schema":"dg18.windows20.admission-result.v1","status":"ADMISSION_FAILURE",
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
    save(next_path,{"schema":"dg18.windows20.phase.v1","phase":name,"hold_name":paths["hold"].name})
    os.replace(next_path,target)

def campaign_command(state,paths):
    return [state["context"]["python"],"-I","-X","utf8","-B",
            str(paths["hold"]/"private-invocation/prepare_and_execute.py"),
            "--source",str(paths["source"]),"--python",state["context"]["python"],
            "--git",state["bindings"]["tools"]["git"]["path"],
            "--git-sha256",state["bindings"]["tools"]["git"]["sha256"],"--output",str(paths["out"])]

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
    hold=temp/("dg18-iw20-hold-"+name);out=temp/("dg18-iw20-"+name)
    require(not any(hold.is_relative_to(p) or out.is_relative_to(p) for p in (source,packet_repo)),
            "hold/output must be separated")
    return {"source":source,"packet":packet,"packet_repo":packet_repo,
            "hold":hold,"out":out,"control":hold/"control.git"}

def discover_tools(ctx,paths):
    custody,progress=load_git_custody(ctx,paths)
    git=Path(custody["selected"]["path"])
    return {"python":fingerprint(ctx["python"],role="TOOL_PYTHON"),"git":fingerprint(git,role="TOOL_GIT"),"bash":fingerprint(BASH,role="TOOL_BASH")}

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
    exact(fingerprint(git["path"],role="TOOL_GIT"),git,"held direct Git changed before invocation")
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
    tools=discover_tools(ctx,paths);probe={"context":ctx,"bindings":{"tools":tools}}
    custody,progress=load_git_custody(ctx,paths)
    code_path=paths["packet"]/"CODE_MANIFEST.json"
    code_raw,code_identity=read_regular(code_path,MAX_DOCUMENT,role="CODE_MANIFEST")
    code_doc=parse_document(code_raw)
    require(set(code_doc)=={"schema","source_commit","source_tree","members"} and
            code_doc["schema"]=="dg18.windows20.code-manifest.v1" and
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
    for manifest_index,row in enumerate(rows):
        require(set(row)=={"path","bytes","sha256","git_blob_oid","mode"} and row["mode"]=="100644",
                "code manifest row schema")
        raw,identity=read_regular(paths["packet_repo"]/row["path"],role="CODE_MEMBER",manifest_index=manifest_index)
        require(type(row["bytes"]) is int and identity["bytes"]==row["bytes"] and
                identity["sha256"]==row["sha256"] and blob(raw)==row["git_blob_oid"],"code body differs")
        code[row["path"]]=identity
        additions[row["path"]]={"mode":"100644","oid":blob(raw)}
    require(read_regular(paths["packet"]/"entitlement-reference.txt",32,role="SEALED_ENTITLEMENT")[0]==b"UNGRANTED\n",
            "sealed packet must remain UNGRANTED")
    manifest=read_document(paths["packet"]/"SOURCE_MANIFEST.json",role="SOURCE_MANIFEST")
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
    for manifest_index,row in enumerate(selected):
        require(set(row)=={"path","bytes","sha256","git_blob_oid","git_mode"},"selected source row schema")
        path=row["path"]
        require(path in base and base[path]=={"mode":row["git_mode"],"oid":row["git_blob_oid"]},
                "selected source row differs from actual Git tree")
        raw,identity=read_regular(paths["source"]/path,role="SELECTED_SOURCE",manifest_index=manifest_index)
        require(type(row["bytes"]) is int and len(raw)==row["bytes"] and digest(raw)==row["sha256"]
                and blob(raw)==row["git_blob_oid"],"selected source bytes differ")
        received[path]=identity
    require({p for p in base if p.startswith("skills/")}==
            {p for p in received if p.startswith("skills/")},"all skills closure differs")
    git=Path(tools["git"]["path"])
    exec_path=Path(run_git(probe,paths,paths["source"],"--exec-path",maximum=4096).decode("utf-8").strip())
    require(physical(exec_path)==physical(git.parent.parent/"libexec/git-core"),"custody supported Git exec layout")
    return {"context":ctx,"paths":{k:str(v) for k,v in paths.items()},
            "git_custody":{"record_sha256":digest(canonical(custody)),"projection":progress},
            "tools":tools,"code":code,"code_manifest":code_identity,"source":received,
            "base_tree":base,"packet_tree":packet_tree,
            "volumes":{k:ntfs(paths[k]) for k in ("source","packet_repo","hold")}}

def prepare(source,packet):
    import secrets
    ctx=host_context();paths=resolve_paths(ctx,source,packet)
    paths["hold"].mkdir(exist_ok=False)
    (paths["hold"]/"tmp").mkdir(exist_ok=False)
    mark_phase(paths,"PREPARE_CUSTODY")
    prepare_git_custody(ctx,paths)
    mark_phase(paths,"PREPARE_BINDING")
    bindings=bind_snapshot(ctx,paths)
    iw=time.time_ns();im=time.perf_counter_ns()
    p={"schema":"dg18.windows20.preparation.v1","run_id":ctx["run_id"],"attempt":"1",
       "workflow_commit":ctx["workflow_commit"],"source_commit":SOURCE_COMMIT,"source_tree":SOURCE_TREE,
       "bindings_sha256":digest(canonical(bindings)),"nonce":secrets.token_hex(32),
       "issued_wall_ns":iw,"issued_mono_ns":im,"expires_wall_ns":iw+HOLD_SECONDS*1000000000,
       "expires_mono_ns":im+HOLD_SECONDS*1000000000,"native_started":False,"original_acceptance":False,
       "python_version":"3.12.10","python_architecture":"x64","platform":"Windows",
       "filesystems":["NTFS"],"source_members":99,"code_manifest_sha256":bindings["code_manifest"]["sha256"],
       "tools_sha256":{k:v["sha256"] for k,v in bindings["tools"].items()},
       "original_limits":LIMITS,"inference":False,
       "git_custody":bindings["git_custody"]["projection"]}
    state={"schema":"dg18.windows20.private-state.v1","context":ctx,"preparation":p,"bindings":bindings}
    require(len(canonical(state))<=MAX_STATE and len(canonical(p))<=MAX_DOCUMENT,"preparation record budget")
    save(paths["hold"]/"PRIVATE_STATE.json",state)
    save(paths["hold"]/"PREPARATION.json",p)
    mark_phase(paths,"PREPARATION_RECORDED")
    check_fresh(p)
    return p

def verify_held(state,paths):
    require(state.get("schema")=="dg18.windows20.private-state.v1","private state schema")
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
    prefix="windows20/"+run_id+"/1/"
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
    namespace={"__name__":"dg18_windows20_outer_job","__file__":str(path),"__package__":None}
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
    consumed={"schema":"dg18.windows20.consumed.v1","run_id":p["run_id"],"attempt":"1",
              "workflow_commit":p["workflow_commit"],"preparation_sha256":digest(canonical(p)),
              "GO_sha256":digest(canonical(go)),"control_commit":commit,"nonce":p["nonce"],
              "automatic_retry":False}
    ref="https://github.com/"+REPOSITORY+"/blob/"+commit+"/windows20/"+p["run_id"]+"/1/ROOT_GO.json#sha256="+consumed["GO_sha256"]
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
    with custody_effect_lease(state,paths):
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
            prefix="windows20/"+p["run_id"]+"/1/"
            if mode=="STOP":
                stop=parse_document(run_git(state,paths,paths["control"],"show",commit+":"+prefix+"STOP.json",maximum=MAX_DOCUMENT))
                exact(stop,{"schema":"dg18.windows20.stop.v1","decision":"STOP","root_author":"/root",
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
    diagnostic=None;staged_diagnostic=None;p=None;consumed=False
    if (hold/"FAILURE_CONTEXT.json").exists():
        observed=read_document(hold/"FAILURE_CONTEXT.json")
        require(set(observed)=={"schema","run_id","attempt","workflow_commit","phase","error_class","predicate_sha256","shape_diagnostic","staged_copy_diagnostic"}
                and observed["schema"]=="dg18.windows20.failure-context.v1"
                and observed["run_id"]==ctx["run_id"] and observed["attempt"]=="1"
                and observed["workflow_commit"]==ctx["workflow_commit"],"failure context request/schema")
        require(type(observed["phase"]) is str and observed["phase"] in PHASES
                and type(observed["error_class"]) is str and observed["error_class"] in ERROR_CLASSES,
                "failure context vocabulary")
        require(hex_value(observed["predicate_sha256"],64) if observed["error_class"]=="PREDICATE_REFUSED"
                else observed["predicate_sha256"] is None,"failure context predicate fingerprint")
        failure={k:observed[k] for k in failure}
        diagnostic=validate_shape_diagnostic(observed["shape_diagnostic"],ctx,failure["phase"],
            failure["error_class"],failure["predicate_sha256"])
        staged_diagnostic=validate_staged_copy_diagnostic(observed["staged_copy_diagnostic"],ctx,failure["phase"],
            failure["error_class"],failure["predicate_sha256"])
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
        result={"schema":"dg18.windows20.preparation-refusal.v1","run_id":ctx["run_id"],"attempt":"1",
                "workflow_commit":ctx["workflow_commit"],"source_commit":SOURCE_COMMIT,"source_tree":SOURCE_TREE,
                "status":"PREPARATION_NOT_ESTABLISHED","effect_reach":"UNKNOWN",
                "original_acceptance":False,"automatic_retry":False,**failure}
    custody=read_custody_projection(ctx,paths,required=p is not None or result["phase"]=="PREPARE_CUSTODY")
    result=validate_admission_export({**result,"shape_diagnostic":diagnostic,"custody_diagnostic":custody,
        "staged_copy_diagnostic":staged_diagnostic},ctx,p,consumed)
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
            diagnostic=bind_shape_observation(getattr(observed_exception,"shape_observation",None),ctx,
                failure["phase"],failure["error_class"],failure["predicate_sha256"])
            staged_diagnostic=bind_staged_copy_observation(getattr(observed_exception,"staged_copy_observation",None),ctx,
                failure["phase"],failure["error_class"],failure["predicate_sha256"])
            if not (paths["hold"]/"FAILURE_CONTEXT.json").exists():
                save(paths["hold"]/"FAILURE_CONTEXT.json",{"schema":"dg18.windows20.failure-context.v1",
                     "run_id":ctx["run_id"],"attempt":"1","workflow_commit":ctx["workflow_commit"],
                     "shape_diagnostic":diagnostic,"staged_copy_diagnostic":staged_diagnostic,**failure})
            if (paths["hold"]/"PREPARATION.json").exists() and not (paths["hold"]/"ADMISSION_RESULT.json").exists():
                p=read_document(paths["hold"]/"PREPARATION.json")
                save(paths["hold"]/"ADMISSION_RESULT.json",failure_result(p,(paths["hold"]/"CONSUMED.json").exists(),**failure))
    except BaseException:
        pass

def main():
    global DIAGNOSTIC_WRAPPER_SHA256
    parser=argparse.ArgumentParser()
    parser.add_argument("action",choices=("prepare","wait","export"))
    parser.add_argument("--source",type=Path,required=True)
    parser.add_argument("--diagnostic-wrapper-sha256",required=True)
    args=parser.parse_args();packet=Path(__file__).resolve().parent
    try:
        require(hex_value(args.diagnostic_wrapper_sha256,64),"diagnostic workflow wrapper pin")
        DIAGNOSTIC_WRAPPER_SHA256=args.diagnostic_wrapper_sha256
        if args.action=="prepare":
            prepare(args.source,packet);print("DG18_WINDOWS20_PREPARED")
        elif args.action=="wait":
            result=wait_and_dispatch(args.source,packet)
            print("DG18_WINDOWS20_ADAPTER_RECORDED")
            if result["adapter_exit_code"]!=0:return 1
        else:
            export_result(args.source,packet);print("DG18_WINDOWS20_ADMISSION_EXPORTED")
        return 0
    except BaseException:
        retain_failure(args.source,packet)
        print("DG18_WINDOWS20_REFUSED")
        return 1

if __name__=="__main__":
    raise SystemExit(main())
