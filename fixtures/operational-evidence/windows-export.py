"""Actual Windows export custody controls; no native-source admission claim."""
import ctypes
import importlib.util
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(sys.argv.pop(1)).resolve()
spec = importlib.util.spec_from_file_location("oe_windows_export", ROOT / "scripts/operational-evidence.py")
oe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oe)


@unittest.skipUnless(os.name == "nt", "actual Windows handles required")
class WindowsExportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="r0038-export-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.raw = b"exact immutable export\n" * 1024

    def export(self, root=None):
        target = (root or self.root) / "snapshot.json"
        oe._snapshot_stage_export_v1(self.raw, target)
        self.assertEqual(target.read_bytes(), self.raw)
        self.assertEqual(target.stat().st_nlink, 1)
        return target

    def test_unmocked_supported_volume_positive_and_reopen(self):
        target = self.export()
        with self.assertRaises(OSError):
            os.link(target, self.root / "post-close-alias")
        with self.assertRaises(OSError):
            target.write_bytes(b"changed")
        target.unlink()
        self.assertEqual(list(self.root.iterdir()), [])

    def test_existing_and_concurrent_destination_preserved(self):
        for phase in (None, "before-publish"):
            with self.subTest(phase=phase):
                root = self.root / str(phase)
                root.mkdir()
                target = root / "snapshot.json"
                def occupy(observed):
                    if observed == phase:
                        target.write_bytes(b"foreign")
                if phase is None:
                    target.write_bytes(b"foreign")
                with patch.object(oe, "_snapshot_stage_v1", side_effect=occupy):
                    with self.assertRaises(FileExistsError):
                        self.export(root)
                self.assertEqual(target.read_bytes(), b"foreign")
                self.assertEqual(list(root.iterdir()), [target])

    def test_all_original_stage_mutation_edges(self):
        phases = ("stage-created", "write-complete", "fsync-complete",
                  "readback-start", "readback-eof", "before-publish")
        for phase in phases:
            for action in ("write", "append", "unlink", "link"):
                with self.subTest(phase=phase, action=action):
                    root = self.root / (phase + "-" + action)
                    root.mkdir()
                    seen = []
                    def attack(observed):
                        if observed != phase:
                            return
                        seen.append(observed)
                        stage, = root.glob("*.implementaudit-stage")
                        with self.assertRaises(OSError):
                            if action == "write":
                                stage.write_bytes(b"foreign")
                            elif action == "append":
                                with stage.open("ab") as stream:
                                    stream.write(b"foreign")
                            elif action == "unlink":
                                stage.unlink()
                            else:
                                os.link(stage, root / "alias")
                    with patch.object(oe, "_snapshot_stage_v1", side_effect=attack):
                        self.export(root)
                    self.assertEqual(seen, [phase])

    def test_original_native_rename_edges_exclude_links(self):
        original = oe._snapshot_atomic_no_replace_v1
        for after in (False, True):
            with self.subTest(after=after):
                root = self.root / str(after)
                root.mkdir()
                seen = []
                def attack(handle, target):
                    if after:
                        original(handle, target)
                        source = target
                    else:
                        source, = root.glob("*.implementaudit-stage")
                    with self.assertRaises(OSError):
                        os.link(source, root / "alias")
                    seen.append(after)
                    if not after:
                        original(handle, target)
                with patch.object(oe, "_snapshot_atomic_no_replace_v1", side_effect=attack):
                    self.export(root)
                self.assertEqual(seen, [after])

    def test_interruptions_remove_exact_stage(self):
        for phase in ("stage-created", "write-complete", "fsync-complete",
                      "readback-start", "readback-eof", "before-publish"):
            with self.subTest(phase=phase):
                root = self.root / phase
                root.mkdir()
                def interrupt(observed):
                    if observed == phase:
                        raise OSError("injected interruption")
                with patch.object(oe, "_snapshot_stage_v1", side_effect=interrupt):
                    with self.assertRaises(OSError):
                        self.export(root)
                self.assertEqual(list(root.iterdir()), [])

    def test_parent_and_ancestor_rename_excluded(self):
        root = self.root / "ancestor" / "parent"
        root.mkdir(parents=True)
        seen = []
        def attack(phase):
            if phase == "stage-created":
                for parent in (root, root.parent):
                    with self.assertRaises(OSError):
                        parent.rename(parent.with_name(parent.name + "-moved"))
                seen.append(phase)
        with patch.object(oe, "_snapshot_stage_v1", side_effect=attack):
            self.export(root)
        self.assertEqual(seen, ["stage-created"])

    def test_empty_parent_junction_race_cannot_redirect_stage(self):
        parent, peer = self.root / "parent", self.root / "peer"
        parent.mkdir()
        peer.mkdir()
        kernel = oe._snapshot_windows_kernel_v1()
        kernel.DeviceIoControl.argtypes = [ctypes.c_void_p, ctypes.c_uint32,
            ctypes.c_void_p, ctypes.c_uint32, ctypes.c_void_p, ctypes.c_uint32,
            ctypes.POINTER(ctypes.c_uint32), ctypes.c_void_p]
        kernel.DeviceIoControl.restype = ctypes.c_int
        original = oe._windows_open_child_v1
        changed = []
        def substitute(handle, name, directory, **kwargs):
            if kwargs.get("create_security") is not None:
                substitute_name = ("\\??\\" + str(peer)).encode("utf-16-le")
                printed = str(peer).encode("utf-16-le")
                names = substitute_name + b"\0\0" + printed + b"\0\0"
                raw = struct.pack("<IHHHHHH", 0xA0000003, 8 + len(names), 0,
                    0, len(substitute_name), len(substitute_name) + 2, len(printed)) + names
                writer = kernel.CreateFileW(str(parent), 0x100, 7, None, 3, 0x02200000, None)
                self.assertNotEqual(writer, ctypes.c_void_p(-1).value)
                try:
                    data, count = ctypes.create_string_buffer(raw), ctypes.c_uint32()
                    self.assertTrue(kernel.DeviceIoControl(writer, 0x900A4, data,
                        len(raw), None, 0, ctypes.byref(count), None))
                    changed.append(True)
                finally:
                    kernel.CloseHandle(writer)
            return original(handle, name, directory, **kwargs)
        try:
            with patch.object(oe, "_windows_open_child_v1", side_effect=substitute):
                with self.assertRaises(OSError):
                    self.export(parent)
            self.assertEqual(changed, [True])
            self.assertEqual(list(peer.iterdir()), [])
        finally:
            if parent.lstat().st_file_attributes & 0x400:
                parent.rmdir()  # Exact test-owned junction; never traverse its target.

    def test_unsealed_descriptor_and_failed_readback_refuse(self):
        # A failed actual-descriptor readback cannot be replaced by creation intent.
        for value in (False, OSError("descriptor read unavailable")):
            with self.subTest(value=str(value)):
                options = {"side_effect": value} if isinstance(value, Exception) else {"return_value": value}
                with patch.object(oe, "_snapshot_sealed_dacl_v1", **options):
                    with self.assertRaises(OSError):
                        self.export()
                self.assertEqual(list(self.root.iterdir()), [])

    def test_corrupt_stage_is_not_published(self):
        kernel = oe._snapshot_windows_kernel_v1()
        write = kernel.WriteFile
        seen = []
        def corrupt(handle, buffer, size, count, overlapped):
            replacement = ctypes.create_string_buffer(b"X" * size)
            seen.append(size)
            return write(handle, replacement, size, count, overlapped)
        kernel.WriteFile = corrupt
        with patch.object(oe, "_snapshot_windows_kernel_v1", return_value=kernel):
            with self.assertRaisesRegex(OSError, "exact bytes changed"):
                self.export()
        self.assertTrue(seen)
        self.assertEqual(list(self.root.iterdir()), [])

    def test_actual_process_interruption_preserves_no_publication(self):
        code = """import importlib.util, os, pathlib, sys
spec = importlib.util.spec_from_file_location('export_child', sys.argv[1])
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
def interrupt(phase):
    if phase == sys.argv[3]: os._exit(73)
module._snapshot_stage_v1 = interrupt
module._snapshot_stage_export_v1(b'complete bytes', pathlib.Path(sys.argv[2]))
raise SystemExit('interruption did not execute')
"""
        for phase in ("stage-created", "before-publish"):
            root = self.root / phase
            root.mkdir()
            previous = root / "previous.json"
            previous.write_bytes(b"prior complete")
            target = root / "snapshot.json"
            child = subprocess.run([sys.executable, "-I", "-S", "-B", "-c", code,
                str(ROOT / "scripts/operational-evidence.py"), str(target), phase],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=15,
                creationflags=subprocess.CREATE_NO_WINDOW)
            self.assertEqual(child.returncode, 73, child.stderr)
            self.assertFalse(os.path.lexists(target))
            self.assertEqual(previous.read_bytes(), b"prior complete")
            # A killed process cannot run finally. Observe its exact private
            # residue before removing that one test-owned regular stage.
            stage, = root.glob("*.implementaudit-stage")
            self.assertEqual(stage.stat().st_nlink, 1)
            self.assertFalse(stage.lstat().st_file_attributes & 0x400)
            stage.unlink()
            self.assertFalse(os.path.lexists(stage))
            self.assertEqual(list(root.iterdir()), [previous])

    def test_zero_access_native_link_and_owner_rewrite_denied(self):
        target = self.export()
        kernel = oe._snapshot_windows_kernel_v1()
        native = ctypes.WinDLL("ntdll")
        native.NtSetInformationFile.argtypes = [ctypes.c_void_p, ctypes.c_void_p,
            ctypes.c_void_p, ctypes.c_uint32, ctypes.c_int]
        native.NtSetInformationFile.restype = ctypes.c_long
        for rights in (0x100, 0x40000, 0x80000):
            handle = kernel.CreateFileW(str(target), rights, 7, None, 3, 0, None)
            self.assertEqual(handle, ctypes.c_void_p(-1).value)
            self.assertEqual(ctypes.get_last_error(), 5)
        control = self.root / "unsealed-control"
        control.write_bytes(b"control")
        for path, permitted in ((target, False), (control, True)):
            handle = kernel.CreateFileW(str(path), 0, 7, None, 3, 0, None)
            self.assertNotEqual(handle, ctypes.c_void_p(-1).value)
            try:
                name = ("\\??\\" + str(path.with_name(path.name + "-alias"))).encode("utf-16-le")
                pointer = ctypes.sizeof(ctypes.c_void_p)
                root_offset = (4 + pointer - 1) // pointer * pointer
                offset = root_offset + pointer + 4
                buffer = ctypes.create_string_buffer(offset + len(name) + 2)
                ctypes.c_uint32.from_buffer(buffer, offset - 4).value = len(name)
                ctypes.memmove(ctypes.addressof(buffer) + offset, name, len(name))
                status = oe._WindowsIoStatusV1()
                code = native.NtSetInformationFile(handle, ctypes.byref(status), buffer, offset + len(name), 11)
                self.assertEqual(code >= 0, permitted)
                if not permitted:
                    self.assertEqual(code & 0xffffffff, 0xC0000022)
            finally:
                kernel.CloseHandle(handle)


if __name__ == "__main__":
    unittest.main()
