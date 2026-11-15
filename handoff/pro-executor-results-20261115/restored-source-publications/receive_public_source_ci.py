"""Single acquisition of ordinary public source-CI output; no accepting route."""
import hashlib, importlib.util, io, json, os, stat, sys, time, zipfile
from pathlib import Path, PurePosixPath

ROOT=Path('/workspace/scratch/0269e6626329/dg16')
SOURCE=ROOT/'handoff/dg16-pro-executor-20261115/platform_artifact.py'
ALLOWED_RUNS={43686248655:'a297957be11feb494c0ec467235794a1e0c54751',
              43686188100:'c073689e315b4db7c26e5a95c9024a34b1e560b7'}

def need(value, code):
    if not value: raise ValueError(code)

def desc(b): return {'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}

def write(p,b):
    with p.open('xb') as f: f.write(b); f.flush(); os.fsync(f.fileno())
    need(p.read_bytes()==b,'WRITE_READBACK')

def record(p,v): write(p,(json.dumps(v,sort_keys=True,indent=2)+'\n').encode())

def allowed(name, run):
    if run==43686188100:
        return name in {x+'.json' for x in ('RESULT','HOST','SOURCE','PACKAGES','ROUTES','PHASES','FAILURE','CLEANUP','ARTIFACT_MANIFEST')}
    return name in {'source-controls.log','rebuild.log','store-custody.log','rebuilt/PINS.json'} or name in {
        m+s for m in ('native-boundary','full','blocked-hook') for s in ('.log','/REHEARSAL_RESULT.json','/SIMULATED_ONLY.json')}

def main():
    need(sys.flags.isolated and sys.dont_write_bytecode and sys.flags.optimize==0 and len(sys.argv)==4,'FIXED_ENTRY')
    metadata=Path(sys.argv[1]).read_bytes(); catalog=json.loads(metadata)
    aid=int(sys.argv[2]); matches=[a for a in catalog['artifacts'] if a['id']==aid]
    need(len(matches)==1,'EXACT_ARTIFACT')
    a=matches[0]; run=a['workflow_run']['id']; name=a['name']; size=a['size_in_bytes']
    need(run in ALLOWED_RUNS and a['workflow_run']['head_sha']==ALLOWED_RUNS[run] and a['expired'] is False,'EXACT_SOURCE_RUN')
    need(name in ('dg17-linux-source-only','dg17-windows-store-source-only') if run==43686248655 else name=='dg16-installed-runtime05-43686188100-1','PUBLIC_SOURCE_ARTIFACT_ONLY')
    need(type(size) is int and 0<size<=1048576 and a['digest'].startswith('sha256:') and len(a['digest'])==71,'ARTIFACT_DESCRIPTOR')
    wanted={'bytes':size,'sha256':a['digest'][7:]}
    target=Path(sys.argv[3]);need(not target.exists() and target.parent.is_dir(),'EXCLUSIVE_TARGET')
    target.mkdir(mode=0o700)
    raw=SOURCE.read_bytes();need(desc(raw)['sha256']=='35ea21a75c8f7da3614454a384ebf53d30c132ac597cbdd86d39017161393389','TRANSPORT_SOURCE_PIN')
    spec=importlib.util.spec_from_file_location('retained_transport',SOURCE);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    _,resolver,acquire,_,_=m.owners()
    record(target/'ACQUISITION_INTENT.json',{'schema':'public-source-ci-acquisition.v1','artifact':a,'metadata':desc(metadata),'helper':desc(Path(__file__).read_bytes()),'protected_operation':False,'original_acceptance':False,'body_get_limit':1,'automatic_retry':False})
    raw=resolver.read_ephemeral_frame(4*1024**2)
    note,url=acquire.download_reference(raw,aid,name+'.zip');raw=None
    record(target/'DOWNLOAD_REFERENCE_DESCRIPTOR.json',note)
    started=time.monotonic()
    record(target/'BODY_READ_INTENT.json',{'started_monotonic':started,'deadline_monotonic':started+45,'body_gets':1,'automatic_retry':False})
    try:
        with resolver.request_watchdog(45): body=m.fetch_once(url,size,45,m.platform_proxy())
    finally: url=None
    need(time.monotonic()<started+45 and desc(body)==wanted,'EXACT_CURRENT_BODY')
    write(target/'artifact.zip',body)
    members=[]
    with zipfile.ZipFile(io.BytesIO(body)) as z:
        infos=z.infolist();need(0<len(infos)<100 and len({x.filename for x in infos})==len(infos),'ZIP_POPULATION')
        need(sum(x.file_size for x in infos)<4*1024**2,'EXPANSION_BOUND')
        for item in infos:
            pp=PurePosixPath(item.filename)
            need(not pp.is_absolute() and '..' not in pp.parts and '\\' not in item.filename and not item.flag_bits&1 and not stat.S_ISLNK(item.external_attr>>16),'PUBLIC_REGULAR_MEMBER')
            if item.is_dir(): continue
            need(allowed(str(pp),run),'FIXED_PUBLIC_MEMBER')
            b=z.read(item);out=target/'members'/str(pp);out.parent.mkdir(parents=True,exist_ok=True);write(out,b)
            members.append({'path':str(pp),**desc(b)})
    result={'status':'EXACT_PUBLIC_SOURCE_CI_ARTIFACT_RECEIVED','authority':'NONE','original_acceptance':False,'run_id':run,'head_sha':ALLOWED_RUNS[run],'artifact_id':aid,'archive':desc(body),'members':members,'body_gets':1,'automatic_retry':False,'signed_url_retained':False}
    record(target/'ACQUISITION_RECEIPT.json',result);print(json.dumps(result,sort_keys=True),flush=True)

if __name__=='__main__':
    try: main()
    except BaseException as e:
        print(json.dumps({'status':'ACQUISITION_REFUSED_OR_UNCERTAIN','type':type(e).__name__,'automatic_retry':False,'signed_url_retained':False}),flush=True);raise SystemExit(1)
