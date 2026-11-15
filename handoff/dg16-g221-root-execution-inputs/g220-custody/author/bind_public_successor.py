"""Pure public receiver source binding. No paths are opened and no input code runs.

Root must authenticate issuer, physical path receiving, actual decisions and
distinct-review provenance outside this API. Matching data is never authority.
Returned bytes are preparation, not an effect grant or private-role binding.
"""
import ast
import hashlib
import json
import re
from pathlib import PurePosixPath, PureWindowsPath

ISSUER='01a1cf82-cdd6-7053-b7b7-32f5c3d93d21'
# One exact actual current Root source adoption; never a native effect grant.
RETAINED_HOST_ADOPTION_ISSUER = '01a1cf82-cdd6-7053-b7b7-32f5c3d93d21'
RETAINED_HOST_ADOPTION_SHA256 = '99d3315c8c8cd894f66dc04bfebb7a5519abe232fca3f4205d90a8690e6180df'
SOURCE = '205aeab7c93299b0666b261485ab5658d8e183de'
TREE = '9ffbaf95080092bf4a45b8772a97ed16068544a7'
PREFIX='qualification/dg16-r5-full-g2/'
FROZEN = {'public_receiver.py': '5bb8d71aa40e2a4d842ddd178b31257eef496ca3c0073461e8328d2e64560f5e', 'admission_gate.py': '4bbb432df0c76334719600793412ae4425b0dfd3b7c4b3892bea10b9b5854481', 'native_public.py': 'fd97a976fe9ef7a7a57f599aec5f037305a9c7050bde0e7a5236676f7e599eff'}
TEMPLATE_PINS = {'adfcf7b001b49ceb8df20a772829a56514f4e40801fb05d84a2fbd0b8a52478a'}
DECISIONS=('INDEPENDENT_COLD_REVIEW.json','ROOT_POLICY_ADOPTION.json','NATIVE_INDEPENDENT_REVIEW.json','ROOT_NATIVE_APPLICABILITY_ADOPTION.json')
DIGEST_FIELDS='candidate_seal_sha256 code_review_seal_sha256 composition_seal_sha256 composition_sha256 native_gate_sha256 native_review_seal_sha256 policy_gate_sha256 public_adoption_sha256 public_native_adoption_sha256 public_native_review_sha256 public_review_sha256'.split()

def need(ok,code):
    if not ok:raise ValueError(code)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def desc(raw):return dict(bytes=len(raw),sha256=sha(raw))
def encode(value):return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=True,allow_nan=False)+'\n').encode('ascii')
def parse(raw):
    need(type(raw) is bytes and 0<len(raw)<=1024**2,'INPUT_BYTES_BOUND')
    def pairs(rows):
        out={}
        for k,v in rows:need(k not in out,'DUPLICATE_KEY');out[k]=v
        return out
    try:value=json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:need(False,'NONFINITE'))
    except (TypeError,RecursionError,UnicodeError) as exc:raise ValueError('JSON_SHAPE') from exc
    need(type(value) is dict,'JSON_OBJECT');return value
def digest(value,length=64):return type(value) is str and re.fullmatch('[0-9a-f]{'+str(length)+'}',value) is not None and value!='0'*length
def exact(value,keys):need(type(value) is dict and set(value)==set(keys.split()),'FIELDS')
def path(value):
    need(type(value) is str and 0<len(value)<=4096 and not any(c in value for c in ('\0','\n','\r')),'PUBLIC_PATH')
    p=PurePosixPath(value) if value.startswith('/') else PureWindowsPath(value)
    need(p.is_absolute() and '..' not in p.parts and (str(p)==value or p.as_posix()==value),'PUBLIC_ABSOLUTE_CANONICAL_PATH')
    return p
def literals(raw):
    out={}
    for n in ast.parse(raw).body:
        if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name):
            try:out[n.targets[0].id]=ast.literal_eval(n.value)
            except (ValueError,TypeError):pass
    return out
def assignments(raw,values):
    tree=ast.parse(raw);lines=raw.decode().splitlines(keepends=True);edits=[]
    for name,text in values.items():
        hits=[n for n in tree.body if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and n.targets[0].id==name]
        need(len(hits)==1,'ASSIGNMENT_'+name);n=hits[0];edits.append((n.lineno-1,n.end_lineno,name+' = '+text+'\n'))
    for start,end,text in sorted(edits,reverse=True):lines[start:end]=[text]
    result=''.join(lines).encode();ast.parse(result);return result

def requirements():
    return dict(schema='dg16.public-only-final-binding-requirements.v1',authority='NONE',actual_inputs_supplied=False,
      required_inputs=['Exact frozen structural public_receiver/admission_gate/native_public and binding template bytes',
       'Parent-selected complete public byte map: actual host adoption/recipient, bridge BOUND, run FINAL source true',
       'Actual Root public-only runtime with fresh/current physical workspace/output/source receiving and exact host-adoption descriptor',
       'Actual public binding: fresh candidate/composition paths/seals/tree and all native/policy/review/adoption digests',
       'Actual candidate composition, policy gate, native gate and four exact public decision bodies',
       'Actual Root distinct-review selection and separately authenticated current source author identity'],
      issuer_thread=ISSUER,private_binding_emitted=False,effect_grant=False,
      remaining_consumer_gates='Unchanged public_receiver.verified recomputes native admission and checks exact composition/policy/source seals. Unchanged require_final_review requires later sealed exact independent PASS in Root effect admission.',
      provenance='Root must authenticate fresh issuer/path/decision/reviewer provenance outside matching JSON; this API performs no physical acquisition or authentication.')

def bind_public(structural,public,inputs):
    """Return public-only file bytes; never write them or alter supplied maps.

    structural: four frozen receiver files, including BINDING_TEMPLATE.json.
    public: complete selected candidate/public relative-name -> bytes map.
    inputs: host_adoption/runtime/binding/review_selection/composition/policy_gate/
    native_gate bytes, four decision bytes under decisions, and author string.
    Root's real acquisition/authority remains an external prerequisite.
    """
    need(type(structural) is dict and set(structural)==set(FROZEN)|{'BINDING_TEMPLATE.json'},'STRUCTURAL_FILES')
    for name,h in FROZEN.items():need(type(structural[name]) is bytes and sha(structural[name])==h,'FROZEN_CONSUMER_'+name)
    need(type(structural['BINDING_TEMPLATE.json']) is bytes and sha(structural['BINDING_TEMPLATE.json']) in TEMPLATE_PINS,'FROZEN_PUBLIC_BINDING_TEMPLATE')
    exact(inputs,'host_adoption runtime binding review_selection composition policy_gate native_gate decisions author')
    need(type(public) is dict and bool(public),'PUBLIC_BYTES')
    for name,body in public.items():
        need(type(name) is str and not name.startswith('/') and '\\' not in name and '..' not in PurePosixPath(name).parts and type(body) is bytes and 0<len(body)<=1024**2,'PUBLIC_MEMBER')
    a=parse(inputs['host_adoption']);rt=parse(inputs['runtime']);b=parse(inputs['binding']);selected=parse(inputs['review_selection'])
    c=parse(inputs['composition']);policy=parse(inputs['policy_gate']);native=parse(inputs['native_gate']);template=parse(structural['BINDING_TEMPLATE.json'])
    need(sha(inputs['host_adoption'])==RETAINED_HOST_ADOPTION_SHA256
      and a.get('schema')=='dg16.protected-full-g2-direct-host-recipient-adoption.v2'
      and a.get('issuer_thread')==RETAINED_HOST_ADOPTION_ISSUER
      and a.get('actor')=='/root' and a.get('effect_grant') is False and a.get('private_key_on_host') is False
      and a.get('original_awards')==[] and a.get('isolated_maximum_encrypt_capture_received') is True
      and a.get('private_authenticated_interoperability')=='NOT_ESTABLISHED_BY_THIS_ADOPTION','ACTUAL_HOST_ONLY_ADOPTION')
    need(a.get('source_commit')==SOURCE and a.get('source_tree')==TREE,'HOST_SOURCE')
    need(public.get(PREFIX+'PROTECTED_RECIPIENT.json')==inputs['host_adoption'],'SELECTED_ADOPTION_BYTES')
    need(desc(public[PREFIX+'PROTECTED_RECIPIENT.pem'])==a['recipient'],'SELECTED_CERTIFICATE')
    bridge=literals(public[PREFIX+'protected_bridge.py']);run=literals(public[PREFIX+'run.py'])
    need(bridge.get('BOUND') is True and bridge.get('SELECTION_SHA')==sha(inputs['host_adoption'])
      and bridge.get('HOST_SELECTION_EXPECTED')==a and run.get('FINAL_COMPOSITION_READY') is True,'PARENT_SELECTED_FINAL_SOURCE_REQUIRED')
    need(run.get('PROTECTED_BRIDGE_SHA')==sha(public[PREFIX+'protected_bridge.py'])
      and bridge.get('PREFLIGHT_SHA')==sha(public[PREFIX+'protected_preflight.py']),'HOST_PIN_CHAIN')
    for name,pin in bridge['COMPONENT_PINS'].items():need(desc(public[PREFIX+name])==pin,'HOST_COMPONENT_PIN')
    need(run.get('BRANCH')==a['branch']==bridge['BRANCH'] and bridge['CONTROL_BRANCH']==a['control_branch'],'SOURCE_BRANCHES')
    exact(rt,'schema actor issuer_thread session status workspace_root receiver_output_root maintained_source_root source_commit source_tree host_adoption workspace_current output_fresh source_current private_custody_ready effect_grant native_currentness original_awards')
    need(rt['schema']=='dg16.direct-host-public-runtime-binding.v1' and rt['actor']=='/root' and rt['issuer_thread']==rt['session']==ISSUER
      and rt['status']=='ACTUAL_PUBLIC_PATHS_RECEIVED_FOR_CODE_BINDING' and rt['host_adoption']==desc(inputs['host_adoption'])
      and rt['source_commit']==SOURCE and rt['source_tree']==TREE and rt['workspace_current'] is True
      and rt['output_fresh'] is True and rt['source_current'] is True and rt['private_custody_ready'] is False
      and rt['effect_grant'] is False and rt['native_currentness'] is False and rt['original_awards']==[],'FRESH_PUBLIC_ONLY_RUNTIME')
    workspace=path(rt['workspace_root']);output=path(rt['receiver_output_root']);source=path(rt['maintained_source_root'])
    need(type(workspace) is type(output) is type(source) and output!=workspace and output.is_relative_to(workspace)
      and not output.is_relative_to(source) and not source.is_relative_to(output),'PUBLIC_PATH_SEPARATION')
    need(set(b)==set(template),'PUBLIC_BINDING_FIELDS')
    dynamic=set(DIGEST_FIELDS+['candidate_path','composition_path','final_tree','branch','control_branch','session','modules','successor_runtime_binding','composition_review_reviewer','composition_review_selection'])
    for key,value in template.items():
        if key not in dynamic:need(type(b[key]) is type(value) and b[key]==value,'UNCHANGED_PUBLIC_GATE_'+key)
    need(b['source_commit']==SOURCE and b['source_tree']==TREE and b['authority']=='NONE' and b['effect_authority'] is False and b['original_acceptance'] is False,'PUBLIC_BINDING_SCOPE')
    need(b['branch']==a['branch'] and b['control_branch']==a['control_branch'] and b['session']==ISSUER
      and b['successor_runtime_binding']==desc(inputs['runtime']),'RUNTIME_BINDING_JOIN')
    for key in DIGEST_FIELDS:need(digest(b[key]),'ACTUAL_DECISION_REQUIRED_'+key)
    need(digest(b['final_tree'],40),'FINAL_TREE')
    for key in ('candidate_path','composition_path'):
        p=path(b[key]);need(p!=workspace and p.is_relative_to(workspace) and not p.is_relative_to(output) and not p.is_relative_to(source),'FRESH_PUBLIC_COMPOSITION_PATH')
    need(b['candidate_path']!=b['composition_path'],'DISTINCT_COMPOSITION_PATHS')
    modules={name[len(PREFIX):]:desc(body) for name,body in public.items() if name.startswith(PREFIX)}
    need(b['modules']==modules and b['native_public_validator']==desc(structural['native_public.py']),'ACTUAL_MODULE_BYTES')
    decisions=inputs['decisions'];need(type(decisions) is dict and set(decisions)==set(DECISIONS),'FOUR_ACTUAL_DECISIONS_REQUIRED')
    decoded={name:parse(body) for name,body in decisions.items()}
    need(all(type(d.get('schema')) is str and bool(d['schema']) for d in decoded.values()),'ACTUAL_DECISION_BODY')
    for key,name in zip(('public_review_sha256','public_adoption_sha256','public_native_review_sha256','public_native_adoption_sha256'),DECISIONS):need(b[key]==sha(decisions[name]),'DECISION_BODY_JOIN')
    need(b['composition_sha256']==sha(inputs['composition']) and b['policy_gate_sha256']==sha(inputs['policy_gate'])
      and b['native_gate_sha256']==sha(inputs['native_gate']),'COMPOSITION_GATE_HASHES')
    for key in ('source_commit','source_tree','final_tree','branch','control_branch','candidate_seal_sha256','native_review_seal_sha256','public_native_review_sha256','public_native_adoption_sha256'):need(c.get(key)==b[key],'COMPOSITION_'+key)
    need(c.get('independent_review_seal_sha256')==b['code_review_seal_sha256'],'CODE_REVIEW_JOIN')
    need(policy.get('review_sha256')==b['public_review_sha256'] and policy.get('adoption_sha256')==b['public_adoption_sha256'],'POLICY_GATE_JOIN')
    need(native.get('schema')=='dg16.g2-current-native-admission-readback.v1' and native.get('authority')=='NONE'
      and native.get('one_shot') is True and native.get('current_only') is True and native.get('original_awards')==[]
      and native.get('source_commit')==SOURCE and native.get('source_tree')==TREE
      and native.get('candidate_seal_sha256')==b['candidate_seal_sha256'] and native.get('review_sha256')==b['public_native_review_sha256']
      and native.get('adoption_sha256')==b['public_native_adoption_sha256']
      and decoded[DECISIONS[3]].get('independent_review_seal_sha256')==b['native_review_seal_sha256'],'NATIVE_GATE_JOIN')
    author=inputs['author'];reviewer=b['composition_review_reviewer']
    need(type(author) is str and bool(author) and type(reviewer) is str and re.fullmatch('/root/[a-z0-9_]+',reviewer)
      and reviewer!=author,'ACTUAL_DISTINCT_REVIEWER')
    expected=dict(schema='dg16.direct-host-public-combined-review-selection.v1',actor='/root',issuer_thread=ISSUER,session=ISSUER,
      status='ACTUAL_DISTINCT_REVIEWER_SELECTED_FOR_FINAL_BINDING',author=author,reviewer=reviewer,
      **{k:b[k] for k in ('source_commit','source_tree','branch','control_branch','candidate_seal_sha256','composition_seal_sha256','final_tree')},
      effect_grant=False,native_currentness=False,original_awards=[])
    need(type(selected) is dict and set(selected)==set(expected) and all(type(selected[k]) is type(v) and selected[k]==v for k,v in expected.items()),'ACTUAL_ROOT_DISTINCT_REVIEW_SELECTION_JOIN')
    need(b['composition_review_selection']==desc(inputs['review_selection']),'REVIEW_SELECTION_DESCRIPTOR')
    runtime_raw=inputs['runtime'];binding_raw=inputs['binding']
    root_node=next(n.value for n in ast.parse(structural['public_receiver.py']).body if isinstance(n,ast.Assign)
      and isinstance(n.targets[0],ast.Name) and n.targets[0].id=='MAINTAINED_SOURCE_ROOTS')
    old_excluded=ast.literal_eval(root_node.args[0].generators[0].iter)
    excluded=tuple(dict.fromkeys(list(old_excluded)+[rt['maintained_source_root']]+[str(base/n)
      for base in (workspace,workspace.parent) for n in ('source','source-codex-home','source-3e','source-8ee4','source-ea61','source-current')]))
    receiver=assignments(structural['public_receiver.py'],dict(ROOT='Path('+repr(rt['workspace_root'])+')',
      RECEIVER_OUT='Path('+repr(rt['receiver_output_root'])+')',RUNTIME_BINDING_SHA=repr(sha(runtime_raw)),BINDING_SHA=repr(sha(binding_raw)),
      MAINTAINED_SOURCE_ROOTS='tuple(Path(p) for p in '+repr(excluded)+')'))
    gate=assignments(structural['admission_gate.py'],{'CURRENT_AUTHOR':repr(author)})
    tree=ast.parse(gate);n=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='require_review_selection');lines=gate.decode().splitlines(keepends=True)
    replacement='''def require_review_selection(value, binding):
    # This exact public selector has modern issuer identity; Root authenticates provenance.
    expected = %s
    reviewer = binding['composition_review_reviewer']
    assert type(reviewer) is str and re.fullmatch('/root/[a-z0-9_]+', reviewer)
    assert reviewer != CURRENT_AUTHOR, 'CURRENT_AUTHOR_CANNOT_REVIEW_FINAL_BINDING'
    assert type(value) is dict and set(value) == set(expected), 'ACTUAL_ROOT_REVIEW_SELECTION_SHAPE'
    assert all(type(value[k]) is type(v) and value[k] == v for k,v in expected.items()), 'ACTUAL_ROOT_DISTINCT_REVIEW_SELECTION_JOIN'
    assert reviewer == expected['reviewer'] and binding['session'] == expected['session']
    for key in ('source_commit','source_tree','branch','control_branch','candidate_seal_sha256','composition_seal_sha256','final_tree'):
        assert binding[key] == expected[key], 'ACTUAL_ROOT_REVIEW_SUBJECT_JOIN'
    return reviewer
''' % repr(expected)
    lines[n.lineno-1:n.end_lineno]=[replacement];gate=''.join(lines).encode();ast.parse(gate)
    return {'public_receiver.py':receiver,'admission_gate.py':gate,'native_public.py':structural['native_public.py'],
      'BINDING.json':binding_raw,'SUCCESSOR_RUNTIME_BINDING.json':runtime_raw,'FINAL_REVIEW_SELECTION.json':inputs['review_selection'],
      'PUBLIC_BINDING_REQUIREMENTS.json':encode(requirements())}
