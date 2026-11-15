"""Read-only: run the generated parents' own capture() over the exact readset. No --execute, no grant, no native effect."""
import ast,hashlib,json,os,stat,sys,platform
from pathlib import Path
A=Path(sys.argv[1]); out=Path(sys.argv[2])
def load_capture(name):
    text=(A/name).read_text(encoding='utf-8'); tree=ast.parse(text)
    fn=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='capture']; assert len(fn)==1
    consts={n.targets[0].id:ast.literal_eval(n.value) for n in tree.body if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and n.targets[0].id in {'OP_SHA','DRIVER_SHA','RPC_SHA','JOB_SHA'}}
    ns={'hashlib':hashlib,'os':os,'stat':stat,'Path':Path}; exec(ast.get_source_segment(text,fn[0]),ns)
    job=[ast.get_source_segment(text,n.value) for n in tree.body if isinstance(n,ast.Assign) and getattr(n.targets[0],'id','')=='JOB']
    return ns['capture'],consts,(eval(job[0],{'Path':Path}) if job else None)
cap,c,JOB=load_capture('parent_launch_a.py')
rows=[]
def row(label,path,pin,size=None,phys=None):
    try: cap(path,pin,size,phys); ok=True; err=None
    except BaseException as e: ok=False; err=type(e).__name__+': '+str(e)[:200]
    s=Path(path).lstat() if Path(path).exists() else None
    rows.append({'role':label,'path':str(path),'sha256':pin,'bytes':s.st_size if s else None,'parent_capture':'PASS' if ok else 'REFUSED','error':err})
op=json.loads((A/'OPERATION_A.json').read_bytes())
row('operation',A/'OPERATION_A.json',c['OP_SHA'])
for it in op['readset']: row('readset',it['path'],it['sha256'],it['bytes'],it.get('physical_identity'))
row('stage_a_driver',A/'stage_a.py',c['DRIVER_SHA']); row('rpc',A/'native_rpc.py',c['RPC_SHA']); row('job_helper',JOB,c['JOB_SHA'])
capb,cb,_=load_capture('parent_launch_b.py'); 
try: capb(A/'stage_b.py',cb['DRIVER_SHA']); rows.append({'role':'stage_b_driver','path':str(A/'stage_b.py'),'sha256':cb['DRIVER_SHA'],'parent_capture':'PASS','error':None})
except BaseException as e: rows.append({'role':'stage_b_driver','parent_capture':'REFUSED','error':str(e)})
H=Path(op['case']).parent
fresh={n:(not (H/n).exists()) for n in ['case-native-02','EPISODE_WINDOW_02.json','parent-A-02','PARENT_STAGE_A_JOB_RESULT_02.json','OPERATION_B_BOUND.json','parent-B-01','PARENT_STAGE_B_JOB_RESULT.json']}
res={'schema':'dg17.final-host-readback.v1','authority':'NONE - read-only readback; no grant, no --execute, no native effect','host':platform.node(),'os':platform.platform(),'python':sys.version.split()[0],
 'python_executable_equals_operation_python':Path(sys.executable).resolve()==Path(op['python']['path']).resolve(),
 'operation_case':op['case'],'case_absent':not Path(op['case']).exists(),'expected_codex_home_is_dir':Path(op['expected_codex_home']).is_dir(),
 'fixed_locations_absent':fresh,'issuer_retained':op['issuer'],'rows':rows,'pass':sum(r['parent_capture']=='PASS' for r in rows),'total':len(rows)}
out.write_text(json.dumps(res,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({k:v for k,v in res.items() if k!='rows'},indent=1)); [print(r['parent_capture'],r['role'],Path(r.get('path','')).name,r.get('error') or '') for r in rows]
