"""Independent G3 proof-body consumer, v1 R2.

The pinned native compiler and maintained G1 complete raw receiver are shared
trusted components. This module does not import SCOPE_READER or its validators.
It has no dispatch, producer, controller mutation, provider or grant interface.
execute() is called only by the reviewed host inside its already owned step.
Only that future authenticated execution can create a live receipt. Pure checks
and constructed controls do not create one and do not authenticate native history.
"""
from __future__ import annotations
C5_ENTRYPOINT = 'GenuineC5Session'
C5_SOURCE_REVISION = 'R5_HOSTED_UBUNTU24_RUNTIME_DIRECTORY_MODE_SOURCE_20261110_V8'
SOURCE_FILES = 1766
SOURCE_BYTES = 167022158
import contextlib
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import stat
import time
import types

VERSION = 'dg16.independent-proof-consumer.v1.r2'
SOURCE = '5f899a653df20073ed6691f898d9c9f630f0c100'
TREE = 'e7af9906e32eea314e33bddb7aeaf6bcff9242b0'
SOURCE_PARENT = '32f659266b5a08fddb1a0a398eb3eabf0b20e313'
COMPILER_SHA = '0aa4572a03c7270c538b954d435569b882be59674c9d8275b002402cf9f8d78d'
OWNER_SHA = '9bce5c887cd89c2d2991b84f1bf765787e7a6b75a2eba29a8433c3a6c05f73a3'
SCOPE_SHA = 'b108e81e799ea670efbee41bb51fd6b62d896f4e23517a79388719f82d29a1cd'
ADVERSE_SHA = '484c21f972b0273b5852c7b4ada6f676f9911fe3a89e90a356b5ef0dd7a14f5d'
ROOT, PHASE, JOIN = 'R5_ROOT', 'DG16_CURRENT', 'DG16_COMPONENT_JOIN'
PAIR, SCOPE = 'G1_ORIGINAL_PAIR', 'HOST_SCOPE_RECEIVING'
SELECTED = [PAIR, SCOPE]
ORIGINAL = 'DG16_ORIGINAL48_WITH_GUARDED_EXTERNAL_INTERFACES'
BEFORE = 'WAITING_FOR_G1_AND_HOST_SCOPE'
AFTER = 'SCOPED_RETURNS_RETAINED_ORIGINAL_CELL_OPEN'
CONDITION = 'ACTUAL_ROOT_CONSUMPTION_OF_BOTH_COMPONENT_RETURNS'
NATURAL = 'ORIGINAL_RLGWO_PREREQUISITE_AND_NATURAL_SHAPE_NOT_RECEIVED'
FULL_G2 = 'NOT_DISPATCHED_OR_CONSUMED_IN_THIS_HOST'
OWNER_ARRANGEMENT = 'SELECTIVE_PARALLEL_EXISTING_OWNERS_DG16_SOLE_SHARED_WRITER'
IDS = ['R35-Q06'] + ['R35-L%02d' % n for n in range(1,8)]
SCOPES = dict(zip(IDS, [
 'NATIVE_BOUNDED_FRESH_GOVERNED_EPISODE',
 'MATERIAL_RETURN_ANCESTRY_CURRENT_NATIVE_CAMPAIGN',
 'PREPARATION_SELECTION_WITH_BLOCKED_ADMISSION_EFFECT',
 'FOUR_DIRECTIONS_PARTIAL_JOIN_RECONSIDERATION',
 'ACTUAL_NATURAL_TRANSITION_AND_CONSUMED_USEFUL_PREPARATION',
 'HELD_OUT_INERT_NEGATIVES_WITH_EXACT_SOURCE_APPLICABILITY',
 'NATIVE_CURRENTNESS_AND_BOUNDED_SELECTION_BLOCKS',
 'SCOPED_TRIAD_GUARDS_WITH_STRONGER_CLAIMS_SEPARATE']))
# Exactly the independent finding's fifteen bodies: eleven dynamic, public
# scope, two static inputs, and the ACTUAL first root decision.
PROOFS = {
 'g1_receiving':'RECEIVING.json',
 'g1_preboundary_inputs':'g3/G1_PREBOUNDARY_INPUTS.json',
 'initial_native':'g3/SELECTED_NATIVE.json',
 'dispatch':'g3/DISPATCH.json', 'transition':'g3/TRANSITION.json',
 'join':'g3/JOIN.json', 'recursive_records':'g3/RECURSIVE_RECORD_CHECK.json',
 'final_native':'g3/FINAL_NATIVE.json', 'final_transition':'g3/FINAL_TRANSITION.json',
 'stale_return':'g3/STALE_RETURN.json', 'missing_return':'g3/MISSING_RETURN_CONTROL.json',
 'scope_receiving':'g3/SCOPE_RETURN.json',
 'negative_applicability':'g3/inputs/ADVERSE_APPLICABILITY.json',
 'module':'g3/inputs/SCOPE_READER.py', 'root_consumption':'g3/ROOT_DECISION.json'}
# Seven explicit supporting bodies bind acquired records and the distinct
# original G1 acquisition / canonical descriptor-map roles. No new producer
# output is introduced: g3/inputs/G1_INPUTS.json already exists on the host.
SUPPORT = {
 'results':'g3/RESULTS.json', 'executions':'g3/EXECUTIONS.json',
 'consumptions':'g3/CONSUMPTIONS.json',
 'selected_canonical_inputs':'g3/SELECTED_CANONICAL_INPUTS.json',
 'g1_inputs':'g3/inputs/G1_INPUTS.json',
 'return_native':'g3/RETURN_NATIVE.json', 'consuming_native':'g3/CONSUMING_NATIVE.json'}
CONTROLS = {'initial_request':'G3_ROOT_REQUEST.json', 'final_request':'G3_FINAL_REQUEST.json'}
FILES = PROOFS | SUPPORT | CONTROLS
BODY_MAX = 1024 * 1024
AGGREGATE_MAX = 8 * 1024 * 1024
PUBLIC_MAX = 16384
CONSUMER_SECONDS = 30
FINAL_SECONDS = 60
RESERVE_SECONDS = 180
NODES = {ROOT,PHASE,'CURRENT_SOURCE_RECEIPT','CURRENT_PACKAGE_RECEIPT',PAIR,SCOPE,JOIN,
 'FULL_G2_RECEIVING','DG16_ORIGINAL_RECEIVING','DG17_INTERFACE_SCOPE','DG18_INTERFACE_SCOPE',
 'COMMON_ADOPTION_RECEIVING','RESERVED_SOURCE_ADOPTION','RESERVED_DG16_CERTIFICATION'}
BLOCKED = NODES - {ROOT,PHASE,'CURRENT_SOURCE_RECEIPT','CURRENT_PACKAGE_RECEIPT',PAIR,SCOPE,JOIN}
SELECTED_READS = {
 PAIR:['path:G1_INPUTS.json','path:POLICY.json','path:NATIVE_PREREQUISITE_RECEIVING.json'],
 SCOPE:['path:ORIGINAL_SCOPE.json','path:G1_INPUTS.json','path:POLICY.json','path:SCOPE_READER.py',
        'path:COMPILER_READER.py','path:ADVERSE_APPLICABILITY.json','path:SOURCE_ACQUISITION.json',
        'path:PACKAGE_ROOT_RECEIVING.json','path:PACKAGE_BODY_RECEIVING.json','path:PACKAGE_TERMINAL_RECEIVING.json']}
CANONICAL_NAMES = ('STATE.md','PROTOCOL.md','ROADMAP.md','THINKING.md','sidecars.md','tools.md','context.md','phases/phase-1.md')
# Actual selected-source facts, verified against the original acquisition
# contract and the five source bodies. These do not attest live execution.
EXECUTING_SOURCE_PINS = {'scripts/load-work-graph-c5-executor.py': {'bytes': 56600, 'sha256': '7efaac014d54f640af58eb75ad14bbf87a87c5a053256632a48d63ddd8016b88'}, 'scripts/qualify-work-graph-prefix.py': {'bytes': 53362, 'sha256': 'ff5dbdce5b4419268b0fc11c4659763ad68d40e32f18f721b6093a7dd269b7ab'}, 'scripts/work-graph-c5-inputs.py': {'bytes': 21275, 'sha256': '2befafe8c933467bd6dffbe2d4d27b09b4d6e3b52cab3e1ce680ac061a49310a'}, 'scripts/work-graph-c5-provider-inputs.py': {'bytes': 24898, 'sha256': 'e6cb523c3ce2f59fcdb2a1ed90db75d987ca59456dc423d82aceeeaff01d594f'}, 'scripts/repro-event-capture.py': {'bytes': 87416, 'sha256': 'e1e40d28121f648ab1742ecc169d70e4a1f54054419225a12a696d3ac14f0d08'}, 'scripts/work-graph-completion.py': {'bytes': 29565, 'sha256': '70137df6459caa3eecbf847580a34968d13aa1991eae6208e37ea84e60f556eb'}, 'skills/implementaudit/scripts/compile-work-graph.py': {'bytes': 262144, 'sha256': '0aa4572a03c7270c538b954d435569b882be59674c9d8275b002402cf9f8d78d'}, 'scripts/qualify-work-graph-verifier.py': {'bytes': 268686, 'sha256': '79e3250a654abff1c5c326908875da1fea575686bdfb0c1a291c73bc525ed33b'}, 'scripts/work-graph-c5-live-gate.py': {'bytes': 40531, 'sha256': 'b252d0c1ac55e64caa9d8ed8b45402e0e8a6854227e4681b7ffe612eb5c7c3d5'}, 'scripts/work-graph-c5-executor.py': {'bytes': 107991, 'sha256': 'e6e2a46bc8965b92355fe5f2bab1c90e4bc59c983ddacca70ba67865d3c11c5b'}, 'fixtures/work-graph-c5-inputs/execution-r5-hosted-ubuntu24-python312.json': {'bytes': 8304, 'sha256': '15e71318bfb65427e5f5bb49bd0a7e6f5cf4460618ef1b64d3d598b447646e97'}, 'fixtures/work-graph-c5-inputs/package-r5-hosted-single-copy-python312.json': {'bytes': 9783, 'sha256': 'c13127d28bf98d8ca192e6bb2de8be5fc9d515b9cef3d88319c45166528fe430'}, 'fixtures/work-graph-c5-inputs/genuine-r5-hosted-ubuntu24-runtime-directory-mode-execution-profile.json': {'bytes': 9327, 'sha256': '5a70e74151d2daa2813a7ee3b3ca1188a76ceb3d3354af01a35b30a1f1ecfaa0'}}
PREDICATES = (
 'CLOSED_BODY_POPULATION', 'EXACT_REQUEST_RUN_ATTEMPT_NONCE_SOURCE',
 'ACTUAL_G1_SMALL_BODY_JOIN', 'PUBLIC_SCOPE_BODY_JOIN',
 'ROOT_FIRST_DECISION_EXACT_BYTES_AND_SCOPE', 'ORIGINAL_OBLIGATIONS_RETAINED',
 'SOURCE_DOCUMENT_GRAPH_REPLAY', 'TWO_PROSPECTIVE_DISJOINT_WRITERS',
 'ORIGINAL_PREREQUISITE_DONE_EVIDENCE_BOUND', 'ORIGINAL_SELECTED_READ_AND_INVALIDATOR_CONTRACT',
 'DECLARED_KNOWN_INPUT_BODIES_BOUND', 'G1_ACQUISITION_AND_CANONICAL_DESCRIPTOR_ROLES_SEPARATE',
 'SHARED_SOURCE_NO_INDEPENDENT_RESULTS_CREDIT', 'DECLARED_ANCESTRY_AND_GUARDED_SIBLINGS',
 'PROSPECTIVE_DISPATCH_REDERIVED', 'RETURN_RECORDS_BOUND_TO_ACQUIRED_OUTPUTS',
 'REQUIRED_JOIN_REDERIVED', 'RECURSIVE_RECORDS_REDERIVED',
 'CANONICAL_PREBOUNDARY_BODY_JOIN', 'G0001_TO_G0002_SCOPE_SEPARATION',
 'FINAL_SOURCE_REDERIVATION', 'OLD_RETURN_RECOMPUTE_REDERIVED',
 'MISSING_RETURN_PENDING_REDERIVED', 'STATIC_MODULE_AND_APPLICABILITY_PINNED',
 'MAINTAINED_COMPLETE_G1_RAW_READBACK_BOOKENDS', 'FRESH_NATIVE_G0002_OBSERVATION_BOOKENDS',
 'EXACT_INPUT_PHYSICAL_AND_BYTE_BOOKENDS', 'ORIGINAL_SHARED_DEADLINE_AND_RESERVE_PRESERVED')
LIMITS = {
 'selected_dynamic_bodies':11,'selected_proof_bodies':15,'support_bodies':7,
 'request_bodies':2,'additional_pinned_source_bodies':4,'total_input_bodies':28,'body_bytes':BODY_MAX,'aggregate_bytes':AGGREGATE_MAX,
 'consumer_seconds':30,'first_hold_seconds':300,'shared_seconds':600,
 'resume_reserve_seconds':180,'final_decision_seconds':60,
 'producer_watchdog_seconds':120,'producer_cpu_seconds':90,'core_seconds':1800}
LIMITATIONS = [
 'SHARED_TRUSTED_COMPILER_NOT_INDEPENDENT_COMPILER_IMPLEMENTATION',
 'SHARED_MAINTAINED_G1_COMPLETE_RAW_RECEIVER_NOT_SECOND_PRODUCER_RUN',
 'HISTORICAL_G0001_AUTHENTICITY_REQUIRES_EXISTING_HOST_CUSTODY_AND_ROOT_CONTROL',
 'NATIVE_PROCESS_PROVENANCE_REQUIRES_AUTHENTICATED_HOST_EXPORT_AND_REVIEWED_CODE',
 'SERIALIZED_RECEIPT_ALONE_DOES_NOT_AUTHENTICATE_EXECUTION',
 'PURE_RECURSIVE_CHECK_IS_NOT_NATIVE_CAMPAIGN_ATTESTATION',
 'HISTORICAL_ADVERSE_RECORD_IS_NOT_NEW_EPISODE_SPECIFIC_APPLICABILITY',
 'AUTHOR_INDEPENDENCE_REQUIRES_GOVERNOR_ASSIGNMENT_NOT_PROCESS_NAMING']

class Refusal(Exception):
    """Fixed refusal code only; never expose arbitrary private input strings."""

def require(ok, code):
    if not ok:
        raise Refusal(code)

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',',':'), ensure_ascii=True, allow_nan=False)+'\n').encode('ascii')

def digest(value):
    require(type(value) is str and re.fullmatch('[0-9a-f]{64}',value) is not None,'DIGEST_REFUSED')
    return value

def integer(value, low, high):
    require(type(value) is int and low <= value <= high,'INTEGER_REFUSED')
    return value

def exact(value, fields):
    require(type(value) is dict and set(value)==set(fields),'CLOSED_SCHEMA_REFUSED')

def parse(raw, *, canonical=False, maximum=BODY_MAX):
    require(type(raw) is bytes and 0 < len(raw) <= maximum,'BODY_BOUND_REFUSED')
    def pairs(rows):
        result={}
        for key,value in rows:
            require(key not in result,'DUPLICATE_KEY_REFUSED')
            result[key]=value
        return result
    try:
        value=json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:require(False,'NONFINITE_REFUSED'))
    except (ValueError,UnicodeError,RecursionError) as exc:
        raise Refusal('JSON_REFUSED') from exc
    def walk(v,depth=0):
        require(depth<=48,'JSON_DEPTH_REFUSED')
        if isinstance(v,dict):
            require(len(v)<=4096,'JSON_POPULATION_REFUSED')
            for x in v.values():walk(x,depth+1)
        elif isinstance(v,list):
            require(len(v)<=4096,'JSON_POPULATION_REFUSED')
            for x in v:walk(x,depth+1)
        elif isinstance(v,str):require(len(v)<=512*1024,'JSON_STRING_BOUND_REFUSED')
        elif v is not None:require(type(v) in (int,bool),'JSON_SCALAR_REFUSED')
    walk(value)
    if canonical:require(encode(value)==raw,'CANONICAL_BYTES_REFUSED')
    return value

def descriptor(raw):
    return {'bytes':len(raw),'sha256':sha(raw)}

def stamp(s):
    return [s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_uid,s.st_gid]

class Population:
    """Finite no-follow ordinary-file acquisition with ancestor identity fences."""
    def __init__(self, root, clock_check=lambda:None):
        self.root=Path(root).absolute()
        self.clock_check=clock_check
        self.records={}
        self.total=0
    def _ancestry(self, path):
        require(path.is_absolute() and '..' not in path.parts,'PATH_REFUSED')
        result=[]
        for parent in reversed(path.parents):
            s=parent.lstat()
            require(stat.S_ISDIR(s.st_mode) and not parent.is_symlink(),'ANCESTRY_REFUSED')
            # Directory size/mtime can change for sibling command capture files.
            # Retain identity, mode, ownership and link count, not population time.
            result.append([s.st_dev,s.st_ino,s.st_mode,s.st_uid,s.st_gid,s.st_nlink])
        return result
    def read(self, key, relative, *, maximum=BODY_MAX):
        self.clock_check()
        require(key not in self.records and type(relative) is str and
                not relative.startswith('/') and '..' not in Path(relative).parts,'MEMBER_REFUSED')
        path=self.root/relative
        ancestors=self._ancestry(path)
        s=path.lstat()
        require(stat.S_ISREG(s.st_mode) and s.st_nlink==1 and 0<s.st_size<=maximum,'ORDINARY_FILE_REFUSED')
        fd=os.open(path,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK|os.O_CLOEXEC)
        try:
            require(stamp(os.fstat(fd))==stamp(s) and not os.listxattr(fd),'FILE_OPEN_REFUSED')
            with os.fdopen(fd,'rb',closefd=False) as stream:raw=stream.read(maximum+1)
            require(len(raw)==s.st_size and stamp(os.fstat(fd))==stamp(s) and
                    stamp(path.lstat())==stamp(s) and self._ancestry(path)==ancestors,'FILE_CLOSING_REFUSED')
        finally:os.close(fd)
        self.total+=len(raw)
        require(self.total<=AGGREGATE_MAX,'AGGREGATE_REFUSED')
        self.records[key]={'relative':relative,'physical':stamp(s),'ancestors':ancestors,**descriptor(raw)}
        self.clock_check()
        return raw
    def close(self):
        self.clock_check()
        for key,row in self.records.items():
            other=Population(self.root,self.clock_check)
            raw=other.read(key,row['relative'],maximum=max(row['bytes'],1))
            require(other.records[key]==row and sha(raw)==row['sha256'],'BOOKEND_CHANGED')
        self.clock_check()
        return {'schema':'dg16.independent-proof-bookends.v1', 'members':self.records,
                'aggregate_bytes':self.total,'closing_exact':True}

INITIAL_FIELDS = '''schema authority source_commit source_tree source_parent run_id attempt nonce control_branch control_path root join original_scope_sha256 graph_sha256 dispatch_sha256 transition_sha256 join_sha256 scope_return_sha256 g1_return_sha256 complete_input_key returned_nodes issued_unix_ms expires_unix_ms hold_seconds shared_expires_unix_ms shared_window_seconds decision_before decision_after original_total original_awards full_g2 status'''.split()
SCOPE_FIELDS = '''schema authority source_commit source_tree run_id attempt graph_sha256 dispatch_sha256 original_scope_sha256 complete_input_key selected_tracked_source_files selected_tracked_source_bytes scope_obligations ancestors actual_complete_source_files actual_complete_source_bytes selected required_join root node_count original_total observed_affinity_count capacity_units host_capacity operator_ceiling reserve active_owned_task_slots independence owner_arrangement received_input_bodies natural_transition full_g2 original_awards future_adoption result root_decision_before'''.split()
G1_FIELDS = '''schema authority source_commit source_tree status original_G1_award original_acceptance actual_raw_comparison_sha256 operation_result_sha256 same_checkout_current original_operation_complete private_raw_publication'''.split()
FINAL_FIELDS = '''schema authority source_commit source_tree source_parent run_id attempt nonce control_branch control_path original_scope_sha256 initial_request_sha256 proofs initial_graph_sha256 final_graph_sha256 continuity_generation current_receipt_sha256 component_return_nodes consumed_join root actual_stale_result final_selected original_ids original_scopes g1_facts retained_original_total g1_input_scope g1_complete_input_key g3_current_scope input_change_reason actual_original_awards original_scope v041_admission global_liveness retirement_or_transfer full_g2 whole_DG16_awarded shared_window_started_unix_ms issued_unix_ms expires_unix_ms shared_window_seconds status'''.split()
ROOT_FIELDS = '''schema issuer action request_sha256 run_id attempt nonce source_commit source_tree graph_sha256 dispatch_sha256 join_sha256 consumed_nodes outputs decision_before decision_after owner_arrangement original_awards full_g2 issued_unix_ms expires_unix_ms'''.split()
PIN_FIELDS = '''schema source_commit source_tree scope_sha256 adverse_sha256 compiler_sha256 owner_sha256 scope_module_sha256 consumer_sha256 initial_control_branch'''.split()

def pins_contract(pins):
    exact(pins,PIN_FIELDS)
    require(pins['schema']=='dg16.independent-consumer-pins.v1' and pins['source_commit']==SOURCE and pins['source_tree']==TREE and
            pins['scope_sha256']==SCOPE_SHA and pins['adverse_sha256']==ADVERSE_SHA and
            pins['compiler_sha256']==COMPILER_SHA and pins['owner_sha256']==OWNER_SHA,'TRUSTED_SOURCE_PIN_REFUSED')
    for key in ('scope_module_sha256','consumer_sha256'):digest(pins[key])
    require(type(pins['initial_control_branch']) is str and re.fullmatch(r'pro/[A-Za-z0-9][A-Za-z0-9/_-]{0,180}',pins['initial_control_branch']) and
            '..' not in pins['initial_control_branch'] and '//' not in pins['initial_control_branch'],'CONTROL_BRANCH_REFUSED')
    return pins

def source_identity(value):
    require(value.get('source_commit')==SOURCE and value.get('source_tree')==TREE,'SOURCE_IDENTITY_REFUSED')

def validate_first(initial_raw,scope_raw,g1_raw,pins,scope_basis):
    """Root can consume the actual small G1 body at the FIRST hold."""
    pins_contract(pins)
    require(sha(encode(scope_basis))==SCOPE_SHA,'ORIGINAL_SCOPE_BASIS_REFUSED')
    initial=parse(initial_raw,canonical=True,maximum=8192)
    scope=parse(scope_raw,canonical=True,maximum=PUBLIC_MAX)
    g1=parse(g1_raw,canonical=True,maximum=4096)
    exact(initial,INITIAL_FIELDS);exact(scope,SCOPE_FIELDS);exact(g1,G1_FIELDS)
    for item in (initial,scope,g1):source_identity(item);require(item['authority']=='NONE','AUTHORITY_REFUSED')
    require(initial['schema']=='dg16.g3-root-consumption-request.v2' and initial['source_parent']==SOURCE_PARENT,
            'INITIAL_SCHEMA_REFUSED')
    require(type(initial['run_id']) is str and re.fullmatch('[1-9][0-9]{5,19}',initial['run_id']) and
            initial['attempt']==1 and type(initial['attempt']) is int and re.fullmatch('[0-9a-f]{32}',initial['nonce']),
            'RUN_ATTEMPT_NONCE_REFUSED')
    require(initial['control_branch']==pins['initial_control_branch'] and
            initial['control_path']=='qualification/dg16-r5-g3/ROOT_DECISION.json' and
            initial['root']==ROOT and initial['join']==JOIN and initial['original_scope_sha256']==SCOPE_SHA,'INITIAL_ROUTE_REFUSED')
    for key in ('graph_sha256','dispatch_sha256','transition_sha256','join_sha256','scope_return_sha256','g1_return_sha256','complete_input_key'):
        digest(initial[key])
    start=integer(initial['issued_unix_ms'],1,10**16)
    hold=integer(initial['hold_seconds'],60,300);shared=integer(initial['shared_window_seconds'],180,600)
    require(initial['expires_unix_ms']==start+hold*1000 and initial['shared_expires_unix_ms']==start+shared*1000 and hold<=shared-120,
            'INITIAL_WINDOW_REFUSED')
    require(initial['returned_nodes']==SELECTED and initial['decision_before']==BEFORE and initial['decision_after']==AFTER and
            initial['original_total']==157 and type(initial['original_awards']) is int and initial['original_awards']==0 and
            initial['full_g2']==FULL_G2 and initial['status']=='ROOT_REQUEST_READY','INITIAL_SCOPE_REFUSED')
    require(all(type(g1[k]) is bool for k in ('original_G1_award','original_acceptance','same_checkout_current','original_operation_complete','private_raw_publication')),
            'G1_BODY_REFUSED')
    require(g1==dict(schema='dg16.g1-live-receiving.v1',authority='NONE',source_commit=SOURCE,source_tree=TREE,
        status='RECEIVED_AT_PROSPECTIVE_COMPONENT_SCOPE',original_G1_award=False,original_acceptance=False,
        actual_raw_comparison_sha256=digest(g1['actual_raw_comparison_sha256']),operation_result_sha256=digest(g1['operation_result_sha256']),
        same_checkout_current=True,original_operation_complete=True,private_raw_publication=False),'G1_BODY_REFUSED')
    require(sha(g1_raw)==initial['g1_return_sha256'] and sha(scope_raw)==initial['scope_return_sha256'],'FIRST_RETURN_JOIN_REFUSED')
    require(scope['schema']=='dg16.g3-host-scope-receiving.v2' and scope['run_id']==initial['run_id'] and type(scope['attempt']) is int and scope['attempt']==1,
            'SCOPE_RUN_REFUSED')
    for key in ('graph_sha256','dispatch_sha256','complete_input_key','original_scope_sha256'):
        require(scope[key]==initial[key],'SCOPE_REQUEST_JOIN_REFUSED')
    fixed=dict(selected_tracked_source_files=SOURCE_FILES,selected_tracked_source_bytes=SOURCE_BYTES,node_count=14,original_total=157,
        selected=SELECTED,ancestors=[PAIR,PHASE,ROOT],required_join=JOIN,root=ROOT,original_awards=0,full_g2=FULL_G2,
        natural_transition=NATURAL,future_adoption='SEPARATE_GUARDED_RECEIVING_AND_OWNER_DECISION',
        root_decision_before=BEFORE,result='HOST_SPECIFIC_OBLIGATION_CLOSURE_RECEIVED',
        capacity_units='HOST_TASK_EXECUTION_SLOTS_NOT_AGENT_OR_JOB_SLOTS',host_capacity=2,operator_ceiling=2,reserve=0,
        active_owned_task_slots=0,independence='DISJOINT_WRITERS_SHARED_SOURCE_BASELINE_NO_DOUBLE_CREDIT',owner_arrangement=OWNER_ARRANGEMENT)
    for key,wanted in fixed.items():require(type(scope[key]) is type(wanted) and scope[key]==wanted,'SCOPE_CONTRACT_REFUSED')
    integer(scope['observed_affinity_count'],2,4096)
    integer(scope['actual_complete_source_files'],1759,4096)
    integer(scope['actual_complete_source_bytes'],166407881,256*1024**2)
    require(scope['received_input_bodies']=={k:v['sha256'] for k,v in scope_basis['received_inputs'].items()},'RECEIVED_INPUT_BODIES_REFUSED')
    obligations=[]
    for cell,consumer,condition in [
        ('DG16','DG16_ORIGINAL_RECEIVING','ACTIVE_TARGET_ORIGINAL_QUALIFICATION_REMAINS'),
        ('DG17','DG17_INTERFACE_SCOPE','INDEPENDENT_EXTERNAL_OWNER_CE057_INTERFACE_ONLY'),
        ('DG18','DG18_INTERFACE_SCOPE','INDEPENDENT_EXTERNAL_OWNER_CE051_CHANGED_INPUT_ONLY')]:
        obligations.append(dict(cell=cell,count=scope_basis['original_population'][cell],original_ids_sha256=sha(encode(scope_basis['original_ids'][cell])),
            consumer=consumer,condition=condition,state='RETAINED_SCOPE_NOT_EXECUTED_BY_THIS_HOST'))
    require(scope['scope_obligations']==obligations,'ORIGINAL_OBLIGATIONS_REFUSED')
    return initial,scope,g1

def validate_root(raw,initial_raw,initial):
    root=parse(raw,canonical=True,maximum=8192);exact(root,ROOT_FIELDS)
    require(root['schema']=='dg16.g3-root-consumption-decision.v2' and root['issuer']=='R5_ROOT_GOVERNOR' and
            root['action']=='CONSUME_COMPONENT_RETURNS_ONLY' and root['request_sha256']==sha(initial_raw),'ROOT_CONTROL_REFUSED')
    for key in ('run_id','attempt','nonce','source_commit','source_tree','graph_sha256','dispatch_sha256','join_sha256','decision_before','decision_after','full_g2','expires_unix_ms'):
        require(type(root[key]) is type(initial[key]) and root[key]==initial[key],'ROOT_REQUEST_BINDING_REFUSED')
    require(root['consumed_nodes']==SELECTED and root['outputs']=={PAIR:initial['g1_return_sha256'],SCOPE:initial['scope_return_sha256']} and
            root['owner_arrangement']==OWNER_ARRANGEMENT and type(root['original_awards']) is int and root['original_awards']==0,'ROOT_SCOPE_REFUSED')
    integer(root['issued_unix_ms'],initial['issued_unix_ms'],initial['expires_unix_ms'])
    return root

G1_FACT_FIELDS = """schema source_commit source_tree native_prerequisite_profile native_prerequisite_receiving_sha256 native_predicates native_prerequisite_scope raw_receiving_sha256 actual_dispatches validated_actual_events retained_artifacts original_children_exit_codes producer_closing_sha256 maintained_elapsed_ns enclosing_elapsed_ns zero_subtracted_ns producer_watchdog_seconds per_process_cpu_seconds watchdog_events cleanup_errors wait4_reaped process_group_absent measured_outer_wait4_max_rss_kib max_rss_scope runtime_mounted_bytes runtime_unique_bytes runtime_logical_bytes actual_source_files actual_source_bytes runtime_physical_limit_bytes source_acquisition_limit_bytes image_readback operation_scope producer_original48_qualification whole_DG16_awarded""".split()

def bounded_g1_facts(value,initial):
    # Facts are admitted as bounded host statements and joined to the maintained
    # receiver. Their numeric values are not claimed as independent measurements.
    exact(value,G1_FACT_FIELDS);source_identity(value)
    fixed=dict(schema='dg16.g3-g1-actual-facts.v2',actual_dispatches=2,validated_actual_events=38,retained_artifacts=12,
        original_children_exit_codes=[0,0],zero_subtracted_ns=0,producer_watchdog_seconds=120,
        per_process_cpu_seconds=90,watchdog_events=0,cleanup_errors=0,wait4_reaped=True,process_group_absent=True,
        runtime_physical_limit_bytes=128*1024**2,source_acquisition_limit_bytes=256*1024**2,
        native_prerequisite_profile='DG16_8EE4_LINUX_CHANGED_NATIVE_BINDING_V1',
        native_predicates=['fixed_receiver_identity','wrong_receiver_refusal','current_native_intake','later_invalidation_refusal','host_and_diagnosed_intake'],
        native_prerequisite_scope='ACTUALLY_CONSUMED_G0001_PREDICATES',
        max_rss_scope='ACTUAL_OUTER_WAIT4_OBSERVATION_NOT_WINDOWS_WHOLE_JOB',
        image_readback='COMPLETE_CAPTURED_SOURCE_RUNTIME_BYTES_MODES_ALIASES',
        operation_scope='PROSPECTIVE_GENUINE_ORIGINAL19_SHARED_IMAGE_PAIR',producer_original48_qualification=False,whole_DG16_awarded=False)
    for k,v in fixed.items():require(type(value[k]) is type(v) and value[k]==v,'G1_FACT_SCOPE_REFUSED')
    require(all(type(x) is int for x in value['original_children_exit_codes']),'G1_FACT_SCOPE_REFUSED')
    for k in ('native_prerequisite_receiving_sha256','raw_receiving_sha256','producer_closing_sha256'):digest(value[k])
    require(value['raw_receiving_sha256']==initial['g1_return_sha256'],'G1_FACT_SCOPE_REFUSED')
    for k in ('maintained_elapsed_ns','enclosing_elapsed_ns'):integer(value[k],0,1800*10**9)
    integer(value['measured_outer_wait4_max_rss_kib'],0,2**63-1)
    for k in ('runtime_mounted_bytes','runtime_unique_bytes'):integer(value[k],1,128*1024**2)
    integer(value['runtime_logical_bytes'],1,2**63-1)
    integer(value['actual_source_files'],1759,4096);integer(value['actual_source_bytes'],166407881,256*1024**2)

def validate_final(raw,initial_raw,initial,bodies,pins):
    final=parse(raw,canonical=True,maximum=PUBLIC_MAX);exact(final,FINAL_FIELDS);source_identity(final)
    require(final['schema']=='dg16.g3-original-receiving-request.v2' and final['authority']=='NONE' and
            final['source_parent']==SOURCE_PARENT and final['control_branch']==pins['initial_control_branch'] and
            final['control_path']=='qualification/dg16-r5-g3/ORIGINAL_DECISION.json' and final['original_scope_sha256']==SCOPE_SHA,
            'FINAL_IDENTITY_REFUSED')
    for key in ('run_id','attempt','nonce'):require(type(final[key]) is type(initial[key]) and final[key]==initial[key],'FINAL_EPISODE_REFUSED')
    require(final['initial_request_sha256']==sha(initial_raw) and final['g1_complete_input_key']==initial['complete_input_key'], 'FINAL_FIRST_REQUEST_REFUSED')
    exact(final['proofs'],PROOFS)
    require(final['proofs']=={key:sha(bodies[key]) for key in PROOFS},'FINAL_PROOF_BODY_JOIN_REFUSED')
    expected=dict(continuity_generation='G0002',component_return_nodes=SELECTED,consumed_join=JOIN,root=ROOT,
        actual_stale_result='RECOMPUTE_REQUIRED',final_selected=[],original_ids=IDS,original_scopes=SCOPES,retained_original_total=157,
        g1_input_scope='ACTUALLY_CONSUMED_G0001_COMPLETE_SOURCE_GIT_HIDDEN_AND_RUNTIME',
        g3_current_scope='CURRENT_G0002_AFTER_SUPPORTED_ROOT_CONSUMPTION_AND_REDERIVATION',
        input_change_reason='ACTUAL_CAPTURE_INCLUDES_CANONICAL_FILES_CHANGED_BY_ROOT_JOIN_AND_OWNER_GENERATION',
        actual_original_awards='ROOT_DECISION_PENDING',
        original_scope='EXACT_ORIGINAL_ID_AND_GATE_DECISIONS_REQUIRE_ROOT_AND_INDEPENDENT_APPLICABILITY',
        v041_admission='PENDING_NOT_GRANTED_BY_THIS_EPISODE',global_liveness='NOT_ESTABLISHED',retirement_or_transfer='NOT_PERFORMED',
        full_g2=FULL_G2,whole_DG16_awarded=False,status='FINAL_ROOT_DECISION_REQUIRED_WHILE_CURRENT')
    for key,wanted in expected.items():require(type(final[key]) is type(wanted) and final[key]==wanted,'FINAL_SCOPE_REFUSED')
    for key in ('initial_graph_sha256','final_graph_sha256','current_receipt_sha256'):digest(final[key])
    require(final['shared_window_started_unix_ms']==initial['issued_unix_ms'] and final['expires_unix_ms']==initial['shared_expires_unix_ms'] and
            final['shared_window_seconds']==initial['shared_window_seconds'],'SHARED_WINDOW_RESET_REFUSED')
    integer(final['issued_unix_ms'],initial['issued_unix_ms'],final['expires_unix_ms']-1)
    require(type(final['g1_facts']) is dict and len(encode(final['g1_facts']))<=8192,'G1_FACTS_BOUND_REFUSED')
    bounded_g1_facts(final['g1_facts'],initial)
    return final

def graph_contract(graph,run,completed=False,scope_basis=None):
    """Independent original-contract predicates, not producer validator reuse."""
    require(graph['root']==ROOT and graph['campaign']=='DG16_SUCCESSOR_G3_HOST_'+run and
            graph['original_scope']==ORIGINAL and graph['authority']=='NONE','GRAPH_SCOPE_REFUSED')
    exact(graph['context'],('host_capacity','operator_ceiling','reserve','route_facts','outstanding_deliveries'))
    require(graph['context']==dict(host_capacity=2,operator_ceiling=2,reserve=0,route_facts=[],outstanding_deliveries=[]),
            'GRAPH_CAPACITY_REFUSED')
    require(graph['event']==dict(id='g3-current-'+run+('-root-join' if completed else '-prospective-selection'),
        kind='JOIN' if completed else 'REDERIVE',subject=JOIN if completed else PAIR),'GRAPH_EVENT_REFUSED')
    nodes={x['id']:x for x in graph['nodes']}
    require(set(nodes)==NODES and len(graph['nodes'])==len(NODES),'NODE_POPULATION_REFUSED')
    require(set(graph['source_documents'])=={'STATE.md','ROADMAP.md','phases/phase-1.md'},'SOURCE_DOCUMENT_POPULATION_REFUSED')
    expected_parent={ROOT:None,PHASE:ROOT}
    for name in NODES-{ROOT,PHASE}:expected_parent[name]=ROOT if name in {
        'DG17_INTERFACE_SCOPE','DG18_INTERFACE_SCOPE','COMMON_ADOPTION_RECEIVING','RESERVED_SOURCE_ADOPTION','RESERVED_DG16_CERTIFICATION'} else PHASE
    for name,node in nodes.items():
        require(node['parent']==expected_parent[name] and node['independence']=='KNOWN' and node['optional']==[] and
                node['independent_results'] is False,'TOPOLOGY_OR_INDEPENDENCE_REFUSED')
        if name in BLOCKED:require(node['authorization']=='MISSING' and node['state']=='BLOCKED' and 'AUTHORIZATION' in node['blocked_reasons'],
                                  'GUARDED_SCOPE_REFUSED')
        if name in (ROOT,PHASE):require(node['state']!='DONE','PARENT_CREDIT_REFUSED')
    require(nodes[ROOT]['kind']=='PLAN' and nodes[PHASE]['kind']=='PHASE' and nodes[JOIN]['kind']=='JOIN','ANCESTRY_KIND_REFUSED')
    require(nodes[JOIN]['requires']==SELECTED and nodes['DG16_ORIGINAL_RECEIVING']['requires']==[JOIN,'FULL_G2_RECEIVING'] and
            nodes['COMMON_ADOPTION_RECEIVING']['requires']==['CURRENT_SOURCE_RECEIPT','CURRENT_PACKAGE_RECEIPT'], 'JOIN_TOPOLOGY_REFUSED')
    require(nodes['RESERVED_SOURCE_ADOPTION']['effect']=='EXTERNAL' and nodes['RESERVED_DG16_CERTIFICATION']['effect']=='EXTERNAL',
            'RESERVED_EFFECT_REFUSED')
    for name,write in ((PAIR,'semantic:g1-private-owned-operation'),(SCOPE,'semantic:host-scope-receiving-output')):
        node=nodes[name]
        require(node['effect']=='PREPARATION' and node['writes']==[write] and node['future_consumer']==dict(node=JOIN,condition=CONDITION) and
                node['state']==('DONE' if completed else 'READY'),'PREPARATION_SCOPE_REFUSED')
    require(nodes[PAIR]['requires']==[] and nodes[SCOPE]['requires']==['CURRENT_SOURCE_RECEIPT','CURRENT_PACKAGE_RECEIPT'],
            'PREPARATION_PREREQUISITE_REFUSED')
    # Source replay establishes self-consistency, not agreement with the
    # original contract. Bind these facts independently at BOTH graph stages.
    require(type(scope_basis) is dict and sha(encode(scope_basis))==SCOPE_SHA,'ORIGINAL_SCOPE_BASIS_REFUSED')
    for name,body in (('CURRENT_SOURCE_RECEIPT','SOURCE_ACQUISITION.json'),
                      ('CURRENT_PACKAGE_RECEIPT','PACKAGE_ROOT_RECEIVING.json')):
        node=nodes[name]
        require(node['state']==node['declared_state']=='DONE' and
                node['done_evidence']==scope_basis['received_inputs'][body]['sha256'],
                'ORIGINAL_PREREQUISITE_EVIDENCE_REFUSED')
        require(node['kind']=='TASK' and node['effect']=='READ_ONLY' and node['authorization']=='PERMITTED' and
                node['requires']==node['reads']==node['invalidators']==node['writes']==node['authority']==[],
                'ORIGINAL_PREREQUISITE_DECLARATION_REFUSED')
    for name,reads in SELECTED_READS.items():
        require(nodes[name]['reads']==reads and nodes[name]['invalidators']==[],
                'ORIGINAL_SELECTED_INPUT_DECLARATION_REFUSED')
    for name,condition in [('DG17_INTERFACE_SCOPE','CE057_CURRENT_RUN_TURN_INTERFACE_ONLY'),
                           ('DG18_INTERFACE_SCOPE','CE051_MATERIALLY_AFFECTED_SHARED_INPUT_ONLY')]:
        require(nodes[name]['authority']==['scope:NOT_DELEGATED_TO_THIS_DG16_HOST'] and
                nodes[name]['future_consumer']['condition']==condition,'SIBLING_SCOPE_REFUSED')
    return nodes

def original_policy(run):
    """Original bounded input policy, independently stated from its contract.

    These 16/64 MiB values describe the producer's pre-existing input policy;
    they do not replace this consumer's unchanged 1/8 MiB acquisition caps.
    """
    return dict(schema='dg16.g3-prospective-policy.v2',source_commit=SOURCE,source_tree=TREE,
        source_parent=SOURCE_PARENT,run_id=run,attempt=1,original_scope_sha256=SCOPE_SHA,
        capacity_units='HOST_TASK_EXECUTION_SLOTS_NOT_AGENT_OR_JOB_SLOTS',host_capacity=2,
        operator_ceiling=2,reserve=0,active_owned_task_slots=0,
        execution_order=['HOST_SCOPE_RECEIVING_BEFORE_TIMED_C5','G1_ORIGINAL_PAIR'],
        independence='DISJOINT_WRITERS_SHARED_SOURCE_BASELINE_NO_DOUBLE_CREDIT',
        input_limits=dict(file_bytes=16*1024**2,total_bytes=64*1024**2,entries=4096,depth=16),
        full_source_reader='MAINTAINED_GENUINE_C5_SESSION_ACQUIRE_WITH_UNCHANGED_BOUNDS',
        selected_tracked_source_files=SOURCE_FILES,selected_tracked_source_bytes=SOURCE_BYTES,
        original_awards=0,full_g2=False,owner_arrangement=OWNER_ARRANGEMENT,
        natural_transition=NATURAL,c5_entrypoint=C5_ENTRYPOINT,
        c5_source_revision=C5_SOURCE_REVISION,
        timing_scope='PRODUCER_WATCHDOG120_CPU90_ENCLOSING_INTERVAL_MEASURED_SEPARATELY_NO_SUBTRACTION')

def known_input_contract(selected,current,bodies,scope_basis,initial,final):
    """Join all eleven declared input identities without importing a validator.

    The four received-input hashes have intentionally distinct historical
    roles fixed by ORIGINAL_SCOPE. A package receipt is not relabeled as a
    new selected-source package run. The native prerequisite hash remains a
    joined, bounded host fact, not an independent native qualification award.
    """
    known={
        'ORIGINAL_SCOPE.json':SCOPE_SHA, 'G1_INPUTS.json':sha(bodies['g1_inputs']),
        'POLICY.json':sha(encode(original_policy(initial['run_id']))),
        'SCOPE_READER.py':sha(bodies['module']), 'COMPILER_READER.py':COMPILER_SHA,
        'ADVERSE_APPLICABILITY.json':ADVERSE_SHA,
        'NATIVE_PREREQUISITE_RECEIVING.json':final['g1_facts']['native_prerequisite_receiving_sha256']}
    known.update({name:row['sha256'] for name,row in scope_basis['received_inputs'].items()})
    expected={'path:'+name:dict(status='PRESENT_FILE',sha256=value) for name,value in known.items()}
    require(len(expected)==11,'ORIGINAL_DECLARED_INPUT_POPULATION_REFUSED')
    for graph in (selected,current):
        require(graph['binding']['read_set']==expected,'ORIGINAL_KNOWN_INPUT_BODY_REFUSED')

def canonical_input_contract(bodies,initial,selected):
    """Receive the actual eight-entry map and the separate G1 acquisition body.

    Only the initial G0001 source documents match this map. Final G0002
    documents are intentionally changed by root consumption. The complete
    raw G1 receiver and source/currentness mechanisms remain shared trust.
    """
    acquired=parse(bodies['g1_inputs'],canonical=True);exact(acquired,('key','observation'))
    observation=acquired['observation'];require(type(observation) is dict,'G1_ACQUISITION_SHAPE_REFUSED')
    require(observation.get('source_commit')==SOURCE and observation.get('source_tree')==TREE,
            'G1_ACQUISITION_SOURCE_REFUSED')
    provider=observation.get('provider')
    require(type(provider) is dict and type(provider.get('source')) is dict and
            provider['source'].get('projection')=='ALL_ACTUAL_BYTES_NO_GIT_OR_HIDDEN_OMISSIONS',
            'G1_ACQUISITION_PROJECTION_REFUSED')
    executing=observation.get('executing_sources')
    require(type(executing) is dict and executing==EXECUTING_SOURCE_PINS,
            'G1_ACQUISITION_EXECUTING_SOURCE_REFUSED')
    acquisition_raw=json.dumps(observation,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf-8')+b'\n'
    require(acquired['key']==initial['complete_input_key']==sha(acquisition_raw),'COMPLETE_CANONICAL_INPUT_KEY_REFUSED')
    canonical=parse(bodies['selected_canonical_inputs'],canonical=True);exact(canonical,CANONICAL_NAMES)
    for row in canonical.values():
        exact(row,('bytes','sha256'));integer(row['bytes'],1,96*1024);digest(row['sha256'])
    require(sum(row['bytes'] for row in canonical.values())<=256*1024,'CANONICAL_POPULATION_BOUND_REFUSED')
    files=observation
    for key in ('provider','source','state','files'):
        require(type(files) is dict and key in files,'G1_CANONICAL_CAPTURE_SHAPE_REFUSED');files=files[key]
    require(type(files) is dict,'G1_CANONICAL_CAPTURE_SHAPE_REFUSED')
    require(all(type(row) is dict and type(row.get('bytes')) is int and row['bytes']>=0
                for row in files.values()),'G1_SOURCE_CENSUS_SHAPE_REFUSED')
    source_count=len(files);source_bytes=sum(row['bytes'] for row in files.values())
    require(type(provider.get('actual_source_files')) is int and type(provider.get('actual_source_bytes')) is int and
            provider['actual_source_files']==source_count and provider['actual_source_bytes']==source_bytes,
            'G1_SOURCE_CENSUS_REFUSED')
    scope=parse(bodies['scope_receiving'],canonical=True)
    require(scope['actual_complete_source_files']==source_count and scope['actual_complete_source_bytes']==source_bytes,
            'SCOPE_SOURCE_CENSUS_JOIN_REFUSED')
    roots={name[:-len('/STATE.md')] for name in files if re.fullmatch(r'\.IMPLEMENTAUDIT/runs/r5-g1-hosted-[A-Za-z0-9]{6}/STATE\.md',name)}
    matches=[]
    for root in roots:
        if all(type(files.get(root+'/'+name)) is dict and
               {field:files[root+'/'+name].get(field) for field in ('bytes','sha256')}==row
               for name,row in canonical.items()):matches.append(root)
    require(len(matches)==1,'CANONICAL_CAPTURE_BODY_JOIN_REFUSED')
    for name,source_text in selected['source_documents'].items():
        require(canonical[name]==descriptor(source_text.encode('utf-8')),'CANONICAL_INITIAL_SOURCE_JOIN_REFUSED')
    return matches[0]

def check_bodies(bodies,pins,scope_basis,engine):
    """Pure source/body/contract rederivation. Never creates a live receipt."""
    exact(bodies,FILES)
    require(sum(map(len,bodies.values()))<=AGGREGATE_MAX and all(0<len(x)<=BODY_MAX for x in bodies.values()),'POPULATION_BOUND_REFUSED')
    pins_contract(pins)
    require(sha(bodies['module'])==pins['scope_module_sha256'] and sha(bodies['negative_applicability'])==ADVERSE_SHA,
            'STATIC_APPLICABILITY_PIN_REFUSED')
    adverse=parse(bodies['negative_applicability'],canonical=True)
    require(adverse['compiler_sha256']==COMPILER_SHA and adverse['authority']=='NONE' and adverse['errors']==0 and adverse['failures']==0 and
        adverse['evidence_scope']=='CONSTRUCTED_DATA_AND_INERT_ADAPTER_CONTROLS_NO_NATIVE_CAMPAIGN_CREDIT','ADVERSE_SCOPE_REFUSED')
    initial,scope,g1=validate_first(bodies['initial_request'],bodies['scope_receiving'],bodies['g1_receiving'],pins,scope_basis)
    decision=validate_root(bodies['root_consumption'],bodies['initial_request'],initial)
    final=validate_final(bodies['final_request'],bodies['initial_request'],initial,bodies,pins)
    records={key:parse(raw) for key,raw in bodies.items() if key not in {'module'} and key not in CONTROLS}
    selected_wrapper=records['initial_native'];final_wrapper=records['final_native']
    for wrapper in (selected_wrapper,final_wrapper,records['return_native'],records['consuming_native']):
        exact(wrapper,('schema','projection','continuity_sources','continuity_closure'))
        require(wrapper['schema']=='implementaudit.native-run-source-observation.v2','NATIVE_WRAPPER_REFUSED')
    selected=selected_wrapper['projection'];current=final_wrapper['projection']
    # Direct trusted native interface replays source_documents and rejects a
    # merely resealed projection before these independent policy predicates.
    dispatch=engine.select_native_frontier_v1(selected)
    nodes=graph_contract(selected,initial['run_id'],scope_basis=scope_basis)
    finalnodes=graph_contract(current,initial['run_id'],True,scope_basis)
    require(dispatch==records['dispatch'] and dispatch['selected']==SELECTED and dispatch['authority']=='NONE' and
            dispatch['graph_required'] is True and dispatch['capacity']==2 and dispatch['active_occupancy']==0 and dispatch['free_capacity']==2,
            'DISPATCH_REDERIVATION_REFUSED')
    transition=engine.compile_recursive_transition_v1(selected,[])
    require(transition==records['transition'] and transition['ancestors']==[PAIR,PHASE,ROOT] and transition['selected']==SELECTED,
            'TRANSITION_REDERIVATION_REFUSED')
    require(initial['graph_sha256']==selected['digest'] and initial['dispatch_sha256']==sha(encode(dispatch)) and
            initial['transition_sha256']==transition['digest'] and initial['join_sha256']==sha(bodies['join']),
            'INITIAL_GRAPH_REQUEST_JOIN_REFUSED')
    require(final['initial_graph_sha256']==selected['digest'] and final['final_graph_sha256']==current['digest'],
            'FINAL_GRAPH_REQUEST_JOIN_REFUSED')
    sb,cb=selected['binding'],current['binding']
    for key in ('controller','claim','candidate_head','candidate_tree','continuity_helper_digest','input_root_identity','read_set'):
        require(sb[key]==cb[key],'NATIVE_IDENTITY_DRIFT_REFUSED')
    for key in ('return_native','consuming_native'):
        require(records[key]==selected_wrapper,'RETURN_NATIVE_CHANGED_REFUSED')
    known_input_contract(selected,current,bodies,scope_basis,initial,final)
    # Exact private module and applicability must be inputs to both graphs.
    for name,key in [('SCOPE_READER.py','module'),('ADVERSE_APPLICABILITY.json','negative_applicability')]:
        require(sb['read_set']['path:'+name]==dict(status='PRESENT_FILE',sha256=sha(bodies[key])), 'DECLARED_INPUT_BODY_REFUSED')
    require(sb['read_set']['path:ORIGINAL_SCOPE.json']==dict(status='PRESENT_FILE',sha256=SCOPE_SHA) and
            sb['read_set']['path:COMPILER_READER.py']==dict(status='PRESENT_FILE',sha256=COMPILER_SHA),'TRUSTED_INPUT_SOURCE_REFUSED')
    expected_results=[];expected_executions=[]
    for name,bodykey,independence_key in [(PAIR,'g1_receiving','ACTUAL_G1_OWNER'),(SCOPE,'scope_receiving','ACTUAL_DISTINCT_SCOPE_RECEIVER')]:
        n=nodes[name];output=sha(bodies[bodykey])
        expected_results.append(dict(schema='implementaudit.work-result.v1',node=name,dispatch_id=dispatch['dispatch_id'],
            graph_digest=selected['digest'],input_digest=n['input_digest'],status='PASS',terminal=True,exit_code=0,
            evidence_digest=output,independence_key=independence_key,scope=[name]))
        expected_executions.append(dict(node=name,dispatch_id=dispatch['dispatch_id'],graph_digest=selected['digest'],
            input_digest=n['input_digest'],input_root_identity=sb['input_root_identity'],
            read_set={p:sb['read_set'][p] for p in n['reads']+n['invalidators'] if p.startswith('path:')},output_digest=output,exit_code=0))
    require(records['results']==expected_results and records['executions']==expected_executions,'ACTUAL_RETURN_RECORD_BINDING_REFUSED')
    consumptions=[dict(node=x['node'],consumer=JOIN,condition=CONDITION,input_digest=x['input_digest'],input_root_identity=x['input_root_identity'],
        read_set_digest=sha(engine.canonical_json_v1(x['read_set'])),output_digest=x['output_digest'],decision_before=decision['decision_before'],
        decision_after=decision['decision_after']) for x in expected_executions]
    require(records['consumptions']==consumptions,'ACTUAL_CONSUMPTION_RECORD_BINDING_REFUSED')
    joined=engine.reconcile_native_results_v1(selected,selected,dispatch,records['results'],JOIN)
    require(joined==records['join'] and joined['status']=='SATISFIED_AT_DECLARED_RESULT_CONTRACT' and
            joined['authority']=='NONE' and joined['lifecycle_credit']=='NONE','JOIN_REDERIVATION_REFUSED')
    recursive=engine.check_recursive_execution_v1(selected,[],transition,records['executions'],records['consumptions'])
    require(recursive==records['recursive_records'] and recursive['status']=='PORTABLE_RECORDS_CONSUMED' and
            recursive['native_campaign_proven'] is False and recursive['consumed']==SELECTED,'RECURSIVE_REDERIVATION_REFUSED')
    final_transition=engine.compile_recursive_transition_v1(current,[recursive['event_receipt']])
    require(final_transition==records['final_transition'] and final_transition['selected']==[] and final_transition['ancestors']==[JOIN,PHASE,ROOT],
            'FINAL_FRONTIER_REDERIVATION_REFUSED')
    for name,bodykey in ((PAIR,'g1_receiving'),(SCOPE,'scope_receiving'),(JOIN,'join')):
        require(finalnodes[name]['state']=='DONE' and finalnodes[name]['done_evidence']==sha(bodies[bodykey]),'DONE_OUTPUT_BINDING_REFUSED')
    stale=engine.reconcile_native_results_v1(selected,current,dispatch,records['results'],JOIN)
    missing=engine.reconcile_native_results_v1(selected,selected,dispatch,records['results'][:1],JOIN)
    require(stale==records['stale_return'] and stale['status']=='RECOMPUTE_REQUIRED' and all(n in stale['invalidated'] for n in SELECTED),
            'OLD_RETURN_REDERIVATION_REFUSED')
    require(missing==records['missing_return'] and missing['status']=='PENDING' and missing['missing']==[SCOPE],
            'MISSING_RETURN_REDERIVATION_REFUSED')
    selected_run_root=canonical_input_contract(bodies,initial,selected)
    pre=records['g1_preboundary_inputs'];exact(pre,('scope','complete_input_key','current_generation','root_consumption_decision_sha256',
        'actual_canonical_population_sha256','g1_receiving_sha256','complete_readback_before_and_after_raw_receiver'))
    require(pre==dict(scope='ACTUAL_MAINTAINED_ACQUIRE_ALL_SOURCE_GIT_HIDDEN_AND_RUNTIME',complete_input_key=initial['complete_input_key'],
        current_generation='G0001',root_consumption_decision_sha256=sha(bodies['root_consumption']),
        actual_canonical_population_sha256=sha(bodies['selected_canonical_inputs']),g1_receiving_sha256=initial['g1_return_sha256'],
        complete_readback_before_and_after_raw_receiver=True),'PREBOUNDARY_BODY_JOIN_REFUSED')
    return {'initial':initial,'final':final,'selected':selected,'current':current,
            'initial_wrapper':selected_wrapper,'final_wrapper':final_wrapper,
            'root_decision':decision,'scope':scope,'g1':g1,'adverse':adverse,'selected_run_root':selected_run_root}

def native_identity(result,controller,receipt):
    a=result['selected']['binding'];b=result['current']['binding']
    require(type(controller) is str and type(receipt) is str,'NATIVE_CALLER_IDENTITY_REFUSED')
    for binding,generation in ((a,'G0001'),(b,'G0002')):
        require(binding['acquisition']=='NATIVE_CONTINUITY_VERIFIED' and binding['controller']==controller and
                binding['epoch']==generation and binding['candidate_head']==SOURCE and binding['candidate_tree']==TREE and
                binding['continuity_helper_digest']==OWNER_SHA,'NATIVE_IDENTITY_REFUSED')
        require(re.fullmatch('refs/implementaudit/continuity-receipts/'+re.escape(controller)+'/'+generation+r'@[0-9a-f]{40}',binding['receipt']),
                'NATIVE_RECEIPT_SHAPE_REFUSED')
    require(b['receipt']==receipt and a['receipt']!=receipt and result['final']['current_receipt_sha256']==sha(receipt.encode('ascii')),
            'CURRENT_NATIVE_RECEIPT_REFUSED')

@contextlib.contextmanager
def bounded_timer(seconds):
    """Shorten inherited real timer; restoration preserves its original endpoint."""
    started=time.monotonic()
    previous=signal.getitimer(signal.ITIMER_REAL)
    require(previous[1]==0,'PERIODIC_TIMER_REFUSED')
    endpoint=started+previous[0] if previous[0]>0 else None
    # A live host must already own a finite enclosing alarm.
    require(endpoint is not None,'OWNED_ENCLOSING_TIMER_REQUIRED')
    signal.setitimer(signal.ITIMER_REAL,min(seconds,previous[0]))
    try:yield
    finally:
        signal.setitimer(signal.ITIMER_REAL,max(0.000001,endpoint-time.monotonic()))

def write_once(path,raw):
    path=Path(path)
    fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600)
    try:
        with os.fdopen(fd,'wb',closefd=False) as stream:stream.write(raw);stream.flush();os.fsync(fd)
    finally:os.close(fd)
    checker=Population(path.parent);require(checker.read('output',path.name,maximum=max(len(raw),1))==raw,'OUTPUT_READBACK_REFUSED')

def execute(api,pins):
    """Future live-only host entry. No CLI fallback, no replay/inert receipt mode.

    api is the existing reviewed g3_api with source/private/run_root,
    receipt/controller, enclosing deadline and the exact maintained callbacks.
    Root integration must pin this source and the pin record, preserve both
    maintained G1 function bodies, and authenticate exported output via R2.
    """
    pins_contract(pins)
    required={'source','private','run_root','controller','receipt','deadline_monotonic','require_current','verify_g1_retained'}
    require(type(api) is dict and required<=set(api) and callable(api['require_current']) and callable(api['verify_g1_retained']),
            'BOUND_HOST_API_REQUIRED')
    run_id=os.environ.get('GITHUB_RUN_ID','')
    require(re.fullmatch('[1-9][0-9]{5,19}',run_id) and os.environ.get('GITHUB_RUN_ATTEMPT')=='1' and
            api['controller']=='r5-g1-hosted-'+run_id+'-a1','LIVE_RUN_BINDING_REQUIRED')
    require(type(api['run_root']) is str and re.fullmatch(r'\.IMPLEMENTAUDIT/runs/r5-g1-hosted-[A-Za-z0-9]{6}',api['run_root']),
            'LIVE_RUN_ROOT_REQUIRED')
    private=Path(api['private']).absolute();source=Path(api['source']).absolute();run_root=source/api['run_root']
    require(source!=private and source not in private.parents and private not in source.parents and
            os.getuid()==os.geteuid()==os.getgid()==os.getegid()==0,'OWNED_HOST_ROOTS_REQUIRED')
    require(private.is_dir() and source.is_dir() and run_root.is_dir(),'HOST_ROOTS_REQUIRED')
    began_mono=time.monotonic();began_ns=time.monotonic_ns();began_wall=int(time.time()*1000)
    initial=parse(Population(private).read('initial','G3_ROOT_REQUEST.json',maximum=8192),canonical=True)
    shared_end=initial['shared_expires_unix_ms']
    require(shared_end-began_wall>=(CONSUMER_SECONDS+FINAL_SECONDS)*1000 and
            api['deadline_monotonic']-began_mono>=RESERVE_SECONDS+CONSUMER_SECONDS+FINAL_SECONDS,'PROSPECTIVE_BUDGET_REFUSED')
    def check_clock():
        require(time.monotonic()-began_mono<=CONSUMER_SECONDS and int(time.time()*1000)+FINAL_SECONDS*1000<=shared_end and
                time.monotonic()+RESERVE_SECONDS+FINAL_SECONDS<=api['deadline_monotonic'],'CONSUMER_DEADLINE_REFUSED')
    with bounded_timer(CONSUMER_SECONDS):
        check_clock();api['require_current']('independent-proof-before-currentness')
        owned=Population(Path(__file__).absolute().parent,check_clock)
        own=owned.read('consumer',Path(__file__).name)
        require(sha(own)==pins['consumer_sha256'],'CONSUMER_SOURCE_PIN_REFUSED')
        trusted=Population(source,check_clock)
        compiler_raw=trusted.read('compiler','skills/implementaudit/scripts/compile-work-graph.py')
        owner_raw=trusted.read('owner','skills/implementaudit/scripts/claim-run.sh')
        require(sha(compiler_raw)==COMPILER_SHA and sha(owner_raw)==OWNER_SHA,'TRUSTED_SOURCE_BYTES_REFUSED')
        engine=types.ModuleType('dg16_independent_trusted_native_compiler')
        engine.__file__=str(source/'skills/implementaudit/scripts/compile-work-graph.py')
        exec(compile(compiler_raw,engine.__file__,'exec'),engine.__dict__)
        population=Population(private,check_clock)
        bodies={key:population.read(key,path,maximum=8192 if key=='initial_request' else PUBLIC_MAX if key=='final_request' else BODY_MAX)
                for key,path in FILES.items()}
        scope_raw=population.read('original_scope','g3/inputs/ORIGINAL_SCOPE.json',maximum=65536)
        require(sha(scope_raw)==SCOPE_SHA,'ORIGINAL_SCOPE_BYTES_REFUSED')
        basis=parse(scope_raw,canonical=True)
        require(population.total+trusted.total+owned.total<=AGGREGATE_MAX,'TOTAL_AGGREGATE_REFUSED')
        g1_before=api['verify_g1_retained']()
        require(g1_before==sha(bodies['g1_receiving']),'MAINTAINED_G1_FIRST_READBACK_REFUSED');check_clock()
        result=check_bodies(bodies,pins,basis,engine)
        require(result['initial']['run_id']==run_id,'HOST_RUN_BINDING_REFUSED')
        require(result['selected_run_root']==api['run_root'],'G1_CANONICAL_RUN_ROOT_REFUSED')
        native_identity(result,api['controller'],api['receipt'])
        native_hashes=[]
        for ordinal in (0,1):
            check_clock();api['require_current']('independent-proof-native-'+str(ordinal)+'-before')
            with engine.observe_native_run_sources_v2(run_root,source,input_root=private/'g3/inputs') as native_raw:
                observed=parse(native_raw)
                require(observed==result['final_wrapper'],'FRESH_NATIVE_BODY_REFUSED')
            # Context manager closing guards have NOW completed.
            api['require_current']('independent-proof-native-'+str(ordinal)+'-after')
            native_hashes.append(sha(native_raw));check_clock()
            if ordinal==0:
                require(api['verify_g1_retained']()==g1_before,'MAINTAINED_G1_LAST_READBACK_REFUSED');check_clock()
        api['require_current']('independent-proof-closing-currentness');check_clock()
        private_bookends=population.close();source_bookends=trusted.close();own_bookends=owned.close()
        bookends={'schema':'dg16.independent-proof-input-bookends.v1','private':private_bookends,
            'trusted_sources':source_bookends,'consumer':own_bookends,'native_observation_sha256':native_hashes,
            'maintained_g1_receiving_sha256':[g1_before,g1_before]}
        bookends_raw=encode(bookends)
        require(len(bookends_raw)<=256*1024,'BOOKEND_BOUND_REFUSED')
        finished_ns=time.monotonic_ns();finished_wall=int(time.time()*1000)
        receipt={
            'schema':'dg16.independent-proof-consumption-receipt.v1','consumer':VERSION,'authority':'NONE',
            'source_commit':SOURCE,'source_tree':TREE,'run_id':run_id,'attempt':1,'nonce':result['initial']['nonce'],
            'initial_request_sha256':sha(bodies['initial_request']),'final_request_sha256':sha(bodies['final_request']),
            'first_root_decision_sha256':sha(bodies['root_consumption']),
            'proof_bodies':{k:descriptor(bodies[k]) for k in PROOFS},'support_bodies':{k:descriptor(bodies[k]) for k in SUPPORT},
            'bookends_sha256':sha(bookends_raw),'bookends_bytes':len(bookends_raw),
            'consumer_sha256':pins['consumer_sha256'],'scope_module_sha256':pins['scope_module_sha256'],
            'compiler_sha256':COMPILER_SHA,'owner_sha256':OWNER_SHA,'original_scope_sha256':SCOPE_SHA,'adverse_sha256':ADVERSE_SHA,
            'initial_graph_sha256':result['selected']['digest'],'final_graph_sha256':result['current']['digest'],
            'current_receipt_sha256':sha(api['receipt'].encode('ascii')),
            'predicate_results':{name:'OBSERVED_TRUE' for name in PREDICATES},
            'native_observation_sha256':native_hashes,'maintained_g1_receiving_sha256':g1_before,
            'started_unix_ms':began_wall,'finished_unix_ms':finished_wall,'elapsed_ns':finished_ns-began_ns,
            'shared_expires_unix_ms':shared_end,'final_decision_remaining_ms':shared_end-finished_wall,
            'enclosing_reserve_remaining_ms':int((api['deadline_monotonic']-time.monotonic())*1000),
            'aggregate_input_bytes':population.total+trusted.total+owned.total,'limits':LIMITS,
            'measurement_scope':'ENTRY_THROUGH_INPUT_CLOSURE_OUTPUT_PERSISTENCE_CHARGED_BY_ENCLOSING_HOST',
            'budget_scope':'ORIGINAL_SHARED_WINDOW_AND_CORE_INTERVAL_NO_RESET_OR_SUBTRACTION',
            'evidence_scope':'ACTUALLY_EXECUTED_SOURCE_BOUND_SEMANTIC_BODY_CONSUMPTION',
            'status':'OBSERVATIONS_RETAINED_FOR_ROOT_AND_INDEPENDENT_REVIEW',
            'original_rows':{name:'PARTIAL_REQUIRES_EPISODE_SPECIFIC_ROOT_AND_INDEPENDENT_APPLICABILITY' for name in IDS},
            'natural_L04':'NOT_RECEIVED','full_G2':'NOT_RECEIVED','whole_DG16':'NOT_AWARDED',
            'global_liveness':'NOT_ESTABLISHED','retirement_or_transfer':'NOT_PERFORMED',
            'original_awards':[],'review_or_admission_issued':False,'limitations':LIMITATIONS}
        receipt_raw=encode(receipt);validate_receipt(receipt_raw,bodies['initial_request'],bodies['final_request'],bodies['root_consumption'],pins)
        require(len(receipt_raw)<=PUBLIC_MAX,'PUBLIC_RECEIPT_BOUND_REFUSED')
        check_clock()
        write_once(private/'g3/INDEPENDENT_INPUT_BOOKENDS.json',bookends_raw)
        write_once(private/'G3_INDEPENDENT_PROOF_RECEIPT.json',receipt_raw)
        require(population.close()==private_bookends and trusted.close()==source_bookends and owned.close()==own_bookends,
                'OUTPUT_INTERVAL_BOOKEND_CHANGED')
        check_clock()
        return receipt

RECEIPT_FIELDS = '''schema consumer authority source_commit source_tree run_id attempt nonce initial_request_sha256 final_request_sha256 first_root_decision_sha256 proof_bodies support_bodies bookends_sha256 bookends_bytes consumer_sha256 scope_module_sha256 compiler_sha256 owner_sha256 original_scope_sha256 adverse_sha256 initial_graph_sha256 final_graph_sha256 current_receipt_sha256 predicate_results native_observation_sha256 maintained_g1_receiving_sha256 started_unix_ms finished_unix_ms elapsed_ns shared_expires_unix_ms final_decision_remaining_ms enclosing_reserve_remaining_ms aggregate_input_bytes limits measurement_scope budget_scope evidence_scope status original_rows natural_L04 full_G2 whole_DG16 global_liveness retirement_or_transfer original_awards review_or_admission_issued limitations'''.split()

def validate_receipt(raw,initial_raw,final_raw,actual_root_raw,pins):
    """Closed root-side intake only. Authentication/review is external and mandatory."""
    pins_contract(pins);r=parse(raw,canonical=True,maximum=PUBLIC_MAX);exact(r,RECEIPT_FIELDS)
    initial=parse(initial_raw,canonical=True,maximum=8192);final=parse(final_raw,canonical=True,maximum=PUBLIC_MAX)
    exact(initial,INITIAL_FIELDS);exact(final,FINAL_FIELDS)
    validate_root(actual_root_raw,initial_raw,initial)
    for value in (r,initial,final):source_identity(value)
    fixed={'schema':'dg16.independent-proof-consumption-receipt.v1','consumer':VERSION,'authority':'NONE',
        'consumer_sha256':pins['consumer_sha256'],'scope_module_sha256':pins['scope_module_sha256'],
        'compiler_sha256':COMPILER_SHA,'owner_sha256':OWNER_SHA,'original_scope_sha256':SCOPE_SHA,'adverse_sha256':ADVERSE_SHA,
        'limits':LIMITS,'measurement_scope':'ENTRY_THROUGH_INPUT_CLOSURE_OUTPUT_PERSISTENCE_CHARGED_BY_ENCLOSING_HOST',
            'budget_scope':'ORIGINAL_SHARED_WINDOW_AND_CORE_INTERVAL_NO_RESET_OR_SUBTRACTION',
        'evidence_scope':'ACTUALLY_EXECUTED_SOURCE_BOUND_SEMANTIC_BODY_CONSUMPTION',
        'status':'OBSERVATIONS_RETAINED_FOR_ROOT_AND_INDEPENDENT_REVIEW','natural_L04':'NOT_RECEIVED','full_G2':'NOT_RECEIVED',
        'whole_DG16':'NOT_AWARDED','global_liveness':'NOT_ESTABLISHED','retirement_or_transfer':'NOT_PERFORMED',
        'original_awards':[],'review_or_admission_issued':False,'limitations':LIMITATIONS,
        'original_rows':{name:'PARTIAL_REQUIRES_EPISODE_SPECIFIC_ROOT_AND_INDEPENDENT_APPLICABILITY' for name in IDS},
        'predicate_results':{name:'OBSERVED_TRUE' for name in PREDICATES}}
    for key,wanted in fixed.items():require(type(r[key]) is type(wanted) and r[key]==wanted,'RECEIPT_CLOSED_SCOPE_REFUSED')
    for key in ('run_id','attempt','nonce'):require(type(r[key]) is type(initial[key]) and r[key]==initial[key]==final[key],'RECEIPT_EPISODE_REFUSED')
    require(r['initial_request_sha256']==sha(initial_raw) and r['final_request_sha256']==sha(final_raw) and
            r['first_root_decision_sha256']==sha(actual_root_raw) and final['initial_request_sha256']==sha(initial_raw), 'RECEIPT_REQUEST_JOIN_REFUSED')
    exact(r['proof_bodies'],PROOFS);exact(r['support_bodies'],SUPPORT);exact(final['proofs'],PROOFS)
    for key,row in (r['proof_bodies']|r['support_bodies']).items():
        exact(row,('bytes','sha256'));integer(row['bytes'],1,BODY_MAX);digest(row['sha256'])
        if key in PROOFS:require(row['sha256']==final['proofs'][key],'RECEIPT_PROOF_JOIN_REFUSED')
    require(r['proof_bodies']['module']['sha256']==pins['scope_module_sha256'] and
            r['proof_bodies']['negative_applicability']['sha256']==pins['adverse_sha256'],
            'RECEIPT_STATIC_PIN_JOIN_REFUSED')
    require(r['proof_bodies']['g1_receiving']['sha256']==initial['g1_return_sha256']==r['maintained_g1_receiving_sha256'] and
            r['proof_bodies']['scope_receiving']['sha256']==initial['scope_return_sha256'] and
            r['proof_bodies']['root_consumption']==descriptor(actual_root_raw),'RECEIPT_RETURN_JOIN_REFUSED')
    for key in ('initial_graph_sha256','final_graph_sha256','current_receipt_sha256'):
        require(r[key]==final[key],'RECEIPT_NATIVE_JOIN_REFUSED')
    require(r['initial_graph_sha256']==initial['graph_sha256'],'RECEIPT_INITIAL_GRAPH_REFUSED')
    digest(r['bookends_sha256']);integer(r['bookends_bytes'],1,256*1024)
    require(type(r['native_observation_sha256']) is list and len(r['native_observation_sha256'])==2 and
            r['native_observation_sha256'][0]==r['native_observation_sha256'][1]==final['proofs']['final_native'],'RECEIPT_NATIVE_OBSERVATION_REFUSED')
    start=integer(r['started_unix_ms'],final['issued_unix_ms'],initial['shared_expires_unix_ms'])
    end=integer(r['finished_unix_ms'],start,initial['shared_expires_unix_ms'])
    integer(r['elapsed_ns'],0,CONSUMER_SECONDS*10**9)
    require(end-start<=CONSUMER_SECONDS*1000 and r['shared_expires_unix_ms']==initial['shared_expires_unix_ms']==final['expires_unix_ms'] and
            r['final_decision_remaining_ms']==initial['shared_expires_unix_ms']-end and r['final_decision_remaining_ms']>=FINAL_SECONDS*1000 and
            type(r['enclosing_reserve_remaining_ms']) is int and r['enclosing_reserve_remaining_ms']>=(RESERVE_SECONDS+FINAL_SECONDS)*1000,
            'RECEIPT_DEADLINE_REFUSED')
    integer(r['aggregate_input_bytes'],sum(v['bytes'] for v in (r['proof_bodies']|r['support_bodies']).values())+len(initial_raw)+len(final_raw),AGGREGATE_MAX)
    return r

if __name__=='__main__':
    raise SystemExit('BOUND_HOST_API_REQUIRED')
