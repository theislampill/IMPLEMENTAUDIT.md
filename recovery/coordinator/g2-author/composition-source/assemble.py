"""Pure, pinned public source composition; never issues Root decisions or seals.

Only maintained data validators and selected pure helper definitions execute.
Physical custody/currentness, real decision provenance, composition sealing and
effect admission remain separately received Root acts. No native function runs.
"""
import ast
import hashlib
import json
import re
import types
from pathlib import PurePosixPath

PREFIX='qualification/dg16-r5-full-g2/'
DECISION_PREFIX='qualification/dg16-r5-full-g2-decisions/'
SOURCE='7e2b00b3a2a16fc6033a5eabe4fc795f6249366f'
TREE='6d3f972a424583f9d3d56d8bfd9ae11cf36ecf6e'
ISSUER='01a1953f-a15b-7811-aa72-3538ebb03562'
PINS={'candidate':'9c4b01a11de9b3e064259eb3b893bfe81a5926556e147be5d60c95152641f17b',
 'runtime':'8f8b04026a9a29cbc84841c857ba1d07e717bdcf7e8283c5ee20eb433d9dd5e5',
 'witness':'8dd6be2cef66d4632b2f58f8bc406d93504e1f155b839e5ca559f34d3ff57a99',
 'policy_control.py':'ad9838347df4fe0e3f0caf5c2397f52527257a2a874703a29b590329b0db2981',
 'native_admission.py':'d9c0eeb25dc364e8cec1fea469129ae3b1ccc90deff32db4fa26dbf627dd1cb2',
 'evidence_io.py':'c2f8d718c8acd3a223d494239e6bc19d4a90e3d5c66f49cdac8f701ce4807075',
 'native_profile.py':'c16c75039b938718ab4bfee9e49a6c55322bdfda22f25d0a526cf74f87944c3d',
 'native_integration.py':'622e10fe0b8627f93ae91cd22a3211822e53ea7d3e3f730154cd215c1c67e3e7',
 'SOURCE_MANIFEST.json':'840f6c66afb0f0a50cdbf4b9dc11241ac1d1c83e4ca88d7d3436d0baccb532e8'}
def need(ok,code):
    if not ok:raise ValueError(code)
def sha(raw):return hashlib.sha256(raw).hexdigest()
def desc(raw):return dict(bytes=len(raw),sha256=sha(raw))
def encode(value):return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=True,allow_nan=False)+'\n').encode('ascii')
def parse(raw):
    need(type(raw) is bytes and 0<len(raw)<=2*1024**2,'JSON_BOUND')
    def pairs(rows):
        d={}
        for k,v in rows:need(k not in d,'DUPLICATE_KEY');d[k]=v
        return d
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda _:need(False,'NONFINITE'))
def safe_name(name):
    need(type(name) is str and name and '\\' not in name and '\0' not in name and ':' not in name
      and not name.startswith('/') and str(PurePosixPath(name))==name and '..' not in PurePosixPath(name).parts,'SOURCE_MEMBER_NAME')
def literals(raw):
    out={}
    for n in ast.parse(raw).body:
        if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name):
            try:out[n.targets[0].id]=ast.literal_eval(n.value)
            except (ValueError,TypeError):pass
    return out
def selected_module(raw,name,env,functions=None,constants=None,classes=False):
    nodes=[]
    for n in ast.parse(raw).body:
        if isinstance(n,ast.FunctionDef) and (functions is None or n.name in functions):nodes.append(n)
        elif classes and isinstance(n,ast.ClassDef):nodes.append(n)
        elif isinstance(n,ast.Assign) and (constants is None or all(isinstance(t,ast.Name) and t.id in constants for t in n.targets)):nodes.append(n)
    m=types.ModuleType(name);m.__dict__.update(env)
    exec(compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),'<pinned-pure-'+name+'>','exec'),m.__dict__)
    return m

def validator_context(candidate_files):
    """Load exact maintained validation definitions with byte-only read bindings.

    evidence_io file/native helpers and profile host functions are not compiled.
    native_integration bindings/history are unchanged AST functions with read_packet
    redirected to the supplied immutable public byte map, not a physical reader.
    """
    public={n[len('candidate/public/'):]:b for n,b in candidate_files.items() if n.startswith('candidate/public/')}
    def body(name):
        raw=public[PREFIX+name];need(type(raw) is bytes and sha(raw)==PINS[name],'FROZEN_VALIDATOR_'+name);return raw
    E=selected_module(body('evidence_io.py'),'evidence',{'hashlib':hashlib,'json':json},functions={'need','sha','encode','parse'},constants=set(),classes=True)
    P=selected_module(body('native_profile.py'),'profile',{},functions=set(),constants={'PROFILE','HOST_FIELDS','MATCH_FIELDS'})
    policy=selected_module(body('policy_control.py'),'policy',{'hashlib':hashlib,'json':json,'re':re},classes=True)
    native=selected_module(body('native_admission.py'),'native',{'re':re,'_HOST_EVIDENCE_IO':E,'_G2_NATIVE_PROFILE':P},functions={'independent','validate'})
    run_raw=public[PREFIX+'run.py'];H=types.SimpleNamespace(**literals(run_raw));H.__file__='/candidate/public/'+PREFIX+'run.py'
    N=types.SimpleNamespace(**literals(public[PREFIX+'native_prerequisite.py']))
    def read_bytes(path,maximum=4*1024**2):
        name=str(path);need(name.startswith('/candidate/public/'),'BYTE_READER_SCOPE')
        raw=public[name[len('/candidate/public/'):]];need(len(raw)<=maximum,'BYTE_READER_BOUND');return raw
    E.read_packet=read_bytes
    integration=selected_module(body('native_integration.py'),'integration_bindings',{'E':E,'H':H,'N':N,'need':E.need,'Path':PurePosixPath,'DIRECTORY':PurePosixPath(H.__file__).parent},functions={'history','bindings'},constants={'HISTORICAL_COMMIT','HISTORICAL_TREE'})
    pb=dict(source_commit=H.SOURCE_COMMIT,source_tree=H.SOURCE_TREE,policy_sha256=H.POLICY_SHA,
      receiver_inputs_sha256=H.RELATION_INPUTS_SHA,adapter_sha256=sha(run_raw),pair_driver_sha256=H.PAIR_DRIVER_SHA)
    policy_raw=public[PREFIX+'POLICY.json'];pv=parse(policy_raw)
    need(sha(policy_raw)==H.POLICY_SHA and policy_raw==encode(pv) and pv['receiver_inputs_sha256']==H.RELATION_INPUTS_SHA
      and pv['full_receiver_sha256']==H.FULL_RELATION_SHA,'ACTUAL_POLICY_SOURCE_JOIN')
    return dict(public=public,policy_gate_validator=policy,policy=pv,policy_bindings=pb,native=native,
      native_bindings=integration.bindings(),historical=integration.history()['host_prerequisite'],profile=P,evidence=E)

def git_object(kind,body):return hashlib.sha1(kind.encode()+b' '+str(len(body)).encode()+b'\0'+body).hexdigest()
def git_tree(entries):
    trie={}
    for name,(mode,blob) in entries.items():
        safe_name(name);node=trie
        parts=name.split('/')
        for part in parts[:-1]:
            need(not isinstance(node.get(part),tuple),'TREE_PATH_COLLISION');node=node.setdefault(part,{})
        need(parts[-1] not in node,'TREE_DUPLICATE_PATH');node[parts[-1]]=(mode,blob)
    trees={}
    def walk(node,prefix):
        body=b''
        for name,value in sorted(node.items(),key=lambda x:(x[0]+('/' if isinstance(x[1],dict) else '')).encode()):
            if isinstance(value,dict):mode,blob='40000',walk(value,prefix+name+'/')
            else:mode,blob=value
            need(mode in ('40000','100644','100755','120000') and re.fullmatch('[0-9a-f]{40}',blob),'GIT_ENTRY')
            body+=mode.encode()+b' '+name.encode()+b'\0'+bytes.fromhex(blob)
        h=git_object('tree',body);trees[prefix or '/']=dict(bytes=len(body),sha1=h);return h
    return walk(trie,''),trees

def assemble(candidate_files,candidate_seal,runtime,host_witness,decisions,review_seals):
    """Return prospective composition/gates/tree/files; no Root act is minted."""
    for label,raw in (('candidate',candidate_seal),('runtime',runtime),('witness',host_witness)):
        need(type(raw) is bytes and sha(raw)==PINS[label],'ACTUAL_INPUT_PIN_'+label)
    seal=parse(candidate_seal);rt=parse(runtime)
    need(seal['actor']=='/root' and seal['issuer_thread']==ISSUER and seal['effect_grant'] is False
      and seal['member_count']==len(seal['members'])==63,'ACTUAL_CANDIDATE_SEAL')
    need(type(candidate_files) is dict and len(candidate_files)==63 and set(candidate_files)=={r['path'] for r in seal['members']},'CANDIDATE_POPULATION')
    for row in seal['members']:
        safe_name(row['path']);raw=candidate_files[row['path']];need(type(raw) is bytes and desc(raw)=={k:row[k] for k in ('bytes','sha256')},'CANDIDATE_SOURCE_'+row['path'])
    need(rt['issuer_thread']==rt['session']==ISSUER and rt['source_commit']==SOURCE and rt['source_tree']==TREE
      and rt['effect_grant'] is False and rt['private_custody_ready'] is False and rt['output_fresh'] is True
      and rt['source_current'] is True and rt['native_currentness'] is False,'PUBLIC_ONLY_RUNTIME')
    ctx=validator_context(candidate_files);public=ctx['public']
    adoption=parse(public[PREFIX+'PROTECTED_RECIPIENT.json'])
    need(adoption['host_qualification']['root']==desc(host_witness) and rt['host_adoption']==desc(public[PREFIX+'PROTECTED_RECIPIENT.json']),'ACTUAL_HOST_WITNESS_JOIN')
    all_names=set(ctx['policy_gate_validator'].DECISION_FILES)|set(ctx['native'].FILES)
    need(type(decisions) is dict and set(decisions)==all_names,'FOUR_ACTUAL_DECISION_BODIES_REQUIRED')
    pg=ctx['policy_gate_validator'].validate({n:decisions[n] for n in ctx['policy_gate_validator'].DECISION_FILES},ctx['policy_bindings'],ctx['policy'])
    ng=ctx['native'].validate({n:decisions[n] for n in ctx['native'].FILES},ctx['native_bindings'],ctx['historical'])
    candidate=sha(candidate_seal)
    need(pg['candidate_seal_sha256']==ng['candidate_seal_sha256']==candidate,'ACTUAL_REVIEW_CANDIDATE_JOIN')
    need(type(review_seals) is dict and set(review_seals)=={'code','native'},'ACTUAL_REVIEW_SEALS_REQUIRED')
    for role,name in (('code','ROOT_POLICY_ADOPTION.json'),('native','ROOT_NATIVE_APPLICABILITY_ADOPTION.json')):
        raw=review_seals[role];value=parse(raw)
        need(sha(raw)==parse(decisions[name])['independent_review_seal_sha256'],'ACTUAL_REVIEW_SEAL_'+role)
        need(type(value.get('members')) is list and type(value.get('member_count')) is int and len(value['members'])==value['member_count']>0,'REVIEW_SEAL_POPULATION')
    base=parse(public[PREFIX+'SOURCE_MANIFEST.json']);need(sha(public[PREFIX+'SOURCE_MANIFEST.json'])==PINS['SOURCE_MANIFEST.json'],'EXACT_BASE_MANIFEST')
    need(base['commit']==SOURCE and base['tree']==TREE and base['file_count']==len(base['members'])==1759
      and base['total_bytes']==sum(r['bytes'] for r in base['members'])==166407881,'EXACT_1759_BASE')
    entries={r['path']:(r['mode'],r['git_blob']) for r in base['members']};need(len(entries)==1759,'BASE_DUPLICATE')
    base_tree,_=git_tree(entries);need(base_tree==TREE,'BASE_TREE_RECOMPUTATION')
    overlay=dict(public);overlay.update({DECISION_PREFIX+n:raw for n,raw in decisions.items()})
    need(not set(overlay).intersection(entries),'MAINTAINED_BASE_SOURCE_REPLACEMENT')
    for name,raw in overlay.items():entries[name]=('100644',git_object('blob',raw))
    final_tree,trees=git_tree(entries)
    composition=dict(schema='dg16.public-only-prospective-source-composition.v1',authority='NONE',effect_grant=False,
      source_commit=SOURCE,source_tree=TREE,branch=adoption['branch'],control_branch=adoption['control_branch'],
      final_tree=final_tree,candidate_path=rt['workspace_root']+'/candidate',candidate_seal_sha256=candidate,
      independent_review_seal_sha256=sha(review_seals['code']),native_review_seal_sha256=sha(review_seals['native']),
      public_review_sha256=pg['review_sha256'],public_adoption_sha256=pg['adoption_sha256'],
      public_native_review_sha256=ng['review_sha256'],public_native_adoption_sha256=ng['adoption_sha256'],
      runtime=desc(runtime),host_adoption=rt['host_adoption'],original_awards=[],original_acceptance=False)
    requirements=dict(schema='dg16.public-composition-binding-body-requirements.v1',authority='NONE',effect_grant=False,
      actual_composition_physical_seal_required=True,actual_Root_review_selection_required=True,
      prospective_composition_path=rt['workspace_root']+'/composition',candidate_seal=desc(candidate_seal),runtime=desc(runtime),
      composition=desc(encode(composition)),policy_gate=desc(encode(pg)),native_gate=desc(encode(ng)),final_tree=final_tree,
      review_selection_required_fields=['actual author','actual distinct reviewer','Astra issuer/session','candidate seal','actual physical composition seal','source/branch/control/final tree'],
      late_exact_independent_review_required=True,private_enabled=False,native_currentness_received=False,original_awards=[])
    files={'public/'+n:raw for n,raw in overlay.items()}
    files.update({'COMPOSITION.json':encode(composition),'POLICY_GATE_READBACK.json':encode(pg),'NATIVE_GATE_READBACK.json':encode(ng),'PUBLIC_BINDING_BODY_REQUIREMENTS.json':encode(requirements)})
    return dict(files=files,composition=composition,policy_gate=pg,native_gate=ng,
      tree=dict(base_tree=base_tree,tree=final_tree,file_count=len(entries),overlay_files=len(overlay),trees=trees),
      requirements=requirements,runtime=runtime,decisions=dict(decisions),public=public)

def bind_when_issued(assembly,structural,binding_inputs,bind_public):
    """Only hand already-issued data to the separately reviewed pure binder."""
    need(type(binding_inputs) is dict and type(binding_inputs.get('review_selection')) is bytes and binding_inputs['review_selection'],'ACTUAL_ROOT_FINAL_SELECTION_STILL_REQUIRED')
    expected_bodies=dict(runtime=assembly['runtime'],composition=encode(assembly['composition']),
      policy_gate=encode(assembly['policy_gate']),native_gate=encode(assembly['native_gate']))
    for name,expected in expected_bodies.items():
        need(binding_inputs.get(name)==expected,'ISSUED_BINDING_ASSEMBLY_'+name)
    need(binding_inputs.get('decisions')==assembly['decisions'],'ISSUED_DECISIONS_CHANGED')
    return bind_public(structural,assembly['public'],binding_inputs)

def main():
    # Source/operator CLI only. Never run against a Root workspace without its
    # separate source-write assignment. It cannot create decisions or a seal.
    import argparse
    from pathlib import Path
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--candidate',type=Path,required=True);p.add_argument('--issuer',type=Path,required=True)
    p.add_argument('--host-witness',type=Path,required=True);p.add_argument('--decisions',type=Path,required=True)
    p.add_argument('--code-review-seal',type=Path,required=True);p.add_argument('--native-review-seal',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    seal=(a.issuer/'CANDIDATE_SEAL.json').read_bytes()
    need(sha(seal)==PINS['candidate'],'ACTUAL_INPUT_PIN_candidate')
    members=parse(seal)['members']
    for row in members:safe_name(row['path'])
    candidate={row['path']:(a.candidate/row['path']).read_bytes() for row in members}
    names=('INDEPENDENT_COLD_REVIEW.json','ROOT_POLICY_ADOPTION.json','NATIVE_INDEPENDENT_REVIEW.json','ROOT_NATIVE_APPLICABILITY_ADOPTION.json')
    result=assemble(candidate,seal,(a.issuer/'PUBLIC_RUNTIME.json').read_bytes(),a.host_witness.read_bytes(),{n:(a.decisions/n).read_bytes() for n in names},{'code':a.code_review_seal.read_bytes(),'native':a.native_review_seal.read_bytes()})
    need(not a.output.exists(),'FRESH_SOURCE_OUTPUT_REQUIRED');a.output.mkdir(mode=0o700)
    for name,body in result['files'].items():
        target=a.output/name;target.parent.mkdir(parents=True,exist_ok=True)
        with target.open('xb') as f:f.write(body)
    with (a.output/'PROSPECTIVE_TREE.json').open('xb') as f:f.write(encode(result['tree']))
    print(json.dumps({'tree':result['tree']['tree'],'files':len(result['files']),'effect_grant':False,'composition_seal_issued':False}))

if __name__=='__main__':main()
