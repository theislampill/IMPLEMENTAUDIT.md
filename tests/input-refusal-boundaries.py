#!/usr/bin/env python3
"""EXTERNAL_SHADOW_ONLY / NO_CAMPAIGN_CREDIT. Real decoders, inert temp files.

Run: python -B input_refusal_boundaries.py --source /absolute/source/root
These finite cases do not prove universal resource-exhaustion resistance.
"""
from pathlib import Path
import argparse,contextlib,copy,hashlib,importlib.util,io,json,subprocess,sys,tempfile
p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);a=p.parse_args();S=a.source.resolve()
def load(name):
 path=S/'skills/implementaudit/scripts'/name
 spec=importlib.util.spec_from_file_location(name.replace('-','_').replace('.','_'),path)
 m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m);return m
r=load('route-transaction.py');g=load('compile-work-graph.py');q=load('rotate-canonical-state.py')
results=[]
def check(name,fn):
 try: detail=fn(); results.append({'id':name,'result':'PASS','detail':detail})
 except BaseException as e:
  results.append({'id':name,'result':'FAIL','error_type':type(e).__name__,'error':str(e)[:500]})
def require(condition,message):
 if not condition:raise AssertionError(message)
def route_refusal(fn,fragment=None):
 out=io.StringIO()
 with contextlib.redirect_stdout(out):
  try:fn()
  except SystemExit as e:require(e.code==2,'not controlled exit2')
  else:raise AssertionError('invalid input accepted')
 j=json.loads(out.getvalue());require(j['status']=='UNAVAILABLE' and j['advance_allowed'] is False and j['enforcement_available'] is False and j['decision']=='PENDING','refusal shape/authority changed')
 if fragment:require(fragment in j['error'],'wrong refusal: '+j['error'])
 return j
D='sha256:'+'a'*64
valid={'schema':r.REQUEST_SCHEMA,'predicate_version':r.PREDICATE_VERSION,'boundary':{'kind':'fixture','event_id':'fixture-01','digest':D},'scope':{'identity':'scope','digest':D},'action':{'identity':'action','digest':D,'class':'READ_ONLY','argv':['fixture-action']},'inputs':[{'identity':'input','path':'fixture-input','digest':D}]}
check('route.valid-neighbour',lambda:require(r.validate_request(copy.deepcopy(valid))==valid,'valid changed'))
for target in ('boundary','action'):
 for kind,value in [('list',[]),('null',None),('integer',42),('boolean',True),('object',{}),('short','sha256:abc'),('upper','sha256:'+'A'*64)]:
  def f(target=target,value=value):
   v=copy.deepcopy(valid);v[target]['digest']=value
   return route_refusal(lambda:r.validate_request(v),target+' identity is malformed')
  check('route.'+target+'.'+kind,f)
for target in ('inputs','scope'):
 def f(target=target):
  v=copy.deepcopy(valid)
  (v['inputs'][0] if target=='inputs' else v['scope'])['digest']=[]
  return route_refusal(lambda:r.validate_request(v))
 check('route.existing-neighbour-'+target,f)
raw_bad={
 'syntax':b'{',
 'depth':b'['*20000+b'0'+b']'*20000,
 'integer-limit':b'{"v":'+b'9'*5000+b'}',
 'duplicate':b'{"x":1,"x":2}',
 'non-utf8':b'\xff',
}
with tempfile.TemporaryDirectory(prefix='external-shadow-input-') as td:
 root=Path(td)
 for name,raw in raw_bad.items():
  file=root/(name+'.json');file.write_bytes(raw)
  def read_control(file=file):
   before={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in root.iterdir()}
   result=route_refusal(lambda:r.read_request(str(file)))
   after={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in root.iterdir()}
   require(before==after,'refusal changed fixture state');return {'refusal':result,'fixture_unchanged':True}
  check('route.read_request.'+name,read_control)
  for decoder in ('read_exact_artifact','decoded_artifact'):
   def f(decoder=decoder,raw=raw,file=file):
    return route_refusal(lambda: r.read_exact_artifact(str(file),'fixture') if decoder=='read_exact_artifact' else r.decoded_artifact(raw,'fixture'))
   check('route.'+decoder+'.'+name,f)
 file=root/'valid.json';file.write_text(json.dumps(valid,ensure_ascii=False),encoding='utf-8')
 check('route.read_request.valid',lambda:require(r.read_request(str(file))==valid,'valid refused'))
 for decoder in ('read_exact_artifact','decoded_artifact'):
  raw='{"valid":"العربية 日本語 🙂","nested":[1,2,3]}'.encode()
  check('route.'+decoder+'.unicode',lambda decoder=decoder,raw=raw:require((r.decoded_artifact(raw,'fixture') if decoder=='decoded_artifact' else (file.write_bytes(raw),r.read_exact_artifact(str(file),'fixture')[1])[1])==json.loads(raw),'unicode changed'))

def graph_reject(raw):
 try:g.decode_strict_json_bytes(raw,'shadow')
 except g.WorkGraphError as e:return {'error_type':'WorkGraphError','message':str(e)}
 raise AssertionError('invalid graph JSON accepted')
def rotation_reject(raw):
 try:q._decode_exact_canonical_json_v1(raw,'SHADOW_CANONICAL_INVALID')
 except q.RotationError as e:return {'error_type':'RotationError','message':str(e)}
 raise AssertionError('invalid canonical JSON accepted')
invalid=dict(raw_bad,**{'lone-surrogate':b'{"x":"\\ud800"}','surrogate-key':b'{"\\udfff":0}','float':b'{"x":1.0}','nan':b'{"x":NaN}','int64-high':b'{"x":9223372036854775808}','int64-low':b'{"x":-9223372036854775809}'})
for name,raw in invalid.items():
 check('compiler.'+name,lambda raw=raw:graph_reject(raw))
 check('rotation.'+name,lambda raw=raw:rotation_reject(raw))
for label,value in [('unicode',{'x':'العربية 日本語 🙂'}),('int64',{'a':-(2**63),'b':2**63-1}),('large',{'x':'a'*100000}),('deep-supported',{'x':[[[[0]]]]}),('scalar-types',{'a':None,'b':True,'c':False,'d':[],'e':{}})]:
 raw=json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
 check('compiler.valid-'+label,lambda value=value,raw=raw:require(g.decode_strict_json_bytes(raw,'shadow')==value,'valid changed'))
 check('rotation.valid-'+label,lambda value=value,raw=raw:require(q._decode_exact_canonical_json_v1(raw,'SHADOW_CANONICAL_INVALID')==value,'valid changed'))
# An object can decode yet hit the recursive semantic validator: cover both phases.
for depth in (200,600):
 raw=b'{"x":'+b'['*depth+b'0'+b']'*depth+b'}'
 for name,module,decode,error in [('compiler',g,lambda raw=raw:g.decode_strict_json_bytes(raw,'shadow'),g.WorkGraphError),('rotation',q,lambda raw=raw:q._decode_exact_canonical_json_v1(raw,'SHADOW_CANONICAL_INVALID'),q.RotationError)]:
  def f(decode=decode,error=error,depth=depth):
   try:decode();return {'accepted_supported_depth':depth}
   except error:return {'controlled_limit':depth}
  check(name+'.near-interpreter-limit-'+str(depth),f)
# Real compiler CLI: must exit2 with no traceback, no output graph, no file effects.
with tempfile.TemporaryDirectory(prefix='external-shadow-compiler-cli-') as td:
 for name in ('syntax','depth','integer-limit','lone-surrogate'):
  raw=invalid[name];path=Path(td)/'graph.json';path.write_bytes(raw)
  def f(path=path,raw=raw):
   cp=subprocess.run([sys.executable,'-B',str(S/'skills/implementaudit/scripts/compile-work-graph.py'),str(path)],capture_output=True,text=True,timeout=15)
   require(cp.returncode==2 and not cp.stdout and 'Traceback' not in cp.stderr,'CLI leaked error or output: '+cp.stderr[:200]);require(path.read_bytes()==raw,'CLI input mutated')
   return {'exit_code':cp.returncode,'stderr':cp.stderr.strip(),'input_unchanged':True}
  check('compiler.cli.'+name,f)
summary={'label':'EXTERNAL_SHADOW_ONLY / NO_CAMPAIGN_CREDIT','source':str(S),'python':sys.version,'integer_string_limit':sys.get_int_max_str_digits(),'recursion_limit':sys.getrecursionlimit(),'tests':results,'passed':sum(r['result']=='PASS' for r in results),'failed':sum(r['result']=='FAIL' for r in results)}
print(json.dumps(summary,ensure_ascii=True,indent=2));sys.exit(bool(summary['failed']))
