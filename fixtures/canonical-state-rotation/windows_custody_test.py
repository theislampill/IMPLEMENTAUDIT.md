#!/usr/bin/env python3
"""Real Windows filesystem discriminators; no modeled os.name or native credit."""
from __future__ import annotations

import ctypes
import importlib.util
import os
import random
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.dont_write_bytecode = True
BASE = Path(__file__).resolve().parents[2]
SCRIPTS = BASE / "skills/implementaudit/scripts"


def load(name):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), SCRIPTS / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@unittest.skipUnless(os.name == "nt", "requires actual Windows handles and filesystem")
class WindowsCustody(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="r0039-windows-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.claim = load("claim-run-rotation")
        self.rotate = load("rotate-canonical-state")
        self.reader = load("read-canonical-pair")

    def test_all_three_owners_accept_real_directory(self):
        with self.claim.DirectoryPin(self.root) as pin:
            pin.verify()
        self.rotate.require_safe_directory_chain(self.root, self.root)
        path, handle = self.reader.directory(self.root)
        try:
            self.assertEqual(path, self.root)
        finally:
            if os.name == "nt":
                handle.close()
            else:
                os.close(handle)

    def test_retained_binary_file_and_hardlink_refusal(self):
        path = self.root / "input.bin"
        raw = b"a\r\n\x00\x1a\xffz"
        path.write_bytes(raw)
        with self.claim.PinnedFile(path) as pinned:
            self.assertEqual(pinned.read(), raw)
            with self.assertRaises(OSError):
                path.write_bytes(b"mutation")
        os.link(path, self.root / "alias.bin")
        with self.assertRaises((OSError, self.claim.RotationError)):
            self.claim.read_regular(path)

    def test_projection_output_is_exclusive_readonly_and_exact(self):
        path = self.root / "projection.bin"
        raw = b"exact\r\n\x1a\x00\xff"
        self.rotate.write_new_regular(path, raw, 0o444, custody_root=self.root)
        self.addCleanup(path.chmod, 0o666)
        data, info = self.rotate.read_regular(path, self.root, "projection", require_owner_write=False)
        self.assertEqual(data, raw)
        self.assertEqual(stat.S_IMODE(info.st_mode), 0o444)
        with self.assertRaises((OSError, self.rotate.RotationError)):
            self.rotate.write_new_regular(path, b"overwrite", 0o444, custody_root=self.root)
        self.assertEqual(path.read_bytes(), raw)

    def test_junction_ancestor_is_never_followed(self):
        target = self.root / "target"
        target.mkdir()
        alias = self.root / "junction"
        result = subprocess.run([os.environ.get("COMSPEC", r"C:\Windows\System32\cmd.exe"),
                                 "/d", "/c", "mklink", "/J", str(alias), str(target)],
                                capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors="replace"))
        self.addCleanup(alias.rmdir)
        for action in (lambda: self.claim.DirectoryPin(alias),
                       lambda: self.rotate.require_safe_directory_chain(alias, self.root),
                       lambda: self.reader.directory(alias)):
            with self.assertRaises((OSError, ValueError, RuntimeError)):
                action()

    def test_lock_is_exclusive_and_released(self):
        path = self.root / "lock.gate"
        with self.claim.native_lock(path, blocking=False):
            with self.assertRaises((OSError, self.claim.RotationError)):
                with self.claim.native_lock(path, blocking=False):
                    self.fail("second owner acquired the held lock")
        with self.claim.native_lock(path, blocking=False):
            pass

    def test_native_memory_observation(self):
        self.rotate._check_memory_budget()

    def test_retained_directory_name_cannot_be_replaced_before_release(self):
        path = self.root / 'held-ancestor'
        path.mkdir()
        renamed = self.root / 'replacement'
        with self.claim.DirectoryPin(path) as held:
            with self.assertRaises(OSError):
                path.rename(renamed)
            held.verify()
        path.rename(renamed)
        self.assertTrue(renamed.is_dir())

    def test_actual_short_directory_alias_is_refused(self):
        k = ctypes.WinDLL('kernel32', use_last_error=True)
        k.GetShortPathNameW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p, ctypes.c_ulong]
        k.GetShortPathNameW.restype = ctypes.c_ulong
        buffer = ctypes.create_unicode_buffer(32768)
        count = k.GetShortPathNameW(str(self.root), buffer, len(buffer))
        self.assertGreater(count, 0)
        if Path(buffer.value) == self.root:
            self.skipTest('this volume did not provide a distinct 8.3 alias')
        with self.assertRaises((OSError, self.claim.CustodyError)):
            self.claim.DirectoryPin(buffer.value)

    def test_native_preparation_reuse_enumerates_handles_before_owner_check(self):
        generation = self.root / 'state-generations/G0002'
        draft = generation / 'draft'
        draft.mkdir(parents=True)
        for name in ('STATE.md', 'ROADMAP.md', 'protected-state.json', 'draft-manifest.json'):
            (draft / name).write_bytes(b'constructed input')
        (generation / 'native-resume-owner-map.json').write_bytes(b'wrong owner map')
        with self.assertRaisesRegex(self.rotate.RotationError, 'derived owner map drift'):
            self.rotate._read_native_preparation(self.root, self.root, 'test', 'G0002', {}, {}, b'expected map', 'a' * 40)

    def test_snapshot_roundtrip_and_alias_refusal(self):
        files = {'STATE.md': b'exact\r\n\x00\x1a', 'native-records/sub/item.txt': b'paired evidence'}
        _, directory = self.reader.directory(self.root)
        try:
            self.reader.write_snapshot(directory, files)
            self.assertEqual(self.reader.snapshot_files(directory), files)
            with self.assertRaises((OSError, ValueError)):
                self.reader.write_snapshot(directory, {'../outside': b'refuse'})
        finally:
            directory.close()


class GitObjectCustody(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='r0039-object-')
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.claim = load('claim-run-rotation')
        self.custody = load('canonical_custody')
        self.exe, self.env = self.claim.fixed_git(), self.claim.git_environment()
        self.git('init', '-q')

    def git(self, *args, data=None):
        result = subprocess.run([self.exe, '-C', str(self.repo), *args], input=data,
                                capture_output=True, env=self.env, check=False)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors='replace'))
        return result.stdout

    def test_exact_blob_reads_and_process_cleanup(self):
        raw = b'actual binary object\r\n\x00\x1a\xff'
        oid = self.git('hash-object', '-w', '--stdin', data=raw).decode().strip()
        processes = []
        original = self.custody.subprocess.Popen
        def observe_process(*args, **kwargs):
            process = original(*args, **kwargs)
            processes.append(process)
            return process
        with mock.patch.object(self.custody.subprocess, 'Popen', side_effect=observe_process):
            with self.custody.git_scope(self.repo, self.exe, self.env):
                for _ in range(3):
                    self.assertEqual(self.custody.read_object(self.repo, oid, 4096), raw)
                    self.assertTrue(all(p.poll() is not None for p in processes), 'Git cache survived a completed lookup')
        self.assertTrue(processes)
        self.assertTrue(all(p.poll() is not None for p in processes))

    def test_wrong_type_and_size_are_refused(self):
        oid = self.git('hash-object', '-w', '--stdin', data=b'bounded').decode().strip()
        tree = self.git('mktree', data=b'').decode().strip()
        for target, limit in ((oid, 2), (tree, 4096)):
            with self.subTest(target=target), self.custody.git_scope(self.repo, self.exe, self.env):
                with self.assertRaises((OSError, ValueError)):
                    self.custody.read_object(self.repo, target, limit)

    def test_changed_physical_object_cannot_be_served_from_a_value_cache(self):
        oid = self.git('hash-object', '-w', '--stdin', data=b'first value').decode().strip()
        path = self.repo / '.git/objects' / oid[:2] / oid[2:]
        with self.custody.git_scope(self.repo, self.exe, self.env):
            self.assertEqual(self.custody.read_object(self.repo, oid, 4096), b'first value')
            path.chmod(0o600)
            path.write_bytes(b'corrupt physical object')
            with self.assertRaises((OSError, ValueError)):
                self.custody.read_object(self.repo, oid, 4096)

    def test_packed_delta_base_is_not_served_after_physical_corruption(self):
        base = bytearray(random.Random(719).randbytes(50000))
        objects = []
        for index in range(4):
            raw = base.copy()
            raw[1000 + index * 100:1010 + index * 100] = bytes([65 + index]) * 10
            objects.append(self.git('hash-object', '-w', '--stdin', data=raw).decode().strip())
        reader = self.repo / 'packed-reader'
        reader.mkdir()
        initialized = subprocess.run([self.exe, '-C', str(reader), 'init', '-q'], env=self.env, capture_output=True)
        self.assertEqual(initialized.returncode, 0)
        prefix = reader / '.git/objects/pack/pack'
        pack_id = self.git('pack-objects', '--delta-base-offset', '--window=10', '--depth=10', str(prefix),
                           data=('\n'.join(objects) + '\n').encode()).decode().strip()
        pack = prefix.with_name('pack-' + pack_id + '.pack')
        layout = self.git('verify-pack', '-v', str(pack.with_suffix('.idx'))).decode().splitlines()
        entries = {parts[0]: parts for line in layout if len(parts := line.split()) >= 5 and parts[0] in objects}
        delta = next(parts for parts in entries.values() if len(parts) == 7)
        base_oid = delta[6]
        pack.chmod(0o600)
        with self.custody.git_scope(reader, self.exe, self.env):
            self.custody.read_object(reader, delta[0], 100000)
            self.custody.read_object(reader, base_oid, 100000)
            offset = int(entries[base_oid][4]) + 12
            self.assertLess(offset, pack.stat().st_size - 20)
            with pack.open('r+b') as stream:
                stream.seek(offset)
                value = stream.read(1)
                stream.seek(offset)
                stream.write(bytes([value[0] ^ 0xff]))
                stream.flush()
                os.fsync(stream.fileno())
            fresh = subprocess.run([self.exe, '-C', str(reader), 'cat-file', 'blob', base_oid],
                                   env=self.env, capture_output=True)
            self.assertNotEqual(fresh.returncode, 0, 'corruption discriminator did not reach the actual base object')
            with self.assertRaises((OSError, ValueError)):
                self.custody.read_object(reader, base_oid, 100000)

    @unittest.skipUnless(os.name == 'nt', 'Windows files-backend custody control')
    def test_live_loose_packed_and_symbolic_ref_discrimination(self):
        first = self.git('hash-object', '-w', '--stdin', data=b'first').decode().strip()
        second = self.git('hash-object', '-w', '--stdin', data=b'second').decode().strip()
        ref = 'refs/implementaudit/current-generations/test'
        with self.custody.git_scope(self.repo, self.exe, self.env):
            self.assertIsNone(self.custody.current_ref(self.repo, ref))
            self.git('update-ref', ref, first, '0' * 40)
            self.assertEqual(self.custody.current_ref(self.repo, ref), first)
            self.git('pack-refs', '--all', '--prune')
            self.assertEqual(self.custody.current_ref(self.repo, ref), first)
            self.git('update-ref', ref, second, first)
            self.assertEqual(self.custody.current_ref(self.repo, ref), second)
            self.git('symbolic-ref', ref, 'refs/implementaudit/current-generations/other')
            with self.assertRaises((OSError, ValueError)):
                self.custody.current_ref(self.repo, ref)

    @unittest.skipUnless(os.name == 'nt', 'Windows files-backend corruption control')
    def test_dangling_refs_and_noncanonical_packed_grammar_refuse(self):
        oid = self.git('hash-object', '-w', '--stdin', data=b'exact retained value').decode().strip()
        ref = 'refs/implementaudit/current-generations/test'
        path = self.repo / '.git' / ref
        path.parent.mkdir(parents=True)
        path.write_bytes(b'f' * 40 + b'\n')
        with self.custody.git_scope(self.repo, self.exe, self.env):
            with self.assertRaises((OSError, ValueError)):
                self.custody.current_ref(self.repo, ref)
        path.unlink()
        for raw in (b'^' + oid.encode() + b'\n' + oid.encode() + b' ' + ref.encode() + b'\n',
                    oid.encode() + b' ' + ref.encode() + b'\r\n'):
            (self.repo / '.git/packed-refs').write_bytes(raw)
            with self.subTest(raw=raw), self.custody.git_scope(self.repo, self.exe, self.env):
                with self.assertRaises((OSError, ValueError)):
                    self.custody.current_ref(self.repo, ref)


if __name__ == "__main__":
    unittest.main()
