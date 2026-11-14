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
BASELINE_V10=None
if '--baseline-v10-loader' in sys.argv:
 i=sys.argv.index('--baseline-v10-loader');BASELINE_V10=Path(sys.argv[i+1]);del sys.argv[i:i+2]
LOADER='scripts/load-work-graph-c5-executor.py'
COMPILER='skills/implementaudit/scripts/compile-work-graph.py'
OLD='0aa4572a03c7270c538b954d435569b882be59674c9d8275b002402cf9f8d78d'
CURRENT='226f4897a5e8edd0ffe460426a9b2995cd5f2bcfb169b68978ae727d065f685b'
# Exact historical V9-V10 compiler (the 8754 bytes), kept as an explicit retained member.
V10_COMPILER='cfaea1e33fdbcdda6c883c0a1883673166f7feefedfd29d509f90288664ff7a6'
V10_MEMBER='test-support/r5-dg17-composed-compiler-history/8754-source/'+COMPILER
V10_TUPLE='632387df40ca20b0714752b8407cb0b0c6b805f468340148ae681016afdb285f'  # sha256 of the integrated V10 _selection literal
V10_LOADER=(59606,'eba57563d794e86dfd2429b9ba75ebe5e77f226bd527a9becea6386b2f641554')
BUILDER='scripts/package-contract.py'
# Exact historical R5 base (V1-V9) and the separately named current V10 base.
OLD_BASE=('fixtures/work-graph-c5-inputs/execution-r5-hosted-ubuntu24-python312.json',8304,
 '15e71318bfb65427e5f5bb49bd0a7e6f5cf4460618ef1b64d3d598b447646e97','ed7a1b3cc5d02660b6fef32a40a99d51e41ee3cf302a56548de8a4aca0c03960')
NEW_BASE=('fixtures/work-graph-c5-inputs/execution-r5-hosted-ubuntu24-budget5-builder-python312.json',8304,
 '5963c8779ebc1717fd120f44ab21b10386e86e3afe66c644526fe4cc9d7bbc26','506d52a9e12261c295a1bf0fe16e4cf4c382ec06335feeb8806f404396568c1f')
V9_TUPLE='715625ea17e5c3084a24d71a7c3d3f3a7aa9a7e71e99bdea8ac769545faa17e9'  # sha256 of the baseline 8754 V9 _selection literal
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
  names.add('test-support/r5-dg17-composed-compiler-history/MANIFEST.json')
  for mode in ('R5_CURRENT_V4','R5_RETAINED_V3','R5_CURRENT_BUILDER_V10','R5_CURRENT_COMPILER_V11'):
   plan,base=F.selected_plan(L,mode);names.update(row['source'] for row in plan.values())
   s=json.loads((ROOT/base).read_bytes());names.update(s['programs']);names.update(s['payload_sources'])
  names.update(L._selection(L.R5_HOSTED_PROFILE,L.R5_DG17_COMPOSED_SOURCE_REVISION)[0])
  names.update(L._selection(L.R5_HOSTED_PROFILE,L.R5_BUDGET5_BUILDER_SOURCE_REVISION)[0])
  names.update(L._selection(L.R5_HOSTED_PROFILE,L.R5_DG17_OWNER_TEMPORARY_SOURCE_REVISION)[0])
  for attr in F.HISTORIES:names.update(row[0] for row in getattr(L,attr,{}).values())
  for attr in ('R5_RUNTIME_DIRECTORY_REASON_EXECUTOR_MEMBER','R5_RUNTIME_DEFAULT_ACL_EXECUTOR_MEMBER','R5_RUNTIME_DIRECTORY_MODE_EXECUTOR_MEMBER'):names.add(getattr(L,attr))
  for name in names:
   p=self.source/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p);p.chmod((ROOT/name).stat().st_mode&0o777)
  self.S=load(self.source/'scripts/qualify-work-graph-c5-setup.py','actual_hosted_reader')

 def current(self):return self.S.hosted_current_owner(self.source)

 def actual_state(self,engine):
  names=set(engine.B.SPEC['programs'])|set(engine.B.SPEC['payload_sources'])
  return {'files':{n:{'sha256':sha((self.source/n).read_bytes())} for n in names}}

 def engine(self,revision_name,name='selected_revision_loader'):
  L=load(self.source/LOADER,name);return L,L._Engine(L.R5_HOSTED_PROFILE,source_revision=getattr(L,revision_name))

 def test_actual_current_v11_reader_and_compiler_capture(self):
  current=self.current();self.assertEqual(len(current.SOURCES),13)
  self.assertNotIn(OLD_BASE[0],current.SOURCES)
  self.assertEqual((len(current.SOURCES[NEW_BASE[0]][0]),sha(current.SOURCES[NEW_BASE[0]][0])),NEW_BASE[1:3])
  self.assertEqual(current.SPEC['selection_origins']['base_actual_member'],NEW_BASE[0])
  self.assertEqual(current.B.SPEC['programs'][BUILDER],NEW_BASE[3])
  self.assertEqual(sha((self.source/BUILDER).read_bytes()),NEW_BASE[3])
  current.B._producer_contract(self.actual_state(current))
  self.assertEqual(sha(current.SOURCES[COMPILER][0]),CURRENT)
  current.CHECK()
  self.assertEqual(sha(current.Q.LOADED_COMPILER),CURRENT)
  self.assertEqual(sha((self.source/COMPILER).read_bytes()),CURRENT)

 def test_historical_v10_exact_tuple_loads_its_retained_compiler(self):
  # V10 keeps the actual builder base and the 8754 compiler; it never reads the current compiler.
  L,captured=self.engine('R5_BUDGET5_BUILDER_SOURCE_REVISION');E=captured.load()
  self.assertEqual(sha(E.SOURCES[COMPILER][0]),V10_COMPILER)
  self.assertEqual(sha((self.source/V10_MEMBER).read_bytes()),V10_COMPILER)
  self.assertNotEqual(sha((self.source/COMPILER).read_bytes()),V10_COMPILER)
  self.assertEqual((len(E.SOURCES[NEW_BASE[0]][0]),sha(E.SOURCES[NEW_BASE[0]][0])),NEW_BASE[1:3])
  self.assertEqual(E.B.SPEC['programs'][BUILDER],NEW_BASE[3])
  E.B._producer_contract(self.actual_state(E))
  E.CHECK();self.assertEqual(sha(E.Q.LOADED_COMPILER),V10_COMPILER)
  selected=L._selection(L.R5_HOSTED_PROFILE,L.R5_BUDGET5_BUILDER_SOURCE_REVISION)
  self.assertEqual(sha(json.dumps(literal(selected),sort_keys=True,separators=(',',':')).encode()),V10_TUPLE)
  self.assertEqual(dict(L.R5_DG17_COMPOSED_COMPILER_PHYSICAL_HISTORY),{COMPILER:(V10_MEMBER,V10_COMPILER)})

 def test_current_and_retained_compilers_do_not_cross_revisions(self):
  L=load(self.source/LOADER,'compiler_rows')
  old=L._selection(L.R5_HOSTED_PROFILE,L.R5_BUDGET5_BUILDER_SOURCE_REVISION);new=L._selection(L.R5_HOSTED_PROFILE,L.R5_DG17_OWNER_TEMPORARY_SOURCE_REVISION)
  self.assertEqual((old[0][COMPILER],new[0][COMPILER]),(V10_COMPILER,CURRENT))
  self.assertEqual({n:p for n,p in old[0].items() if n!=COMPILER},{n:p for n,p in new[0].items() if n!=COMPILER})
  self.assertEqual(literal(old[1:]),literal(new[1:]))
  for revision in (L.R5_DG17_COMPOSED_SOURCE_REVISION,L.R5_BUDGET5_BUILDER_SOURCE_REVISION):
   self.assertEqual(L._selection(L.R5_HOSTED_PROFILE,revision)[0][COMPILER],V10_COMPILER)
  # Current bytes at the retained member: V9 and V10 refuse; the current tuple is unaffected.
  retained=self.source/V10_MEMBER;kept=retained.read_bytes();retained.write_bytes((self.source/COMPILER).read_bytes())
  for revision in ('R5_BUDGET5_BUILDER_SOURCE_REVISION','R5_DG17_COMPOSED_SOURCE_REVISION'):
   with self.subTest(revision=revision),self.assertRaisesRegex(ValueError,'Unsupported fixed C5 execution member: '+COMPILER):self.engine(revision)
  self.assertEqual(sha(self.current().SOURCES[COMPILER][0]),CURRENT)
  # Retained bytes at the current path: the current tuple refuses; V10 still loads its retained member.
  retained.write_bytes(kept);(self.source/COMPILER).write_bytes(kept)
  with self.assertRaisesRegex(ValueError,'Unsupported fixed C5 execution member: '+COMPILER):self.current()
  self.assertEqual(sha(self.engine('R5_BUDGET5_BUILDER_SOURCE_REVISION')[1].load().SOURCES[COMPILER][0]),V10_COMPILER)

 def test_same_size_altered_retained_compiler_byte_refuses_v10(self):
  captured=self.engine('R5_BUDGET5_BUILDER_SOURCE_REVISION')[1];captured.check()
  p=self.source/V10_MEMBER;b=p.read_bytes();p.write_bytes(b[:100]+bytes([b[100]^1])+b[101:])
  with self.assertRaisesRegex(ValueError,'Captured C5 execution source'):captured.check()
  with self.assertRaisesRegex(ValueError,'Unsupported fixed C5 execution member: '+COMPILER):self.engine('R5_BUDGET5_BUILDER_SOURCE_REVISION')
  self.assertEqual(sha(self.current().SOURCES[COMPILER][0]),CURRENT)

 def test_frozen_v10_fixture_keeps_its_compiler_and_v11_fixture_selects_the_actual_one(self):
  F=load(self.source/'tests/c5-selected-source-fixture.py','v10_v11_fixture')
  frozen=self.parent/'frozen-v10';F.materialize(self.source,frozen,'R5_CURRENT_BUILDER_V10')
  self.assertEqual(sha((frozen/COMPILER).read_bytes()),V10_COMPILER)
  L=load(frozen/LOADER,'frozen_v10_loader');E=L._Engine(L.R5_HOSTED_PROFILE,source_revision=L.R5_BUDGET5_BUILDER_SOURCE_REVISION).load()
  self.assertEqual(sha(E.SOURCES[COMPILER][0]),V10_COMPILER)
  actual=self.parent/'current-v11';F.materialize(self.source,actual,'R5_CURRENT_COMPILER_V11')
  self.assertEqual(sha((actual/COMPILER).read_bytes()),CURRENT)
  self.assertFalse((actual/V10_MEMBER).exists())
  L=load(actual/LOADER,'current_v11_loader');E=L._Engine(L.R5_HOSTED_PROFILE,source_revision=L.R5_DG17_OWNER_TEMPORARY_SOURCE_REVISION).load()
  self.assertEqual(sha(E.SOURCES[COMPILER][0]),CURRENT)

 def test_stale_v10_loader_keeps_its_exact_tuple(self):
  # The integrated V10 loader pair stays an exact historical row of the held reader; it has no
  # retained member for its compiler, so it refuses the actual compiler instead of adopting it.
  if BASELINE_V10 is None:self.skipTest('needs --baseline-v10-loader <integrated V10 loader>')
  raw=BASELINE_V10.read_bytes();self.assertEqual((len(raw),sha(raw)),V10_LOADER)
  (self.source/LOADER).write_bytes(raw)
  with self.assertRaisesRegex(ValueError,'Unsupported fixed C5 execution member: '+COMPILER):self.current()
  (self.source/COMPILER).write_bytes((self.source/V10_MEMBER).read_bytes());stale=self.current()
  self.assertEqual(sha(stale.SOURCES[COMPILER][0]),V10_COMPILER)
  self.assertEqual(stale.B.SPEC['programs'][BUILDER],NEW_BASE[3])

 def test_historical_v9_exact_base_loads_but_refuses_actual_builder(self):
  L,captured=self.engine('R5_DG17_COMPOSED_SOURCE_REVISION');E=captured.load()
  self.assertNotIn(NEW_BASE[0],E.SOURCES)
  self.assertEqual((len(E.SOURCES[OLD_BASE[0]][0]),sha(E.SOURCES[OLD_BASE[0]][0])),OLD_BASE[1:3])
  self.assertEqual(E.SPEC['selection_origins']['base_actual_member'],OLD_BASE[0])
  self.assertEqual(E.B.SPEC['programs'][BUILDER],OLD_BASE[3])
  with self.assertRaisesRegex(ValueError,'C5 original producer source differs: scripts/package-contract.py'):
   E.B._producer_contract(self.actual_state(E))
  selected=L._selection(L.R5_HOSTED_PROFILE,L.R5_DG17_COMPOSED_SOURCE_REVISION)
  self.assertEqual(sha(json.dumps(literal(selected),sort_keys=True,separators=(',',':')).encode()),V9_TUPLE)

 def test_current_base_bytes_at_historical_selector_refuse(self):
  # The 8754 regression: current bytes placed at the historically pinned name.
  old=self.source/OLD_BASE[0];raw=(self.source/NEW_BASE[0]).read_bytes()
  self.assertEqual(len(raw),old.stat().st_size);old.write_bytes(raw)
  for revision in ('R5_DG17_COMPOSED_SOURCE_REVISION','R5_RUNTIME_DIRECTORY_MODE_SOURCE_REVISION','R5_INNER_CAPTURE_SOURCE_REVISION'):
   with self.subTest(revision=revision),self.assertRaisesRegex(ValueError,'Unsupported fixed C5 execution member: '+OLD_BASE[0]):
    self.engine(revision)
  F=load(self.source/'tests/c5-selected-source-fixture.py','substituted_v4_fixture')
  with self.assertRaisesRegex(ValueError,'selected member digest'):
   F.materialize(self.source,self.parent/'substituted-v4','R5_CURRENT_V4')
  self.assertFalse((self.parent/'substituted-v4').exists())
  self.assertEqual(len(self.current().SOURCES),13)

 def test_historical_base_bytes_at_current_selector_refuse(self):
  new=self.source/NEW_BASE[0];raw=(self.source/OLD_BASE[0]).read_bytes()
  self.assertEqual(len(raw),new.stat().st_size);new.write_bytes(raw)
  with self.assertRaisesRegex(ValueError,'Unsupported fixed C5 execution member: '+NEW_BASE[0]):self.current()
  self.engine('R5_DG17_COMPOSED_SOURCE_REVISION')[1].load()

 def test_same_size_altered_base_byte_refuses_each_selection(self):
  for name,revision in ((NEW_BASE[0],'R5_BUDGET5_BUILDER_SOURCE_REVISION'),(OLD_BASE[0],'R5_DG17_COMPOSED_SOURCE_REVISION')):
   with self.subTest(name=name):
    captured=self.engine(revision)[1];captured.check()
    p=self.source/name;b=p.read_bytes();i=b.index(b'"programs"')+2;p.write_bytes(b[:i]+bytes([b[i]^1])+b[i+1:])
    self.assertEqual(p.stat().st_size,len(b))
    with self.assertRaisesRegex(ValueError,'Captured C5 execution source'):captured.check()
    with self.assertRaisesRegex(ValueError,'Unsupported fixed C5 execution member: '+name):self.engine(revision)

 def test_selectors_do_not_cross_revisions(self):
  L=load(self.source/LOADER,'selector_rows')
  old=L._selection(L.R5_HOSTED_PROFILE,L.R5_DG17_COMPOSED_SOURCE_REVISION);new=L._selection(L.R5_HOSTED_PROFILE,L.R5_BUDGET5_BUILDER_SOURCE_REVISION)
  self.assertEqual((old[1],old[0][old[1]],old[4]['base_actual_member']),(OLD_BASE[0],OLD_BASE[2],OLD_BASE[0]))
  self.assertEqual((new[1],new[0][new[1]],new[4]['base_actual_member']),(NEW_BASE[0],NEW_BASE[2],NEW_BASE[0]))
  self.assertNotIn(NEW_BASE[0],old[0]);self.assertNotIn(OLD_BASE[0],new[0]);self.assertNotIn(old[3],new[0]);self.assertNotIn(new[3],old[0])
  self.assertEqual({n:p for n,p in old[0].items() if n not in (old[1],old[3])},{n:p for n,p in new[0].items() if n not in (new[1],new[3])})
  a=json.loads((self.source/old[3]).read_bytes());b=json.loads((self.source/new[3]).read_bytes())
  self.assertEqual(a.pop('selection_origins'),dict(old[4]));self.assertEqual(b.pop('selection_origins'),dict(new[4]));self.assertEqual(a,b)
  a=json.loads((self.source/old[1]).read_bytes());b=json.loads((self.source/new[1]).read_bytes())
  self.assertEqual((a['programs'].pop(BUILDER),b['programs'].pop(BUILDER)),(OLD_BASE[3],NEW_BASE[3]));self.assertEqual(a,b)
  for revision in (L.R5_DG17_COMPOSED_SOURCE_REVISION,L.R5_BUDGET5_BUILDER_SOURCE_REVISION):
   with self.assertRaisesRegex(ValueError,'fixed R5 hosted profile'):L._selection(L.R4_BUILD_CACHE_PROFILE,revision)

 def test_stale_v9_loader_cannot_claim_the_actual_builder(self):
  # A stale owner is not silently current: its exact V9 tuple refuses the actual builder.
  if BASELINE is None:self.skipTest('needs --baseline-loader <8754 loader>')
  raw=BASELINE.read_bytes();self.assertEqual((len(raw),sha(raw)),(58016,'fb416808867945e763d5ed175d49722fc21ca4e4cc933deb5471fd43ada1a33c'))
  (self.source/LOADER).write_bytes(raw)
  with self.assertRaisesRegex(ValueError,'Unsupported fixed C5 execution member: '+COMPILER):self.current()
  # Its exact V9 tuple names the 8754 compiler at the logical path; supply those exact bytes.
  (self.source/COMPILER).write_bytes((self.source/V10_MEMBER).read_bytes());stale=self.current()
  self.assertEqual(sha(stale.SOURCES[COMPILER][0]),V10_COMPILER)
  self.assertEqual(stale.B.SPEC['programs'][BUILDER],OLD_BASE[3])
  with self.assertRaisesRegex(ValueError,'C5 original producer source differs: scripts/package-contract.py'):
   stale.B._producer_contract(self.actual_state(stale))

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
  for revision in (L.R5_BUDGET5_BUILDER_SOURCE_REVISION,L.R5_DG17_OWNER_TEMPORARY_SOURCE_REVISION):
   for profile in (L.CURRENT_PROFILE,L.R4_BUILD_CACHE_PROFILE):
    with self.assertRaisesRegex(ValueError,'fixed R5 hosted profile'):L._selection(profile,revision)

 def test_all_prior_pin_and_revision_tables_are_unchanged(self):
  current=load(self.source/LOADER,'current_pin_tables')
  manifest=json.loads((self.source/'test-support/r5-continuity-compiler-history/MANIFEST.json').read_bytes())
  names=manifest['prior_table_names'];self.assertTrue(names)
  tables={n:literal(getattr(current,n)) for n in names}
  self.assertEqual(sha(json.dumps(tables,sort_keys=True,separators=(',',':')).encode()),manifest['prior_tables_sha256'])
  # The V10 loader's tables (V1-V10) are unchanged under V11 as well.
  retained=json.loads((self.source/'test-support/r5-dg17-composed-compiler-history/MANIFEST.json').read_bytes())
  self.assertEqual((retained['prior_loader']['bytes'],retained['prior_loader']['sha256']),V10_LOADER)
  self.assertEqual([(m['path'],m['bytes'],m['sha256']) for m in retained['members']],[(V10_MEMBER,len((self.source/V10_MEMBER).read_bytes()),V10_COMPILER)])
  later=retained['prior_table_names'];self.assertGreater(len(later),len(names));self.assertLessEqual(set(names),set(later))
  self.assertEqual(sha(json.dumps({n:literal(getattr(current,n)) for n in later},sort_keys=True,separators=(',',':')).encode()),retained['prior_tables_sha256'])
  if BASELINE_V10 is not None:
   v10=load(BASELINE_V10,'v10_pin_tables')
   declared=[n for n in vars(v10) if n.isupper() and n!='ROOT'];self.assertGreaterEqual(len(declared),115)
   for n in declared:self.assertEqual(literal(getattr(current,n)),literal(getattr(v10,n)),n)
   profiles=sorted({v for n,v in vars(v10).items() if n.endswith('PROFILE') and type(v) is str})
   revisions=[None]+sorted({v for n,v in vars(v10).items() if n.endswith('SOURCE_REVISION') and type(v) is str})
   accepted=0
   for profile in profiles:
    for revision in revisions:
     try:expected=literal(v10._selection(profile,revision))
     except ValueError as e:
      with self.assertRaises(ValueError) as refused:current._selection(profile,revision)
      self.assertEqual(str(refused.exception),str(e),(profile,revision))
     else:accepted+=1;self.assertEqual(literal(current._selection(profile,revision)),expected,(profile,revision))
   self.assertGreaterEqual(accepted,26)
  if BASELINE is not None:
   old=load(BASELINE,'original_pin_tables')
   for n in names:self.assertEqual(literal(getattr(current,n)),literal(getattr(old,n)),n)
   # Every baseline declaration and every baseline selector row is unchanged.
   declared=[n for n in vars(old) if n.isupper() and n!='ROOT'];self.assertGreaterEqual(len(declared),110)
   for n in declared:self.assertEqual(literal(getattr(current,n)),literal(getattr(old,n)),n)
   profiles=sorted({v for n,v in vars(old).items() if n.endswith('PROFILE') and type(v) is str})
   revisions=[None]+sorted({v for n,v in vars(old).items() if n.endswith('SOURCE_REVISION') and type(v) is str})
   accepted=0
   for profile in profiles:
    for revision in revisions:
     try:expected=literal(old._selection(profile,revision))
     except ValueError as e:
      with self.assertRaises(ValueError) as refused:current._selection(profile,revision)
      self.assertEqual(str(refused.exception),str(e),(profile,revision))
     else:accepted+=1;self.assertEqual(literal(current._selection(profile,revision)),expected,(profile,revision))
   self.assertGreaterEqual(accepted,25)

if __name__=='__main__':
 def fence(event,args):
  if event.startswith(('subprocess.','socket.','ctypes.')) or event in ('os.fork','os.exec','os.posix_spawn','os.system','os.kill','os.killpg'):
   raise AssertionError('C5 SOURCE CONTROL ATTEMPTED DISPATCH_OR_NATIVE_EFFECT: '+event)
 sys.addaudithook(fence)
 unittest.main(verbosity=2)
