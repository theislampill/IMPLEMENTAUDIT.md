# Exact bounded source projection; source module is never imported.
SOURCE = 'e76a07b2bae7c945e5a9d529ed8cf9069f4c9064'

TREE = 'ff9fc6793892147aecc59bdfc4ddb82fc37f9eb7'

ROLES={'root_admission':'COMPOSITION_ROOT_ADMISSION.json','placement_receiving':'COMPOSITION_PLACEMENT_RECEIVING.json','placement_evidence_index':'COMPOSITION_PLACEMENT_EVIDENCE_INDEX.json','native_applicability_adoption':'COMPOSITION_NATIVE_APPLICABILITY_ADOPTION.json'}

RETAINED = {'SOURCE_ACQUISITION.json': {'bytes': 593285, 'sha256': '265325e29418163caeb27e13f4a66b32e1e5c0e4f3ad72cbef9bfff72a3b3bbf'}, 'PACKAGE_ROOT_RECEIVING.json': {'bytes': 928, 'sha256': '0edff0f3d8bd6f5520ef72d4e91daba54a6b0033e85b94f041f448c2951d6691'}, 'PACKAGE_BODY_RECEIVING.json': {'bytes': 9744, 'sha256': '8c592c76967ae2d95101af86ca25ab3bd4d09acdad486afbb976d61e7e5a7811'}, 'PACKAGE_TERMINAL_RECEIVING.json': {'bytes': 4531, 'sha256': 'e213b8843f03741c48776277f9e1db8c78ea1d3f7609875ce32bcd94e5ed5b89'}}

PLACEMENT={'placement/ACCESS09_DIAGNOSTIC.json':{'bytes':29107,'sha256':'5a56b0705e77314c587020dda0d45522a68bf5c93d4187281971b13cea4f95ae'},'placement/ACCESS09_FINAL.json':{'bytes':5113,'sha256':'61d6afe0d5cb5bca26c435c4529788816161d484714ec3e89148d24186b945c1'},'placement/ACCESS09_ROOT_RECEIVING.json':{'bytes':1961,'sha256':'40ce62326d8e9b759a5db150bf41a99dc77c05580342989aa33e06df2b0bedd3'}}

def need(v,c):
 if not v:raise ValueError(c)

def encode(v):return (json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)+'\n').encode()

def sha(b):return hashlib.sha256(b).hexdigest()

def desc(b):return dict(bytes=len(b),sha256=sha(b))

def parse(b):
 def pairs(rows):
  v={}
  for k,x in rows:need(k not in v,'DUPLICATE_KEY');v[k]=x
  return v
 return json.loads(b,object_pairs_hook=pairs,parse_constant=lambda _:need(False,'NONFINITE'))

def assignments(raw,values):
 text=raw.decode();tree=ast.parse(text);lines=text.splitlines(keepends=True);edits=[]
 for name,value in values.items():
  hits=[n for n in tree.body if isinstance(n,ast.Assign) and len(n.targets)==1 and isinstance(n.targets[0],ast.Name) and n.targets[0].id==name]
  need(len(hits)==1,'UNIQUE_BINDING_'+name);n=hits[0];edits.append((n.lineno-1,n.end_lineno,name+' = '+repr(value)+'\n'))
 for start,end,repl in sorted(edits,reverse=True):lines[start:end]=[repl]
 result=''.join(lines).encode();compile(result,'<composed>','exec');return result

def literal(raw,name):
 t=ast.parse(raw);hits=[n.value for n in t.body if isinstance(n,ast.Assign) and any(isinstance(x,ast.Name) and x.id==name for x in n.targets)]
 need(len(hits)==1,'BINDING_LITERAL');return ast.literal_eval(hits[0])

def loader_bind(carrier):
 pins=literal(carrier['carrier_loader.py'],'MODULE_PINS');carrier['carrier_loader.py']=assignments(carrier['carrier_loader.py'],{'MODULE_PINS':{n:desc(carrier[n+'.py']) for n in pins}})
 return carrier
