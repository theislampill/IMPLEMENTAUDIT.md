#!/usr/bin/env python3
"""Actual finite argv/sealed-byte controls; no Bubblewrap or native award."""
import copy
import fcntl
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('finite_elf_fixtures', REPO/'tests/work-graph-elf-interpreter-cases.py')
E = importlib.util.module_from_spec(spec)
spec.loader.exec_module(E)
Q, S = E.Q, E.S
POLICY = 'SINGLE_LINK_ALL_IMAGE_FILES_READ_ONLY_ROOT'


class StopBeforeProcess(BaseException):
    pass


class MaterializationControls(unittest.TestCase):
    def prepare(self, directory, *, scope=S.SCOPE):
        s = E.InterpreterControls().session(directory)
        s.SCOPE = scope
        files = E.runtime_files()
        files['/usr/lib/python3.12/fixture.py'] = (b'public constructed runtime data\n', 0o444)
        files['/work/source.txt'] = (b'public constructed source data\n', 0o444)
        manifest, digest = s._image(files, {})
        node = dict(id='CONSTRUCTED_MATERIALIZATION', source='true\n', source_sha256=Q.sha(b'true\n'))
        acquired = dict(images={node['id']:(files,manifest)}, state={},
                        acquired=dict(scope=scope, inputs={node['id']:dict(image_digest=digest)}))
        return s, files, manifest, acquired, node

    def launch_arguments(self, s, files, acquired, node, target):
        observations = []
        def stop(command, **options):
            self.assertEqual(command[:2], ['/usr/bin/bwrap', '--args'])
            args = os.pread(int(command[2]), 131072, 0).decode().rstrip('\0').split('\0')
            copied = {}
            for index, arg in enumerate(args):
                if arg not in ('--file', '--ro-bind-data'):
                    continue
                fd, name = int(args[index+1]), args[index+2]
                self.assertIn(fd, options['pass_fds'])
                seal = fcntl.fcntl(fd, fcntl.F_GET_SEALS)
                required = fcntl.F_SEAL_WRITE|fcntl.F_SEAL_GROW|fcntl.F_SEAL_SHRINK|fcntl.F_SEAL_SEAL
                self.assertEqual(seal & required, required)
                self.assertEqual(os.pread(fd, len(files[name][0])+1, 0), files[name][0])
                copied[name] = arg
            observations.append(dict(args=args, copied=copied, command=command, options=options))
            raise StopBeforeProcess()
        with patch.object(Q.subprocess, 'Popen', stop):
            with self.assertRaises(StopBeforeProcess):
                s._execute(acquired,node,dict(key='f'*64),target)
        self.assertEqual(len(observations),1)
        return observations[0]

    def test_all_runtime_and_source_members_are_linked_with_same_sealed_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            s,files,manifest,acquired,node = self.prepare(Path(td))
            observed = self.launch_arguments(s,files,acquired,node,Path(td)/'execution')
            self.assertEqual(observed['copied'],{name:'--file' for name in files})
            self.assertEqual(manifest['finite_file_materialization'],POLICY)
            import json
            dispatch=json.loads((Path(td)/'execution/dispatch.json').read_bytes())
            self.assertEqual(dispatch['finite_file_materialization'],POLICY)
            args=observed['args']
            self.assertIn('--unshare-all',args)
            self.assertNotIn('--share-net',args)
            self.assertNotIn('--proc',args)
            self.assertIn('--seccomp',args)
            self.assertEqual(args[args.index('--cap-drop')+1],'ALL')
            remount=args.index('--remount-ro')
            self.assertEqual(args[remount+1],'/')
            self.assertGreater(remount,max(i for i,arg in enumerate(args) if arg=='--file'))
            self.assertEqual([args[i+1:i+3] for i,arg in enumerate(args) if arg=='--dev-bind'],
                             [['/dev/null','/dev/null']])
            self.assertFalse(any(arg in ('--bind','--ro-bind','--bind-fd','--ro-bind-fd') for arg in args))

    def test_missing_or_changed_materialization_refuses_before_any_execution_directory(self):
        with tempfile.TemporaryDirectory() as td:
            s,files,manifest,acquired,node = self.prepare(Path(td))
            for mode in ('missing','changed','writable-root'):
                damaged=copy.deepcopy(manifest)
                if mode=='missing':del damaged['finite_file_materialization']
                elif mode=='changed':damaged['finite_file_materialization']='UNLINKED_RUNTIME'
                else:damaged['root_read_only']=False
                supplied=dict(acquired,images={node['id']:(files,damaged)})
                target=Path(td)/mode
                with self.assertRaisesRegex(Q.WG.WorkGraphError,'finite file materialization'):
                    s._execute(supplied,node,dict(key='f'*64),target)
                self.assertFalse(target.exists())

    def test_other_scope_keeps_original_unlinked_materialization_and_no_new_field(self):
        with tempfile.TemporaryDirectory() as td:
            s,files,manifest,acquired,node = self.prepare(Path(td),scope='CONTROLLED_TASK_REGISTRY_V1')
            observed=self.launch_arguments(s,files,acquired,node,Path(td)/'execution')
            self.assertEqual(observed['copied'],{name:'--ro-bind-data' for name in files})
            self.assertNotIn('finite_file_materialization',manifest)
            import json
            self.assertNotIn('finite_file_materialization',json.loads((Path(td)/'execution/dispatch.json').read_bytes()))

    def test_other_scope_existing_linked_source_policy_stays_source_only(self):
        with tempfile.TemporaryDirectory() as td:
            s,files,manifest,acquired,node = self.prepare(Path(td),scope='CONTROLLED_TASK_REGISTRY_V1')
            manifest['source_materialization']='SINGLE_LINK_FILES_READ_ONLY_ROOT'
            observed=self.launch_arguments(s,files,acquired,node,Path(td)/'execution')
            self.assertEqual(observed['copied'],{name:('--file' if name.startswith('/work/') else '--ro-bind-data') for name in files})

    def test_foreign_scope_cannot_supply_the_finite_materialization_field(self):
        with tempfile.TemporaryDirectory() as td:
            s,files,manifest,acquired,node = self.prepare(Path(td),scope='CONTROLLED_TASK_REGISTRY_V1')
            manifest['finite_file_materialization']=POLICY
            target=Path(td)/'must-not-start'
            with self.assertRaisesRegex(Q.WG.WorkGraphError,'finite file materialization'):
                s._execute(acquired,node,dict(key='f'*64),target)
            self.assertFalse(target.exists())


if __name__=='__main__':
    unittest.main(verbosity=2)
