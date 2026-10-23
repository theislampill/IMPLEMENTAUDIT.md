"""Actual Windows reader controls in disposable roots; no native admission."""
import importlib.util
import os
from pathlib import Path
import subprocess
import struct
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

ROOT = Path(sys.argv.pop(1)).resolve()
spec = importlib.util.spec_from_file_location("oe_windows_reader", ROOT / "scripts/operational-evidence.py")
oe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oe)


@unittest.skipUnless(os.name == "nt", "actual Windows handles required")
class WindowsReaderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="r0038-windows-reader-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.file = self.root / "ordinary.txt"
        self.file.write_bytes(b"bounded bytes\n")

    def test_regular_and_unicode_bytes(self):
        for name in ("ordinary.txt", "\u0645\u0644\u0641.txt"):
            path = self.root / name
            path.write_bytes(b"bounded bytes\n")
            self.assertEqual(oe._read_repository_path(path, self.root), (b"bounded bytes\n", "file"))

    def test_size_boundary(self):
        size = self.file.stat().st_size
        self.assertEqual(len(oe._read_repository_path(self.file, self.root, size)[0]), size)
        with self.assertRaises(OSError):
            oe._read_repository_path(self.file, self.root, size - 1)

    def test_directory_refused(self):
        directory = self.root / "directory"
        directory.mkdir()
        with self.assertRaises(OSError):
            oe._read_repository_path(directory, self.root)

    def test_remote_drive_refused_before_file_open(self):
        kernel = types.SimpleNamespace(GetDriveTypeW=lambda anchor: 4)
        with patch.object(oe, "_snapshot_windows_kernel_v1", return_value=kernel):
            with self.assertRaises(OSError):
                oe._read_repository_path(self.file, self.root)

    def test_hardlink_refused(self):
        link = self.root / "hardlink.txt"
        os.link(self.file, link)
        for path in (self.file, link):
            with self.assertRaises(OSError):
                oe._read_repository_path(path, self.root)

    def test_ads_refused(self):
        stream = Path(str(self.file) + ":secret")
        stream.write_bytes(b"must not return")
        with self.assertRaises(OSError):
            oe._read_repository_path(stream, self.root)

    def test_actual_short_names_do_not_bypass_excluded_components(self):
        kernel = oe._snapshot_windows_kernel_v1()
        kernel.GetShortPathNameW.argtypes = [oe.ctypes.c_wchar_p, oe.ctypes.c_wchar_p, oe.ctypes.c_uint32]
        kernel.GetShortPathNameW.restype = oe.ctypes.c_uint32
        leaf = self.root / "credentials.json"
        leaf.write_bytes(b"excluded fixture bytes")
        parent = self.root / "credentials"
        parent.mkdir()
        (parent / "data.txt").write_bytes(b"excluded parent fixture bytes")
        observed = []
        for target in (leaf, parent / "data.txt"):
            buffer = oe.ctypes.create_unicode_buffer(32768)
            length = kernel.GetShortPathNameW(str(target), buffer, len(buffer))
            self.assertGreater(length, 0)
            reported = Path(buffer.value)
            alias = (target.parent / reported.name if target == leaf else
                     parent.parent / reported.parent.name / target.name)
            if str(alias).casefold() == str(target).casefold():
                continue
            self.assertIsNone(oe._repository_path_policy(alias.relative_to(self.root).as_posix()))
            observed.append(str(alias))
            with self.subTest(target=target), self.assertRaises(OSError):
                oe._read_repository_path(alias)
        if not observed:
            self.skipTest("this volume did not assign short aliases to the test-owned excluded components")

    def test_alias_and_device_spellings_refused(self):
        for path in (Path(str(self.file) + "."), Path(str(self.file) + " "),
                     self.root / "NUL", Path("\\\\.\\NUL"),
                     Path("\\\\?\\" + str(self.file))):
            with self.subTest(path=path), self.assertRaises(OSError):
                oe._read_repository_path(path)

    def test_junction_parent_refused(self):
        target = self.root / "outside"
        target.mkdir()
        (target / "data.txt").write_bytes(b"outside")
        link = self.root / "junction"
        result = subprocess.run(["cmd.exe", "/d", "/c", "mklink", "/J", str(link), str(target)],
                                capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        try:
            with self.assertRaises(OSError):
                oe._read_repository_path(link / "data.txt", self.root)
        finally:
            link.rmdir()

    def test_file_write_and_parent_rename_denied_during_read(self):
        original = oe._snapshot_handle_info_v1
        observations = []

        def inspect(kernel, handle):
            info = original(kernel, handle)
            if not info.attributes & 0x10:
                with self.assertRaises(OSError):
                    self.file.write_bytes(b"replacement")
                with self.assertRaises(OSError):
                    self.root.rename(self.root.with_name(self.root.name + "-moved"))
                observations.append(True)
            return info

        with patch.object(oe, "_snapshot_handle_info_v1", side_effect=inspect):
            self.assertEqual(oe._read_repository_path(self.file, self.root)[0], b"bounded bytes\n")
        self.assertGreaterEqual(len(observations), 2)
        self.file.write_bytes(b"handles released")
        self.assertEqual(self.file.read_bytes(), b"handles released")

    def test_actual_no_replace_handle_rename(self):
        kernel = oe._snapshot_windows_kernel_v1()
        stage = self.root / "stage.txt"
        stage.write_bytes(b"source bytes")
        target = self.root / "destination.txt"
        target.write_bytes(b"existing bytes")
        handle = kernel.CreateFileW(str(stage), 0x80000000 | 0x00010000,
                                    1, None, 3, 0x00200000, None)
        self.assertNotEqual(handle, oe.ctypes.c_void_p(-1).value)
        try:
            with self.assertRaises(FileExistsError):
                oe._snapshot_atomic_no_replace_v1(handle, target)
            self.assertEqual(target.read_bytes(), b"existing bytes")
            absent = self.root / "new-destination.txt"
            oe._snapshot_atomic_no_replace_v1(handle, absent)
        finally:
            kernel.CloseHandle(handle)
        self.assertFalse(stage.exists())
        self.assertEqual(absent.read_bytes(), b"source bytes")

    def test_parent_metadata_change_cannot_redirect_acquisition(self):
        # Regression for source-review finding: attribute writes are not fenced
        # by FILE_SHARE_READ. All objects and the alternate target are disposable.
        inside, outside = self.root / "inside", self.root / "outside"
        inside.mkdir()
        outside.mkdir()
        parent = inside / "parent"
        parent.mkdir()
        sentinel = b"outside fixture bytes"
        (outside / "data.txt").write_bytes(sentinel)
        kernel = oe._snapshot_windows_kernel_v1()
        kernel.DeviceIoControl.argtypes = [oe.ctypes.c_void_p, oe.ctypes.c_uint32,
            oe.ctypes.c_void_p, oe.ctypes.c_uint32, oe.ctypes.c_void_p,
            oe.ctypes.c_uint32, oe.ctypes.POINTER(oe.ctypes.c_uint32), oe.ctypes.c_void_p]
        kernel.DeviceIoControl.restype = oe.ctypes.c_int
        original = oe._snapshot_handle_info_v1
        parent_id = parent.stat().st_ino
        changed = []

        def inspect(api, handle):
            info = original(api, handle)
            if not changed and (info.file_index_high << 32) | info.file_index_low == parent_id:
                substitute = ("\\??\\" + str(outside)).encode("utf-16-le")
                printed = str(outside).encode("utf-16-le")
                names = substitute + b"\0\0" + printed + b"\0\0"
                raw = struct.pack("<IHHHHHH", 0xA0000003, 8 + len(names), 0,
                                  0, len(substitute), len(substitute) + 2, len(printed)) + names
                writer = kernel.CreateFileW(str(parent), 0x100, 7, None, 3, 0x02200000, None)
                self.assertNotEqual(writer, oe.ctypes.c_void_p(-1).value)
                try:
                    data = oe.ctypes.create_string_buffer(raw)
                    count = oe.ctypes.c_uint32()
                    self.assertTrue(kernel.DeviceIoControl(writer, 0x900A4, data, len(raw),
                                    None, 0, oe.ctypes.byref(count), None))
                    changed.append(True)
                finally:
                    kernel.CloseHandle(writer)
            return info

        try:
            with patch.object(oe, "_snapshot_handle_info_v1", side_effect=inspect):
                with self.assertRaises(OSError):
                    oe._read_repository_path(parent / "data.txt", inside)
            self.assertEqual(changed, [True])
            self.assertEqual((outside / "data.txt").read_bytes(), sentinel)
        finally:
            if parent.lstat().st_file_attributes & 0x400:
                parent.rmdir()  # This exact test-owned junction only; never its target.

    def test_actual_export_requires_per_object_custody(self):
        kernel = oe._snapshot_windows_kernel_v1()
        handle = kernel.CreateFileW(str(self.file), 0x80000000, 1, None, 3, 0, None)
        self.assertNotEqual(handle, oe.ctypes.c_void_p(-1).value)
        try:
            capable = oe._snapshot_hardlink_publication_capable_v1(kernel, handle)
            flags = oe.ctypes.c_uint32()
            self.assertTrue(kernel.GetVolumeInformationByHandleW(
                handle, None, 0, None, None, oe.ctypes.byref(flags), None, 0))
            if flags.value & 0x00400000:
                self.assertFalse(capable)
        finally:
            kernel.CloseHandle(handle)
        target = self.root / "export.json"
        # An unsealed ordinary file on NTFS remains incapable. The exporter
        # creates its own sealed object and checks that actual object's DACL.
        oe._snapshot_stage_export_v1(b"{}", target)
        self.assertEqual(target.read_bytes(), b"{}")
        self.assertEqual(list(self.root.glob("*.implementaudit-stage")), [])


if __name__ == "__main__":
    unittest.main()
