"""Source/data/disposable-file controls only; never runs hosted/original work."""
import hashlib
import importlib.util
import json
import os
import shutil
import types
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
def module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result

class SuccessorTests(unittest.TestCase):
    def loader(self):
        return module(ROOT/'scripts/load-work-graph-c5-executor.py', 'successor_loader')

    def nss(self):
        path=ROOT/'scripts/hosted-files-only-nss.py'
        self.assertTrue(path.is_file(), 'scoped NSS custody owner is absent')
        return module(path, 'successor_nss')

    def test_finite_source_selection_and_setup_admission(self):
        loader=self.loader()
        self.assertTrue(hasattr(loader, 'G132_HOST_PROFILE_SOURCE_REVISION'), 'finite successor selection is absent')
        current=loader._Engine(loader.R5_HOSTED_PROFILE, source_revision=loader.G132_HOST_PROFILE_SOURCE_REVISION).load()
        setup=module(ROOT/'scripts/qualify-work-graph-c5-setup.py','successor_setup')
        admitted=setup.hosted_current_owner(ROOT)
        self.assertEqual(current.SOURCES, admitted.SOURCES)
        self.assertEqual(current.D.SPEC['startup_pins']['/etc/ld.so.cache']['sha256'], '347fdaed89f5b040c24b9d44f4b0700e8de4ef0585eb7e3d1ec6d3bdf664cd84')
        old=loader._selection(loader.R5_HOSTED_PROFILE, loader.R5_GIT_08CA_SOURCE_REVISION)
        self.assertEqual(old[1], 'fixtures/work-graph-c5-inputs/execution-r5-hosted-ubuntu24-python312.json')
        self.assertNotEqual(old[1], loader.G132_HOST_PROFILE_BASE_SELECTION)
        with self.assertRaises(ValueError): loader._selection('foreign',loader.G132_HOST_PROFILE_SOURCE_REVISION)

    def test_only_four_observed_native_pin_values_change(self):
        loader=self.loader()
        self.assertTrue(hasattr(loader,'G132_HOST_PROFILE_BASE_SELECTION'),'finite successor fixtures are absent')
        pairs=[(loader.R5_HOSTED_BASE_SELECTION,loader.G132_HOST_PROFILE_BASE_SELECTION),
               (loader.R5_HOSTED_PROVIDER_SELECTION,loader.G132_HOST_PROFILE_PROVIDER_SELECTION)]
        expected={'/etc/ld.so.cache':(38396,'347fdaed89f5b040c24b9d44f4b0700e8de4ef0585eb7e3d1ec6d3bdf664cd84'),
          '/lib/x86_64-linux-gnu/libc.so.6':(2129424,'755a371e86cc9f564ab54f66140747700fb0a103f698f659f2060f707897e09a'),
          '/lib64/ld-linux-x86-64.so.2':(236616,'5fc0940888e9d2e1a00e66d6b1a559c36364ee867683652e1074fa576952cc3f'),
          '/lib/x86_64-linux-gnu/libpthread.so.0':(14408,'cd34f895c9d2aa669d5d2654bed6b71210fc9003c3a1e96bb5311a40feb86039')}
        changed=set()
        for oldpath,newpath in pairs:
            old=json.loads((ROOT/oldpath).read_bytes());new=json.loads((ROOT/newpath).read_bytes())
            for key in ('runtime_pins','startup_pins','native_pins'):
                for path,row in new.get(key,{}).items():
                    if row!=old[key][path]:
                        changed.add(path); self.assertIn(path,expected)
                        self.assertEqual((row['bytes'],row['sha256']),expected[path])
                        restored=dict(row,bytes=old[key][path]['bytes'],sha256=old[key][path]['sha256'])
                        self.assertEqual(restored,old[key][path])
                        new[key][path]=old[key][path]
            new.pop('host_profile_successor',None)
            self.assertEqual(old,new,'unobserved fixture requirement changed')
        self.assertEqual(changed,set(expected))

    def test_transform_preserves_unrelated_bytes_and_refuses_unknown_layouts(self):
        nss=self.nss(); raw=b'# config\npasswd:  files systemd  # retained\ngroup: files systemd\n'
        self.assertEqual(nss.files_only_bytes(raw), b'# config\npasswd:  files  # retained\ngroup: files systemd\n')
        self.assertEqual(nss.files_only_bytes(b'passwd: files\n'),b'passwd: files\n')
        for bad in [b'passwd: compat\n',b'passwd: files [SUCCESS=return] systemd\n',b'passwd: files\npasswd: files\n',b'group: files\n',b'passwd: files\x00\n']:
            with self.subTest(raw=bad),self.assertRaises(ValueError): nss.files_only_bytes(bad)

    def fixture(self,parent):
        etc=Path(parent)/'etc';etc.mkdir(mode=0o700)
        file=etc/'nsswitch.conf';file.write_bytes(b'passwd: files systemd\ngroup: files\n');file.chmod(0o644)
        return etc,file,Path(parent)/'receipt.json'

    def test_owned_callback_failure_restores_original_inode_bytes_mode_mtime(self):
        nss=self.nss()
        with tempfile.TemporaryDirectory() as td:
            etc,path,receipt=self.fixture(td);raw=path.read_bytes();before=path.stat();fds=set(os.listdir('/proc/self/fd'))
            with self.assertRaisesRegex(RuntimeError,'owned failure'):
                with nss.FilesOnlyNSSLease(etc,receipt,expected_uid=os.getuid(),expected_gid=os.getgid()):
                    self.assertEqual(path.read_bytes(),b'passwd: files\ngroup: files\n')
                    raise RuntimeError('owned failure')
            after=path.stat();self.assertEqual(path.read_bytes(),raw)
            self.assertEqual((before.st_dev,before.st_ino,before.st_mode,before.st_mtime_ns),(after.st_dev,after.st_ino,after.st_mode,after.st_mtime_ns))
            self.assertEqual(set(os.listdir('/proc/self/fd')),fds)
            record=json.loads(receipt.read_bytes())
            self.assertEqual(sorted(p.name for p in etc.iterdir()),sorted(['nsswitch.conf',record['backup_name']]))
            self.assertEqual(record['state'],'RESTORED_REPLACEMENT_RETAINED')
            self.assertFalse(record['cleanup_complete'])
            self.assertFalse(record['backup_removed'])
            self.assertEqual((etc/record['backup_name']).read_bytes(),b'passwd: files\ngroup: files\n')

    def test_symlink_and_hardlink_refuse_before_effect(self):
        nss=self.nss()
        for kind in ('symlink','hardlink'):
            with self.subTest(kind=kind),tempfile.TemporaryDirectory() as td:
                etc,path,receipt=self.fixture(td);original=path.read_bytes()
                if kind=='symlink':
                    path.rename(etc/'real');path.symlink_to('real')
                else: os.link(path,etc/'alias')
                with self.assertRaises((ValueError,OSError)):
                    with nss.FilesOnlyNSSLease(etc,receipt,expected_uid=os.getuid(),expected_gid=os.getgid()):self.fail('alias admitted')
                self.assertEqual(path.read_bytes(),original)

    def test_foreign_active_drift_is_not_overwritten(self):
        nss=self.nss()
        with tempfile.TemporaryDirectory() as td:
            etc,path,receipt=self.fixture(td)
            with self.assertRaises(ValueError):
                with nss.FilesOnlyNSSLease(etc,receipt,expected_uid=os.getuid(),expected_gid=os.getgid()):
                    path.write_bytes(b'passwd: foreign\n')
            self.assertEqual(path.read_bytes(),b'passwd: foreign\n')
            record=json.loads(receipt.read_bytes());self.assertEqual(record['state'],'RESTORATION_REFUSED_RETAIN_FOR_VM_DISPOSAL')
            self.assertTrue((etc/record['backup_name']).exists())

    def test_partial_replacement_failure_retains_owned_partial_before_effect(self):
        nss=self.nss()
        with tempfile.TemporaryDirectory() as td:
            etc,path,receipt=self.fixture(td);raw=path.read_bytes();real=os.pwrite;calls=0
            def partial(fd,data,offset):
                nonlocal calls
                if os.readlink('/proc/self/fd/'+str(fd)).startswith(str(etc)+ '/.implementaudit-g132-nss-'):
                    calls+=1
                    if calls==1:return real(fd,data[:2],offset)
                    raise OSError('injected owned write failure')
                return real(fd,data,offset)
            with patch.object(nss.os,'pwrite',partial),self.assertRaisesRegex(OSError,'injected owned write failure'):
                with nss.FilesOnlyNSSLease(etc,receipt,expected_uid=os.getuid(),expected_gid=os.getgid()):self.fail('partial admitted')
            self.assertEqual(path.read_bytes(),raw)
            record=json.loads(receipt.read_bytes())
            self.assertEqual(sorted(x.name for x in etc.iterdir()),sorted(['nsswitch.conf',record['backup_name']]))
            self.assertEqual((etc/record['backup_name']).read_bytes(),b'pa')
            self.assertTrue(record['restoration_verified'])
            self.assertFalse(record['cleanup_complete'])
            self.assertFalse(record['backup_removed'])

    def test_unsupported_actual_file_refuses_without_files_only_claim(self):
        nss=self.nss()
        with tempfile.TemporaryDirectory() as td:
            etc,path,receipt=self.fixture(td);path.write_bytes(b'passwd: compat\n')
            with self.assertRaises(ValueError):
                with nss.FilesOnlyNSSLease(etc,receipt,expected_uid=os.getuid(),expected_gid=os.getgid()):self.fail('unsupported admitted')
            self.assertEqual(path.read_bytes(),b'passwd: compat\n')
            self.assertEqual(json.loads(receipt.read_bytes())['state'],'REFUSED_INPUT_UNCHANGED')

    def test_finite_pin_drift_and_wrong_origin_refuse_real_loader(self):
        loader=self.loader()
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            for logical in (loader.LOADER,*loader.G132_HOST_PROFILE_PINS):
                physical=loader.R5_GIT_08CA_EXECUTOR_MEMBER if logical==loader.EXECUTOR else logical
                dst=root/physical;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(ROOT/physical,dst)
            loader.ROOT=root
            target=root/loader.G132_HOST_PROFILE_BASE_SELECTION;original=target.read_bytes();target.write_bytes(original+b' ')
            with self.assertRaisesRegex(ValueError,'Unsupported fixed C5 execution member'):
                loader._Engine(loader.R5_HOSTED_PROFILE,source_revision=loader.G132_HOST_PROFILE_SOURCE_REVISION)
            target.write_bytes(original)
            target=root/loader.G132_HOST_PROFILE_EXECUTION_SELECTION;obj=json.loads(target.read_bytes());obj['selection_origins']['provider_actual_member']=loader.R5_HOSTED_PROVIDER_SELECTION
            target.write_text(json.dumps(obj));pins=dict(loader.G132_HOST_PROFILE_PINS);pins[loader.G132_HOST_PROFILE_EXECUTION_SELECTION]=hashlib.sha256(target.read_bytes()).hexdigest();loader.G132_HOST_PROFILE_PINS=types.MappingProxyType(pins)
            with self.assertRaisesRegex(ValueError,'Unsupported fixed C5 execution selection'):
                loader._Engine(loader.R5_HOSTED_PROFILE,source_revision=loader.G132_HOST_PROFILE_SOURCE_REVISION).load()

    def test_actual_files_only_noop_and_production_nonhost_refusal(self):
        nss=self.nss()
        with tempfile.TemporaryDirectory() as td:
            etc,path,receipt=self.fixture(td);path.write_bytes(b'passwd: files\n');before=path.stat()
            with nss.FilesOnlyNSSLease(etc,receipt,expected_uid=os.getuid(),expected_gid=os.getgid()):pass
            self.assertEqual(path.stat(),before)
            record=json.loads(receipt.read_bytes())
            self.assertEqual(record['state'],'UNCHANGED_FILES_ONLY_CLOSED')
            self.assertTrue(record['cleanup_complete'])
            self.assertEqual(record['replacement_cleanup'],{'disposition':'NONE_ALLOCATED'})
            with patch.dict(os.environ,{},clear=True),self.assertRaises(ValueError):nss.hosted_files_only_nss(Path(td)/'not-created.json')
            self.assertFalse((Path(td)/'not-created.json').exists())

    def test_namespace_join_requires_same_boot_and_actual_success(self):
        path=ROOT/'test-support/g132-host-profile-successor/ordinary_qualifier.py'
        self.assertTrue(path.is_file(),'inert ordinary qualifier source is absent')
        driver=module(path,'successor_driver')
        context={'boot_id':'test-only-boot','run_id':'test-only-run'}
        ns={'schema':'dg16.ordinary-setup-capability.v1','authority':'NONE','original19_started':False,'provider_acquired':False,'native_admission':False,
            'classification':'SETUP_REACHED_ABSENT_TARGET','complete_custody':True,'descriptor_restoration':True,'owned_group_absent':True,
            'launcher':dict(driver.LAUNCHER_PIN,current=True),'timed_out':False,'overflow':False,'eof':{'stdout':True,'stderr':True},'exit_code':1}
        row=dict(schema='g132.host-profile-namespace.v1',authority='NONE',source_commit='a'*40,source_tree='b'*40,context=context,setup_pin=driver.SETUP_PIN,namespace_return_code=0,namespace=ns)
        self.assertTrue(driver.namespace_join(row,context,'a'*40,'b'*40))
        for change in [{'context':dict(context,boot_id='foreign')},{'source_commit':'c'*40},{'namespace_return_code':2},{'namespace':dict(ns,classification='PROC_MOUNT_EPERM')}]:
            with self.subTest(change=change),self.assertRaises(ValueError):driver.namespace_join(dict(row,**change),context,'a'*40,'b'*40)

    def name_interleaving(self, lease, *, partial):
        real = lease._named
        injected = []
        def named(name, fd):
            result = real(name, fd)
            ready = (not lease.entered and os.fstat(fd).st_size == 2) if partial else lease.entered
            if (result and name == lease.backup_name and fd == lease.replacement and ready
                    and not injected and real('nsswitch.conf', lease.original)):
                # Real filesystem substitution after the successful observation;
                # the caller receives that now-stale True value.
                os.rename(name, name+'.owned-retained', src_dir_fd=lease.parent, dst_dir_fd=lease.parent)
                foreign = os.open(name, os.O_CREAT|os.O_EXCL|os.O_WRONLY, 0o644, dir_fd=lease.parent)
                try: os.write(foreign, b'foreign concurrently named file\n')
                finally: os.close(foreign)
                injected.append(True)
            return result
        lease._named = named
        return injected

    def test_post_restore_name_race_never_deletes_foreign_or_claims_cleanup(self):
        nss = self.nss()
        with tempfile.TemporaryDirectory() as td:
            etc,path,receipt = self.fixture(td); raw = path.read_bytes()
            lease = nss.FilesOnlyNSSLease(etc,receipt,expected_uid=os.getuid(),expected_gid=os.getgid())
            injected = self.name_interleaving(lease,partial=False)
            try:
                with lease: pass
            except ValueError: pass
            self.assertEqual(injected,[True], 'control did not reach the closing name boundary')
            self.assertEqual(path.read_bytes(),raw)
            foreign = etc/lease.backup_name
            self.assertTrue(foreign.exists(), 'foreign file was deleted through a stale name observation')
            self.assertEqual(foreign.read_bytes(),b'foreign concurrently named file\n')
            self.assertTrue((etc/(lease.backup_name+'.owned-retained')).exists())
            record=json.loads(receipt.read_bytes())
            self.assertIs(record.get('cleanup_complete'),False)
            self.assertIs(record.get('backup_removed'),False)

    def test_partial_write_name_race_never_deletes_foreign_or_claims_cleanup(self):
        nss = self.nss()
        with tempfile.TemporaryDirectory() as td:
            etc,path,receipt=self.fixture(td);raw=path.read_bytes();real=os.pwrite;calls=0
            lease=nss.FilesOnlyNSSLease(etc,receipt,expected_uid=os.getuid(),expected_gid=os.getgid())
            injected=[];pending=[];real_named=lease._named;real_fstat=os.fstat
            def named(name,fd):
                result=real_named(name,fd)
                if result and name==lease.backup_name and fd==lease.replacement and real_fstat(fd).st_size==2:
                    pending.append(True)
                return result
            lease._named=named
            def fstat(fd):
                value=real_fstat(fd)
                if fd==lease.replacement and pending and not injected:
                    # The partial branch has an additional final fstat after its
                    # name observation. Substitute after that snapshot instead.
                    name=lease.backup_name
                    os.rename(name,name+'.owned-retained',src_dir_fd=lease.parent,dst_dir_fd=lease.parent)
                    foreign=os.open(name,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o644,dir_fd=lease.parent)
                    try:os.write(foreign,b'foreign concurrently named file\n')
                    finally:os.close(foreign)
                    injected.append(True)
                return value
            def partial(fd,data,offset):
                nonlocal calls
                if fd==lease.replacement:
                    calls+=1
                    if calls==1:return real(fd,data[:2],offset)
                    raise OSError('injected owned write failure')
                return real(fd,data,offset)
            with patch.object(nss.os,'pwrite',partial),patch.object(nss.os,'fstat',fstat),self.assertRaises((OSError,ValueError)):
                with lease:self.fail('partial admitted')
            self.assertEqual(injected,[True], 'control did not reach the partial cleanup name boundary')
            self.assertEqual(path.read_bytes(),raw)
            foreign=etc/lease.backup_name
            self.assertTrue(foreign.exists(), 'foreign partial-cleanup name was deleted')
            self.assertEqual(foreign.read_bytes(),b'foreign concurrently named file\n')
            self.assertTrue((etc/(lease.backup_name+'.owned-retained')).exists())
            record=json.loads(receipt.read_bytes())
            self.assertIs(record.get('cleanup_complete'),False)
            self.assertIs(record.get('backup_removed'),False)

    def test_complete_cleanup_oracle_refuses_retained_residual_and_old_false_success(self):
        driver=module(ROOT/'test-support/g132-host-profile-successor/ordinary_qualifier.py','cleanup_oracle')
        self.assertTrue(hasattr(driver,'nss_cleanup_complete'), 'explicit complete-cleanup oracle absent')
        old=dict(state='RESTORED',restoration_verified=True,backup_removed=True)
        retained=dict(schema='g132.hosted-files-only-nss.v2',state='RESTORED_REPLACEMENT_RETAINED',
                      restoration_verified=True,cleanup_complete=False,backup_removed=False,
                      replacement_deletion_attempted=False)
        closed=dict(schema='g132.hosted-files-only-nss.v2',state='UNCHANGED_FILES_ONLY_CLOSED',
                    restoration_verified=True,cleanup_complete=True,backup_removed=False,
                    replacement_deletion_attempted=False,replacement_cleanup=dict(disposition='NONE_ALLOCATED'))
        self.assertFalse(driver.nss_cleanup_complete(old))
        self.assertFalse(driver.nss_cleanup_complete(retained))
        self.assertTrue(driver.nss_cleanup_complete(closed))

if __name__=='__main__': unittest.main(verbosity=2)
