#!/usr/bin/env python3
"""Executable-source controls for the claim companion's projection load.

Disposable layout copies are source evidence, not installation, authentication
or native-effect qualification. The shell-to-companion edge is separate.
"""
from __future__ import annotations

import builtins
import hashlib
import os
from pathlib import Path
import shutil
import sys
import tempfile
import types
import unittest
from unittest import mock

sys.dont_write_bytecode = True
SOURCE = Path(__file__).resolve().parents[1] / "skills/implementaudit/scripts"
MEMBERS = ("claim-run-rotation.py", "rotate-canonical-state.py",
           "canonical_hot_projection.py", "canonical_custody.py")
MODULE_PREFIX = "_claim_owned_rotation_projection_"
MARKER = "R002E_CUSTODY_MARKER"


class ProjectionSourceCustody(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="canonical-source-custody-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.modules = set(sys.modules)
        self.addCleanup(self.clear_modules)
        self.owner, self.projection = self.layout("source", "skills/implementaudit/scripts")
        self.original = self.projection.read_bytes()

    def clear_modules(self):
        for name in set(sys.modules) - self.modules:
            if name.startswith((MODULE_PREFIX, "canonical_source_test_")):
                sys.modules.pop(name, None)

    def layout(self, label, relative):
        scripts = self.root / label / relative
        scripts.mkdir(parents=True)
        for name in MEMBERS:
            shutil.copyfile(SOURCE / name, scripts / name)
        path = scripts / "claim-run-rotation.py"
        name = "canonical_source_test_" + label
        module = types.ModuleType(name)
        module.__file__ = str(path)
        sys.modules[name] = module
        exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
        return module, scripts / "rotate-canonical-state.py"

    def changed_source(self):
        old = b"# The controller's existing source identity transitively binds this new owner."
        marker = (MARKER + " = True").encode()
        self.assertEqual(self.original.count(old), 1)
        changed = self.original.replace(old, marker.ljust(len(old)))
        self.assertEqual(len(changed), len(self.original))
        self.assertNotEqual(hashlib.sha256(changed).digest(), hashlib.sha256(self.original).digest())
        return changed

    def assert_refused_before_compile(self, owner=None):
        owner = self.owner if owner is None else owner
        with mock.patch.object(owner, "compile", wraps=builtins.compile, create=True) as compiled:
            with self.assertRaises((owner.RotationError, OSError)):
                owner.projection_helper()
            self.assertEqual(compiled.call_count, 0, "unapproved source reached compile")

    def test_exact_source_and_both_package_layouts_load(self):
        for label, relative in (("source", None), ("plugin", "skills/implementaudit/scripts"),
                                ("standalone", "scripts")):
            with self.subTest(layout=label):
                self.clear_modules()
                owner = self.owner if relative is None else self.layout(label, relative)[0]
                loaded = owner.projection_helper()
                self.assertTrue(callable(loaded.prepare_canonical_draft))
                self.assertTrue(callable(loaded.read_canonical_generation))
                self.assertFalse(getattr(loaded, MARKER, False))

    def test_same_size_source_drift_refuses_before_execution(self):
        self.projection.write_bytes(self.changed_source())
        self.assert_refused_before_compile()

    def test_wrong_source_lengths_refuse_before_execution(self):
        for content in (self.original[:-1], self.original + b"\n"):
            with self.subTest(bytes=len(content)):
                self.projection.write_bytes(content)
                self.assert_refused_before_compile()

    def test_missing_or_invalid_binding_refuses_before_read(self):
        fields = {
            "_PROJECTION_MODULE_BYTES": [None, False, 0, -1, "92941", 1.5, 64 * 1024 * 1024 + 1],
            "_PROJECTION_MODULE_SHA256": [None, False, "", "0" * 63, "G" * 64,
                                          "A" * 64, "0" * 64 + "\n"],
        }
        for name, values in fields.items():
            for value in values:
                with self.subTest(binding=name, value=value):
                    with mock.patch.object(self.owner, name, value, create=True):
                        with mock.patch.object(self.owner, "read_regular",
                                               side_effect=AssertionError("unbound source read")):
                            self.assert_refused_before_compile()
            original = self.owner.__dict__.pop(name, None)
            try:
                with self.subTest(binding=name, value="MISSING"):
                    with mock.patch.object(self.owner, "read_regular",
                                           side_effect=AssertionError("unbound source read")):
                        self.assert_refused_before_compile()
            finally:
                if original is not None:
                    self.owner.__dict__[name] = original

    def test_well_formed_wrong_binding_does_not_accept_source(self):
        for name, value in (("_PROJECTION_MODULE_BYTES", len(self.original) - 1),
                            ("_PROJECTION_MODULE_BYTES", len(self.original) + 1),
                            ("_PROJECTION_MODULE_SHA256", "0" * 64)):
            with self.subTest(binding=name, value=value):
                with mock.patch.object(self.owner, name, value, create=True):
                    self.assert_refused_before_compile()

    def test_missing_source_refuses_before_execution(self):
        self.projection.unlink()
        self.assert_refused_before_compile()

    def test_multiple_links_refuse_before_execution(self):
        os.link(self.projection, self.projection.with_suffix(".alias"))
        self.assert_refused_before_compile()

    @unittest.skipUnless(os.name == "posix", "POSIX alias control; Windows custody has its own bank")
    def test_symbolic_link_refuses_before_execution(self):
        physical = self.projection.with_suffix(".physical")
        self.projection.rename(physical)
        self.projection.symlink_to(physical)
        self.assert_refused_before_compile()

    def test_capture_to_execution_drift_keeps_verified_buffer(self):
        actual_read = self.owner.read_regular

        def capture_then_change(path, **kwargs):
            raw = actual_read(path, **kwargs)
            self.projection.write_bytes(self.changed_source())
            return raw

        with mock.patch.object(self.owner, "read_regular", side_effect=capture_then_change):
            with mock.patch.object(self.owner, "compile", wraps=builtins.compile, create=True) as compiled:
                loaded = self.owner.projection_helper()
                self.assertEqual(compiled.call_count, 1)
                self.assertEqual(compiled.call_args.args[0], self.original)
        self.assertTrue(callable(loaded.prepare_native_resume_draft))
        self.assertFalse(getattr(loaded, MARKER, False))
        self.assertNotEqual(self.projection.read_bytes(), self.original)
        self.assert_refused_before_compile()

    def test_warm_cache_does_not_hide_changed_source(self):
        original_module = self.owner.projection_helper()
        self.assertIs(self.owner.projection_helper(), original_module)
        self.projection.write_bytes(self.changed_source())
        self.assert_refused_before_compile()


if __name__ == "__main__":
    unittest.main()
