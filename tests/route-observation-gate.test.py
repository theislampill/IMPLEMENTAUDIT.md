"""Seam-level real-filesystem checks; no Git/store/native fixtures or authority.
A regression to creating a lock namespace in observe-current fails the first tests.
The canonical-record backend is deliberately replaced only where noted; these
checks do NOT substitute for the complete route-obligation contract.
"""
import argparse, contextlib, errno, hashlib, importlib.util, io, json, os, pathlib, shutil, stat, subprocess, sys, tempfile, unittest
from unittest.mock import patch
parser=argparse.ArgumentParser();parser.add_argument('--source',type=pathlib.Path,required=True);parser.add_argument('--output-root',type=pathlib.Path)
a,rest=parser.parse_known_args();sys.argv=[sys.argv[0],*rest]
path=a.source/'skills/implementaudit/scripts/route-transaction.py'
spec=importlib.util.spec_from_file_location('route_gate_subject',path);route=importlib.util.module_from_spec(spec);sys.modules[spec.name]=route;spec.loader.exec_module(route)
def snapshot(root):
    return [(p.relative_to(root).as_posix(),stat.S_IMODE(p.lstat().st_mode),p.lstat().st_size,os.readlink(p) if p.is_symlink() else hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None) for p in sorted(root.rglob('*'))]
class ObserverGateTests(unittest.TestCase):
    def setUp(self):
        output_root = a.output_root
        if output_root is not None:
            output_root.mkdir(parents=True, exist_ok=True)
        self.tmp=tempfile.TemporaryDirectory(prefix='gate-check-', dir=str(output_root) if output_root is not None else None);self.addCleanup(self.tmp.cleanup);self.root=pathlib.Path(self.tmp.name);self.common=self.root/'common';self.common.mkdir()
    def observe_absent_record(self):
        # Git lookup replaced with a literal absent-record read. Real command and
        # lock filesystem behavior run unchanged; no fabricated passing record.
        with patch.object(route,'repo_context',return_value=(self.root,'',str(self.common))),patch.object(route,'current_ref',return_value=(None,None)),contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):route.command_observe_current(argparse.Namespace(controller='inert-test'))
    def test_observe_absent_namespace_does_not_create_it(self):
        before=snapshot(self.root);self.observe_absent_record();self.assertEqual(snapshot(self.root),before)
    def test_observe_absent_gate_does_not_create_it(self):
        (self.common/'implementaudit-locks').mkdir();before=snapshot(self.root);self.observe_absent_record();self.assertEqual(snapshot(self.root),before)
    def test_observe_existing_gate_does_not_modify_it(self):
        with route.namespace_gate(str(self.common)):pass
        before=snapshot(self.root);self.observe_absent_record();self.assertEqual(snapshot(self.root),before)
    def test_capture_provider_rebinds_exact_route_owner_without_native_execution(self):
        provider_path=a.source/'skills/implementaudit/scripts/native-worker-capture.py'
        provider_spec=importlib.util.spec_from_file_location('capture_gate_consumer',provider_path)
        provider=importlib.util.module_from_spec(provider_spec);provider_spec.loader.exec_module(provider)
        loaded=provider.route_owner()
        self.assertEqual(pathlib.Path(loaded.__file__).resolve(),path.resolve())
        # Source mutation must still fail before loading or executing a provider.
        bad=self.root/'tampered';bad.mkdir();(bad/'route-transaction.py').write_bytes(path.read_bytes()+b'\n')
        provider.ROOT=bad
        with self.assertRaisesRegex(ValueError,'composition changed'):provider.route_owner()
    def test_parent_capture_provider_transitive_binding_is_current(self):
        parent_path=a.source/'skills/implementaudit/scripts/child-parent-visibility.py'
        parent_spec=importlib.util.spec_from_file_location('parent_gate_consumer',parent_path)
        parent=importlib.util.module_from_spec(parent_spec);parent_spec.loader.exec_module(parent)
        provider=parent.selected_capture()
        loaded=provider.route_owner()
        self.assertEqual(pathlib.Path(loaded.__file__).resolve(),path.resolve())
    def test_writer_still_creates_and_reuses_one_byte_gate(self):
        with route.namespace_gate(str(self.common)):pass
        g=self.common/'implementaudit-locks/route-obligations.gate';self.assertEqual(g.read_bytes(),b'\0');before=snapshot(self.root)
        with route.namespace_gate(str(self.common)):pass
        self.assertEqual(snapshot(self.root),before)
    def test_reader_missing_common_is_typed_and_nonmutating(self):
        missing=self.root/'absent';before=snapshot(self.root)
        with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):
            with route.namespace_gate(str(missing),create=False):self.fail('absent guard yielded')
        self.assertEqual(snapshot(self.root),before)
    def test_observe_current_deletion_after_open_is_typed_and_nonmutating(self):
        with route.namespace_gate(str(self.common)):pass
        gate=self.common/'implementaudit-locks/route-obligations.gate';before=snapshot(self.root)
        original_open=route.os.open;triggered={'value':False}
        def open_then_delete(path,*args,**kwargs):
            descriptor=original_open(path,*args,**kwargs)
            if pathlib.Path(path)==gate and not triggered['value']:
                triggered['value']=True;gate.unlink()
            return descriptor
        stdout=io.StringIO();stderr=io.StringIO()
        try:
            with patch.object(route.os,'open',side_effect=open_then_delete),patch.object(route,'repo_context',return_value=(self.root,'',str(self.common))),patch.object(route,'current_ref',return_value=(None,None)),contextlib.redirect_stdout(stdout),contextlib.redirect_stderr(stderr),self.assertRaises(SystemExit):
                route.command_observe_current(argparse.Namespace(controller='inert-test'))
        finally:
            gate.write_bytes(b'\0');gate.chmod(0o600)
        payload=json.loads(stdout.getvalue().strip().splitlines()[-1])
        self.assertTrue(triggered['value'])
        self.assertEqual(payload['schema'],route.RESULT_SCHEMA)
        self.assertEqual(payload['status'],'UNAVAILABLE')
        self.assertFalse(payload['advance_allowed'])
        self.assertIn('FileNotFoundError',payload['error'])
        self.assertEqual(snapshot(self.root),before)
    def test_reader_serialises_with_existing_writer_lock(self):
        with route.namespace_gate(str(self.common)):pass
        gate=self.common/'implementaudit-locks/route-obligations.gate'
        probe = r'''import errno, os, sys
path = sys.argv[1]
fd = os.open(path, os.O_RDWR | getattr(os, 'O_BINARY', 0))
try:
    os.lseek(fd, 0, os.SEEK_SET)
    if os.name == 'nt':
        import msvcrt
        try:
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
        except OSError as exc:
            if exc.errno not in {errno.EACCES, errno.EAGAIN, errno.EDEADLK}:
                raise
            raise SystemExit(0)
        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
        raise SystemExit(1)
    import fcntl
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise SystemExit(0)
    fcntl.flock(fd, fcntl.LOCK_UN)
    raise SystemExit(1)
finally:
    os.close(fd)
'''
        with route.namespace_gate(str(self.common)):
            result=subprocess.run([sys.executable,'-I','-B','-c',probe,str(gate)],capture_output=True,text=True,timeout=5)
            self.assertEqual(result.returncode,0,result.stderr or result.stdout)
    def refuse_gate(self,kind):
        d=self.common/'implementaudit-locks';d.mkdir();g=d/'route-obligations.gate'
        if kind=='symlink':
            target=self.root/'target';target.write_bytes(b'\0')
            try:g.symlink_to(target)
            except OSError as exc:
                if os.name=='nt' and getattr(exc,'winerror',None)==1314:self.skipTest('symlink fixture requires SeCreateSymbolicLinkPrivilege')
                raise
        elif kind=='hardlink':target=self.root/'target';target.write_bytes(b'\0');os.link(target,g)
        elif kind=='directory':g.mkdir()
        else:g.write_bytes(b'' if kind=='empty' else b'xx')
        before=snapshot(self.root)
        with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):
            with route.namespace_gate(str(self.common),create=False):self.fail('unsafe guard yielded')
        self.assertEqual(snapshot(self.root),before)
    def test_reader_refuses_symlink(self):self.refuse_gate('symlink')
    def test_reader_refuses_hardlink(self):self.refuse_gate('hardlink')
    def test_reader_refuses_empty_gate(self):self.refuse_gate('empty')
    def test_reader_refuses_oversized_gate(self):self.refuse_gate('oversize')
    def test_reader_refuses_directory_gate(self):self.refuse_gate('directory')
    def test_reader_refuses_aliased_namespace_directory(self):
        d=self.root/'elsewhere';d.mkdir();(d/'route-obligations.gate').write_bytes(b'\0')
        try:(self.common/'implementaudit-locks').symlink_to(d,target_is_directory=True)
        except OSError as exc:
            if os.name=='nt' and getattr(exc,'winerror',None)==1314:self.skipTest('reparse fixture requires SeCreateSymbolicLinkPrivilege')
            raise
        before=snapshot(self.root)
        with contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):
            with route.namespace_gate(str(self.common),create=False):self.fail('aliased directory yielded')
        self.assertEqual(snapshot(self.root),before)
    def test_reader_rejects_regular_namespace_replacement(self):
        with route.namespace_gate(str(self.common)):pass
        directory=self.common/'implementaudit-locks';backup=self.common/'implementaudit-locks-owned';triggered={'value':False};original_lstat=route.os.lstat
        def lstat_then_replace(path,*args,**kwargs):
            info=original_lstat(path,*args,**kwargs)
            if pathlib.Path(path)==directory and not triggered['value']:
                triggered['value']=True;directory.rename(backup);directory.mkdir();(directory/'route-obligations.gate').write_bytes(b'\0')
            return info
        before=snapshot(self.root)
        with patch.object(route.os,'lstat',side_effect=lstat_then_replace),contextlib.redirect_stdout(io.StringIO()),contextlib.redirect_stderr(io.StringIO()),self.assertRaises(SystemExit):
            with route.namespace_gate(str(self.common),create=False):self.fail('replaced namespace yielded')
        shutil.rmtree(directory);backup.rename(directory)
        self.assertTrue(triggered['value']);self.assertEqual(snapshot(self.root),before)
if __name__=='__main__':unittest.main(verbosity=2)
