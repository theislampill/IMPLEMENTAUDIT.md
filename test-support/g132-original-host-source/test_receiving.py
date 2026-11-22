"""Original owner functions, disposable documents and Git object reads only."""
from copy import deepcopy
import ast
import json
import os
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest

from source_fixture import (BASE, BRANCH, BUILD, C53, E76, EPISODE, M5, desc, enc, fixture,
                            git, historical_manifest, load_owner, source_manifests, source_row)


class OwnerControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.driver = load_owner('run')
        cls.g3, cls.operation, cls.proof, cls.host = [load_owner(n) for n in
            ('g3_receiving', 'operation', 'proof_consumer', 'host_utility')]
        cls.manifest, cls.previous, cls.changes, cls.canonical = source_manifests()

    def test_finite_host_all_images_and_tools(self):
        old_git = '824d5b2fffef332ec7ba053e579659bb12f26a0b4747da6f9c6dc0e71d36f235'
        new_git = '08ca4d2ee4d8915e86f1faaa52603752507c57af1d16d451dec9992bc9b6d801'
        for image in ('20261101.360.1', '20261111.370.1', '20261111.127.1', '20261116.376.1'):
            with self.subTest(image=image):
                facts = dict(platform='linux', architecture='x86_64', os=dict(ID='ubuntu',VERSION_ID='24.04'),
                             python_version=[3,12,3], image_os='ubuntu24', uid=0,euid=0,gid=0,egid=0,image_version=image)
                selected = self.host.select_g1_host_profile(facts)
                pin = new_git if image=='20261116.376.1' else old_git
                tools = {n: dict(sha256=h) for n,h in (
                    ('git', pin), ('bwrap','52231e1caf55bcbc667b269f49c63599a6f7db4767ae6a039580d0ff853db712'),
                    ('python3.12','e50d468e8b0adfb05733f5b87b3cff34829c4a8c1aea50c865aa8bdfe4bb150f'))}
                self.driver.validate_inventory_tool_bytes(self.host, selected, tools, True)
                tools['git']['sha256'] = old_git if pin==new_git else new_git
                with self.assertRaisesRegex(Exception,'SELECTED_TOOL_BYTES_CHANGED'):
                    self.driver.validate_inventory_tool_bytes(self.host, selected, tools, True)
        for changed in (dict(image_version='20261116.376.2'),dict(euid=False),dict(python_version=[3,12,4])):
            with self.assertRaisesRegex(ValueError,'HOST_PROFILE_CHANGED'):
                self.host.select_g1_host_profile(dict(facts, **changed))

    def test_tuple_and_physical_executor(self):
        op = self.operation
        logical = 'scripts/work-graph-c5-executor.py'
        physical = 'test-support/r5-hosted-git-08ca-source/work-graph-c5-executor.py'
        self.assertEqual(op.REVISION, 'G132_HOST_PROFILE_SUCCESSOR_SOURCE_20261122_V1')
        self.assertEqual(op.C5_SOURCE_REVISION, self.proof.C5_SOURCE_REVISION)
        self.assertEqual(self.proof.C5_SOURCE_REVISION, self.g3.C5_SOURCE_REVISION)
        self.assertEqual(op.LOADER_SHA256, source_row(C53,'scripts/load-work-graph-c5-executor.py')['sha256'])
        self.assertEqual(len(op.EXECUTING_SOURCE_BINDINGS),13)
        self.assertEqual(set(op.EXECUTING_SOURCE_BINDINGS),
                         {k for k in self.g3.EXECUTING_SOURCE_BINDINGS})
        self.assertEqual(op.EXECUTING_SOURCE_BINDINGS, self.proof.EXECUTING_SOURCE_PINS)
        for path, pin in op.EXECUTING_SOURCE_BINDINGS.items():
            row = source_row(C53, physical if path==logical else path)
            self.assertEqual(pin, {k:row[k] for k in ('sha256','bytes')})
        self.assertEqual(op.EXECUTING_SOURCE_BINDINGS[logical]['bytes'],108100)
        observation = dict(source_commit=C53, source_tree=self.manifest['tree'],
                           provider=dict(source=dict(projection='ALL_ACTUAL_BYTES_NO_GIT_OR_HIDDEN_OMISSIONS')),
                           executing_sources=deepcopy(op.EXECUTING_SOURCE_BINDINGS))
        key = desc(enc(observation))['sha256']
        self.assertEqual(self.g3.validate_source_acquisition(observation,key),key)
        row = source_row(C53, logical)
        observation['executing_sources'][logical] = {k:row[k] for k in ('sha256','bytes')}
        with self.assertRaisesRegex(self.g3.Refusal,'CURRENT_C5_EXECUTION_SOURCE_BINDINGS'):
            self.g3.validate_source_acquisition(observation,desc(enc(observation))['sha256'])

    def test_source_owner_consistency_and_generated_pin_still_closed(self):
        d, p = self.driver, self.proof
        self.assertEqual((d.SOURCE_COMMIT, d.SOURCE_TREE, d.SOURCE_PARENT),
                         (C53, self.manifest['tree'],self.manifest['parent_commit']))
        self.assertEqual((p.SOURCE, p.TREE, p.SOURCE_PARENT), (d.SOURCE_COMMIT, d.SOURCE_TREE, d.SOURCE_PARENT))
        self.assertEqual((self.host.SOURCE_COMMIT, self.host.SOURCE_TREE), (d.SOURCE_COMMIT,d.SOURCE_TREE))
        self.assertEqual((d.SOURCE_BRANCH,d.SOURCE_FILES,d.SOURCE_BYTES),(BRANCH,1778,167283667))
        self.assertEqual((p.SOURCE_FILES,p.SOURCE_BYTES),(1778,167283667))
        self.assertEqual(d.SETUP_SHA,source_row(C53,d.SETUP)['sha256'])
        if d.MANIFEST_SHA == desc(historical_manifest())['sha256']:
            with self.assertRaisesRegex(Exception,'MANIFEST_SUBJECT_REFUSED|MANIFEST_PIN_REFUSED'):
                d.manifest()
        else:
            self.assertEqual(len(d.manifest()),1778)

    def test_original_manifest_reader_checks_subject_and_parent_tree(self):
        with TemporaryDirectory() as tmp:
            directory=Path(tmp)
            shutil.copyfile(EPISODE/'run.py',directory/'run.py')
            driver=load_owner('run',directory)
            path=directory/'SOURCE_MANIFEST.json'
            raw=enc(self.manifest)
            path.write_bytes(raw)
            driver.MANIFEST_SHA=desc(raw)['sha256']
            self.assertEqual(len(driver.manifest()),1778)
            for change in (dict(parent_tree='0'*40),dict(extra='SYNTHETIC')):
                raw=enc(dict(self.manifest,**change))
                path.write_bytes(raw)
                driver.MANIFEST_SHA=desc(raw)['sha256']
                with self.assertRaisesRegex(driver.Refusal,'MANIFEST_SUBJECT_REFUSED'):
                    driver.manifest()

    def test_unpinned_loader_is_refused_before_evaluation(self):
        with TemporaryDirectory() as temp:
            source = Path(temp)
            (source/'scripts').mkdir()
            (source/'scripts/load-work-graph-c5-executor.py').write_bytes(b'raise AssertionError("unexpected evaluation")')
            with self.assertRaisesRegex(ValueError, 'LOADER_PIN_DIFFERS'):
                self.operation.load_selected(source)
        owner = ast.parse((EPISODE/'operation.py').read_bytes())
        loader = next(n for n in owner.body if isinstance(n, ast.FunctionDef) and n.name=='load_selected')
        self.assertIn('G132_HOST_PROFILE_SOURCE_REVISION', {n.attr for n in ast.walk(loader) if isinstance(n, ast.Attribute)})

    def test_population_limits(self):
        self.assertEqual((self.g3.FILE_LIMIT,self.g3.TOTAL_LIMIT,self.g3.ENTRY_LIMIT,self.g3.DEPTH_LIMIT),
                         (16*1024**2,64*1024**2,4096,16))
        scope = json.loads((EPISODE/'ORIGINAL_SCOPE.json').read_bytes())
        self.assertEqual(scope['original_population'],dict(total=157,DG16=48,DG17=95,DG18=14))
        self.assertEqual(len(git('ls-files', str(EPISODE)).splitlines()),42)
        outside = git('ls-files', 'qualification/dg16-r5-g1-hosted-entry', '.github/workflows/dg16-r5-g1-hosted-episode.yml')
        self.assertEqual(len(outside.splitlines()),11)
        self.assertEqual((self.driver.NATIVE_RETAINED_MEMBERS,self.driver.NATIVE_CHANGED_MEMBERS),(86,3))

    def test_complete_source_and_m5_relation(self):
        self.g3.receive_maintained_source_rows(self.manifest,self.previous,self.changes,
                                               self.changes[:14],self.canonical,BUILD)

    def test_member_bytes_modes_paths_and_package_owners(self):
        defects = [('sha256',self.canonical[0]),('mode',BUILD[0]),('bytes',self.changes[0]['path']),
                   ('drop',self.canonical[-1]),('extra','unlisted.py'),('duplicate',self.canonical[1])]
        for kind, path in defects:
            with self.subTest(kind=kind,path=path):
                manifest=deepcopy(self.manifest)
                rows=manifest['members']; row=next((r for r in rows if r['path']==path),None)
                if kind=='drop': rows.remove(row)
                elif kind=='extra': rows.append(dict(rows[0],path=path))
                elif kind=='duplicate': rows.append(dict(row))
                elif kind=='bytes': row[kind]+=1
                elif kind=='mode': row[kind]='100755' if row[kind]=='100644' else '100644'
                else: row[kind]='0'*64
                with self.assertRaises(self.g3.Refusal):
                    self.g3.receive_maintained_source_rows(manifest,self.previous,self.changes,
                        self.changes[:14],self.canonical,BUILD)

    def test_delta_and_claimed_subsets(self):
        hybrids = [self.changes[:-1], self.changes[:-1]+[self.changes[0]], list(reversed(self.changes))]
        for rows, immediate, canonical, build in [
                *((r, self.changes[:14], self.canonical, BUILD) for r in hybrids),
                (self.changes,self.changes[1:15],self.canonical,BUILD),
                (self.changes,self.changes[:14],self.canonical[:-1]+[BUILD[0]],BUILD),
                (self.changes,self.changes[:14],self.canonical,BUILD[:-1]+[self.canonical[0]])]:
            with self.assertRaises(self.g3.Refusal):
                self.g3.receive_maintained_source_rows(self.manifest,self.previous,rows,immediate,canonical,build)


@unittest.skipUnless(os.environ.get('G132_TEST_V4_INPUT'), 'exact retained v4 body needed for end-to-end receiver control')
class DispatchControls(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.history = json.loads(Path(os.environ['G132_TEST_V4_INPUT']).read_bytes())
        cls.tmp = TemporaryDirectory()
        cls.directory = Path(cls.tmp.name)
        shutil.copyfile(EPISODE/'g3_receiving.py',cls.directory/'g3_receiving.py')
        cls.g3 = load_owner('g3_receiving', cls.directory)
        cls.source = source_manifests()
        (cls.directory/'SOURCE_MANIFEST.json').write_bytes(enc(cls.source[0]))

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_dispatches_strict_v5(self):
        acq,basis,bodies=fixture(*self.source,self.history)
        result=self.g3.receive_retained_package_relation(acq,basis,bodies)
        self.assertTrue(result==acq['package_relation'])

    def test_external_scope_pin_and_existing_size_bound(self):
        acq,receipt,bodies=fixture(*self.source,self.history)
        scope=json.loads((EPISODE/'ORIGINAL_SCOPE.json').read_bytes())
        scope.update({k:v for k,v in receipt.items() if k!='received_inputs'})
        scope['received_inputs'].update(receipt['received_inputs'])
        # The temporary scope contains synthetic current identifiers and body hashes only.
        raw=(json.dumps(scope,indent=2,sort_keys=True)+'\n').encode()
        self.assertLessEqual(len(raw),8192)
        (self.directory/'ORIGINAL_SCOPE.json').write_bytes(raw)
        consumer=load_owner('g3_receiving',self.directory)
        with self.assertRaisesRegex(consumer.Refusal,'ORIGINAL_SCOPE_PIN'):
            consumer.scope_basis()
        consumer.SCOPE_SHA=desc(raw)['sha256']
        _,bound=consumer.scope_basis()
        self.assertTrue(consumer.receive_retained_package_relation(acq,bound,bodies)==acq['package_relation'])
        changed=dict(scope,maintained_source_authority=dict(scope['maintained_source_authority'],controller='SYNTHETIC-STALE'))
        (self.directory/'ORIGINAL_SCOPE.json').write_bytes(enc(changed))
        with self.assertRaisesRegex(consumer.Refusal,'ORIGINAL_SCOPE_PIN'):
            consumer.scope_basis()

    def test_historical_v4_and_no_schema_relabel(self):
        with TemporaryDirectory() as tmp:
            directory=Path(tmp)
            shutil.copyfile(EPISODE/'g3_receiving.py',directory/'g3_receiving.py')
            (directory/'SOURCE_MANIFEST.json').write_bytes(historical_manifest())
            old=load_owner('g3_receiving',directory)
            basis=json.loads(git('show', BASE+':qualification/dg16-r5-g1-hosted-episode/ORIGINAL_SCOPE.json'))
            self.assertTrue(old.receive_retained_package_relation(self.history,basis,{})==basis['retained_package_relation'])
        acq=dict(self.history,schema='dg16.current-source-maintained-package-acquisition.v5')
        with self.assertRaises(self.g3.Refusal):
            self.g3.receive_retained_package_relation(acq,basis,{})

    def test_self_consistent_but_stale_or_wrong_decisions(self):
        for name, path, value in (
                ('ROOT_SOURCE_CURRENTNESS.json',('receipt_sha256',),'d'*64),
                ('ROOT_SOURCE_CURRENTNESS.json',('subject','parent_tree'),'a'*40),
                ('ROOT_PACKAGE_SOURCE_APPLICABILITY.json',('actor',),'OTHER-SYNTHETIC-ISSUER'),
                ('ROOT_PACKAGE_SOURCE_APPLICABILITY.json',('decision',),'ACCEPT_HISTORICAL'),
                ('ROOT_PACKAGE_SOURCE_APPLICABILITY.json',('original_awards',),['SYNTHETIC']),
                ('INDEPENDENT_RECEIVING.json',('actor',),'SYNTHETIC-ROOT'),
                ('PHYSICAL_PRODUCT_READBACK.json',('all_members_exact',),False),
                ('PRODUCT_PUBLICATION_RECEIVING.json',('subject','branch'),'pro/synthetic-wrong')):
            with self.subTest(name=name,path=path):
                def mutate(n,doc):
                    if n==name:
                        target=doc
                        for key in path[:-1]: target=target[key]
                        target[path[-1]]=value
                args=fixture(*self.source,self.history,mutate=mutate)
                with self.assertRaises(self.g3.Refusal):
                    self.g3.receive_retained_package_relation(*args)

    def test_exact_historical_bodies_and_external_scope_binding(self):
        acq,basis,bodies=fixture(*self.source,self.history)
        for name in acq['historical_evidence']:
            changed=deepcopy(acq)
            changed['historical_evidence_bodies'][name]+=' '
            changed['historical_evidence'][name]=desc(changed['historical_evidence_bodies'][name].encode())
            wire=enc(changed)
            revised=dict(basis,received_inputs={'SOURCE_ACQUISITION.json':desc(wire)})
            with self.assertRaises(self.g3.Refusal):
                self.g3.receive_retained_package_relation(changed,revised,{'SOURCE_ACQUISITION.json':wire})
        for revised in (dict(basis,received_inputs={'SOURCE_ACQUISITION.json':desc(b'wrong')}),
                        dict(basis,current_subject=dict(commit=E76,tree='a'*40)),
                        dict(basis,maintained_source_authority=dict(basis['maintained_source_authority'],controller='STALE'))):
            with self.assertRaises(self.g3.Refusal):
                self.g3.receive_retained_package_relation(acq,revised,bodies)


if __name__=='__main__':
    unittest.main()
