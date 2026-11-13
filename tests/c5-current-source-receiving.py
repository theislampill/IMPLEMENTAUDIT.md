#!/usr/bin/env python3
"""Exact current/frozen C5 source readers; no setup, provider or dispatch."""
from pathlib import Path
import ast,ctypes,ctypes.util,hashlib,json,os,shutil,sys,tempfile,types,unittest

ROOT=Path(__file__).resolve().parents[1]
if '--source-root' in sys.argv:
 i=sys.argv.index('--source-root');ROOT=Path(sys.argv[i+1]).resolve();del sys.argv[i:i+2]
BASELINE=None
if '--baseline-loader' in sys.argv:
 i=sys.argv.index('--baseline-loader');BASELINE=Path(sys.argv[i+1]);del sys.argv[i:i+2]
LOADER='scripts/load-work-graph-c5-executor.py'
COMPILER='skills/implementaudit/scripts/compile-work-graph.py'
OLD='0aa4572a03c7270c538b954d435569b882be59674c9d8275b002402cf9f8d78d'
CURRENT='cfaea1e33fdbcdda6c883c0a1883673166f7feefedfd29d509f90288664ff7a6'
sha=lambda b:hashlib.sha256(b).hexdigest()

def load(p,name):
 m=types.ModuleType(name);m.__file__=str(p);sys.modules[name]=m
 exec(compile(p.read_bytes(),str(p),'exec'),m.__dict__);return m

def literal(value):
 if hasattr(value,'items'):return {k:literal(v) for k,v in value.items()}
 if isinstance(value,(tuple,list)):return tuple(literal(v) for v in value)
 return value

@unittest.skipUnless(os.name=='posix','C5 source custody needs POSIX descriptor/mode controls')
class SourceReceiving(unittest.TestCase):
 def setUp(self):
  self.temp=tempfile.TemporaryDirectory(prefix='c5-current-source-only-')
  self.addCleanup(self.temp.cleanup)
  self.parent=Path(self.temp.name);self.source=self.parent/'source'
  L=load(ROOT/LOADER,'declared_current_loader');F=load(ROOT/'tests/c5-selected-source-fixture.py','declared_fixture')
  names={LOADER,'scripts/qualify-work-graph-c5-setup.py','tests/c5-selected-source-fixture.py'}
  names.add('test-support/r5-continuity-compiler-history/MANIFEST.json')
  for mode in ('R5_CURRENT_V4','R5_RETAINED_V3'):
   plan,base=F.selected_plan(L,mode);names.update(row['source'] for row in plan.values())
   s=json.loads((ROOT/base).read_bytes());names.update(s['programs']);names.update(s['payload_sources'])
  names.update(L._selection(L.R5_HOSTED_PROFILE,L.R5_DG17_COMPOSED_SOURCE_REVISION)[0])
  for attr in F.HISTORIES:names.update(row[0] for row in getattr(L,attr,{}).values())
  for attr in ('R5_RUNTIME_DIRECTORY_REASON_EXECUTOR_MEMBER','R5_RUNTIME_DEFAULT_ACL_EXECUTOR_MEMBER','R5_RUNTIME_DIRECTORY_MODE_EXECUTOR_MEMBER'):names.add(getattr(L,attr))
  for name in names:
   p=self.source/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p);p.chmod((ROOT/name).stat().st_mode&0o777)
  self.S=load(self.source/'scripts/qualify-work-graph-c5-setup.py','actual_hosted_reader')

 def current(self):return self.S.hosted_current_owner(self.source)

 def test_actual_current_v9_reader_and_compiler_capture(self):
  current=self.current();self.assertEqual(len(current.SOURCES),13)
  self.assertEqual(sha(current.SOURCES[COMPILER][0]),CURRENT)
  current.CHECK()
  self.assertEqual(sha(current.Q.LOADED_COMPILER),CURRENT)

 def test_frozen_v4_compiler_is_physically_retained(self):
  F=load(self.source/'tests/c5-selected-source-fixture.py','frozen_v4_fixture')
  destination=self.parent/'frozen-v4';F.materialize(self.source,destination,'R5_CURRENT_V4')
  self.assertEqual(sha((destination/COMPILER).read_bytes()),OLD)
  L=load(destination/LOADER,'frozen_v4_loader');E=L._Engine(L.R5_HOSTED_PROFILE,source_revision=L.R5_INNER_CAPTURE_SOURCE_REVISION).load()
  self.assertEqual(sha(E.SOURCES[COMPILER][0]),OLD)
  self.assertEqual(sha((self.source/COMPILER).read_bytes()),CURRENT)

 def test_frozen_v3_compiler_and_qualifier_remain_exact(self):
  F=load(self.source/'tests/c5-selected-source-fixture.py','frozen_v3_fixture')
  destination=self.parent/'frozen-v3';F.materialize(self.source,destination,'R5_RETAINED_V3')
  L=load(destination/LOADER,'frozen_v3_loader');E=L._Engine(L.R5_HOSTED_PROFILE,source_revision=L.R5_CONTINUITY_RECEIVER_SOURCE_REVISION).load()
  self.assertEqual(sha(E.SOURCES[COMPILER][0]),OLD)
  self.assertEqual(sha(E.SOURCES[L.QUALIFIER][0]),F.RETAINED_V3_QUALIFIER)

 def test_current_compiler_drift_refuses_captured_and_fresh_readers(self):
  current=self.current();p=self.source/COMPILER;p.write_bytes(p.read_bytes()+b'\n')
  with self.assertRaisesRegex(ValueError,'Captured C5 execution source'):current.CHECK()
  with self.assertRaisesRegex(ValueError,'Unsupported fixed C5 execution member'):self.current()

 def test_actual_source_program_drift_refuses_contract(self):
  current=self.current();state=current.B.complete_source(self.source,{})['state']
  current.B._producer_contract(state)
  p=self.source/'scripts/package-contract.py';p.write_bytes(p.read_bytes()+b'\n')
  state=current.B.complete_source(self.source,{})['state']
  with self.assertRaisesRegex(ValueError,'C5 original producer source differs: scripts/package-contract.py'):current.B._producer_contract(state)

 def test_actual_payload_population_drift_refuses_contract(self):
  current=self.current();state=current.B.complete_source(self.source,{})['state'];current.B._producer_contract(state)
  (self.source/'skills/implementaudit/scripts/validate-audit-implement-return.py').unlink()
  state=current.B.complete_source(self.source,{})['state']
  with self.assertRaisesRegex(ValueError,'C5 actual package source selector population differs'):current.B._producer_contract(state)

 def test_same_length_unqualified_loader_refuses_before_import(self):
  p=self.source/LOADER;b=p.read_bytes();p.write_bytes(b[:100]+bytes([b[100]^1])+b[101:])
  with self.assertRaisesRegex(ValueError,'hosted current loader pin differs'):self.current()

 def test_new_revision_does_not_select_another_profile(self):
  L=load(self.source/LOADER,'wrong_profile_loader')
  with self.assertRaisesRegex(ValueError,'fixed R5 hosted profile'):L._selection(L.CURRENT_PROFILE,L.R5_DG17_COMPOSED_SOURCE_REVISION)

 def test_all_prior_pin_and_revision_tables_are_unchanged(self):
  current=load(self.source/LOADER,'current_pin_tables')
  manifest=json.loads((self.source/'test-support/r5-continuity-compiler-history/MANIFEST.json').read_bytes())
  names=manifest['prior_table_names'];self.assertTrue(names)
  tables={n:literal(getattr(current,n)) for n in names}
  self.assertEqual(sha(json.dumps(tables,sort_keys=True,separators=(',',':')).encode()),manifest['prior_tables_sha256'])
  if BASELINE is not None:
   old=load(BASELINE,'original_pin_tables')
   for n in names:self.assertEqual(literal(getattr(current,n)),literal(getattr(old,n)),n)

if __name__=='__main__':
 def fence(event,args):
  if event.startswith(('subprocess.','socket.','ctypes.')) or event in ('os.fork','os.exec','os.posix_spawn','os.system','os.kill','os.killpg'):
   raise AssertionError('C5 SOURCE CONTROL ATTEMPTED DISPATCH_OR_NATIVE_EFFECT: '+event)
 sys.addaudithook(fence)
 unittest.main(verbosity=2)
