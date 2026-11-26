#!/usr/bin/env python3
"""Finite leaf ELF-interpreter closure controls; no native campaign authority."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import subprocess
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("finite_elf_qualifier", REPO / "scripts/qualify-work-graph-verifier.py")
Q = importlib.util.module_from_spec(spec)
spec.loader.exec_module(Q)
S = Q.VerifierTaskSession
OLD = "/lib64/ld-linux-x86-64.so.2"
ALIAS = "/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2"
PROGRAMS = ("/usr/bin/bash", "/usr/bin/dirname", "/usr/bin/python3.12")


def elf(interpreter=OLD, *, duplicate=False):
    """Explicit constructed ELF header, never executed or called host evidence."""
    body = interpreter.encode("ascii") + b"\0"
    count = 2 if duplicate else 1
    header = b"\x7fELF\x02\x01\x01" + b"\0" * 9
    header += struct.pack("<HHIQQQIHHHHHH", 3, 62, 1, 0, 64, 0, 0, 64, 56, count, 0, 0, 0)
    ph = struct.pack("<IIQQQQQQ", 3, 4, 64 + 56 * count, 0, 0, len(body), len(body), 1)
    return header + ph * count + body


def runtime_files(interpreter=OLD):
    files = {name: (b"constructed library", 0o555) for name in S.RUNTIME_FILES}
    files.update({name: (elf(interpreter), 0o555) for name in PROGRAMS})
    files[OLD] = (b"constructed identical loader bytes", 0o555)
    if interpreter == ALIAS:
        files[ALIAS] = files[OLD]
    return files


class InterpreterControls(unittest.TestCase):
    def session(self, directory):
        s = object.__new__(S)
        s.runtime_root = directory / "runtime"
        s.runtime_root.mkdir()
        s.output = directory / "evidence"
        s.output.mkdir()
        s.environment = dict(S.ENVIRONMENT)
        return s

    def write_runtime(self, s, files):
        for name, (data, mode) in files.items():
            path = s.runtime_root / name.lstrip("/")
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists():
                path.chmod(0o600)
            path.write_bytes(data)
            path.chmod(mode)

    def test_actual_header_requirement_captures_missing_named_alias(self):
        with tempfile.TemporaryDirectory() as td:
            s = self.session(Path(td))
            original = runtime_files(ALIAS)
            self.write_runtime(s, original)
            captured = s._runtime()
            self.assertIn(ALIAS, captured)
            self.assertEqual(captured[ALIAS], original[OLD])
            self.assertEqual({name: captured[name] for name in original}, original)

    def test_unrequested_alias_is_not_added_and_other_scopes_stay_unchanged(self):
        with tempfile.TemporaryDirectory() as td:
            s = self.session(Path(td))
            self.write_runtime(s, runtime_files())
            self.assertNotIn(ALIAS, s._runtime())
            s.SCOPE = "CONTROLLED_TASK_REGISTRY_V1"
            files = runtime_files(ALIAS)
            self.write_runtime(s, files)
            self.assertNotIn(ALIAS, s._runtime())
            self.assertIsNone(s._leaf_runtime_binding_v1(files))

    def test_required_loader_alias_must_match_retained_loader(self):
        with tempfile.TemporaryDirectory() as td:
            s = self.session(Path(td))
            files = runtime_files(ALIAS)
            files[ALIAS] = (b"different loader", 0o555)
            self.write_runtime(s, files)
            with self.assertRaisesRegex(Q.WG.WorkGraphError, "loader alias"):
                s._runtime()

    def test_manifest_binds_actual_program_and_interpreter_bytes(self):
        with tempfile.TemporaryDirectory() as td:
            s = self.session(Path(td))
            files = runtime_files(ALIAS)
            manifest, digest = s._image(files, {})
            binding = manifest["leaf_elf_interpreters"]
            self.assertEqual(binding["schema"], "implementaudit.finite-leaf-elf-interpreters.v1")
            self.assertEqual(set(binding["programs"]), set(PROGRAMS))
            for name, row in binding["programs"].items():
                self.assertEqual(row["program_sha256"], hashlib.sha256(files[name][0]).hexdigest())
                self.assertEqual(row["program_bytes"], len(files[name][0]))
                self.assertEqual(row["interpreter"], ALIAS)
                self.assertEqual(row["interpreter_sha256"], hashlib.sha256(files[ALIAS][0]).hexdigest())
            changed = dict(files)
            changed["/usr/bin/python3.12"] = (elf(ALIAS) + b"new bytes", 0o555)
            changed_manifest, changed_digest = s._image(changed, {})
            self.assertNotEqual(changed_digest, digest)
            self.assertNotEqual(changed_manifest["leaf_elf_interpreters"], binding)

    def test_absent_interpreter_refuses_before_dispatch_directory(self):
        with tempfile.TemporaryDirectory() as td:
            s = self.session(Path(td))
            files = runtime_files(ALIAS)
            manifest, _ = s._image(files, {})
            del files[ALIAS]
            target = Path(td) / "must-not-start"
            with self.assertRaisesRegex(Q.WG.WorkGraphError, "interpreter.*missing"):
                s._execute({"images": {"node": (files, manifest)}}, {"id": "node"}, {}, target)
            self.assertFalse(target.exists())

    def test_observation_drift_refuses_before_dispatch_directory(self):
        with tempfile.TemporaryDirectory() as td:
            s = self.session(Path(td))
            files = runtime_files()
            manifest, _ = s._image(files, {})
            def forbidden_seal(_data):
                raise AssertionError("unvalidated ELF observation reached input sealing")
            s._sealed = forbidden_seal
            for mutation in ("remove", "alter"):
                damaged = copy.deepcopy(manifest)
                if mutation == "remove":
                    del damaged["leaf_elf_interpreters"]
                else:
                    damaged["leaf_elf_interpreters"]["programs"][PROGRAMS[0]]["program_sha256"] = "0" * 64
                target = Path(td) / mutation
                with self.assertRaisesRegex(Q.WG.WorkGraphError, "interpreter observation differs"):
                    s._execute({"images": {"node": (files, damaged)}, "acquired": {}},
                               {"id": "node"}, {}, target)
                self.assertFalse(target.exists())

    def test_bounded_parser_refuses_malformed_or_unsupported_elf(self):
        valid = elf()
        bad = [b"not ELF", valid[:63], valid[:120], elf(duplicate=True), elf("/tmp/loader"),
               valid[:4] + b"\x01" + valid[5:], valid[:5] + b"\x02" + valid[6:],
               valid[:18] + struct.pack("<H", 183) + valid[20:],
               valid[:54] + struct.pack("<H", 55) + valid[56:],
               valid[:56] + struct.pack("<H", 129) + valid[58:],
               valid[:32] + struct.pack("<Q", 2**64-1) + valid[40:],
               valid[:96] + struct.pack("<Q", 257) + valid[104:],
               valid[:-1] + b"x", elf(OLD + "\0extra")]
        for value in bad:
            with self.subTest(sha256=hashlib.sha256(value).hexdigest()):
                with self.assertRaises(Q.WG.WorkGraphError):
                    S._leaf_elf_interpreter_v1(value)

    def test_missing_program_and_nonexecutable_loader_refuse(self):
        s = object.__new__(S)
        files = runtime_files()
        del files[PROGRAMS[1]]
        with self.assertRaisesRegex(Q.WG.WorkGraphError, "program.*missing"):
            s._leaf_runtime_binding_v1(files)
        files = runtime_files()
        files[OLD] = (files[OLD][0], 0o444)
        with self.assertRaisesRegex(Q.WG.WorkGraphError, "interpreter.*executable"):
            s._leaf_runtime_binding_v1(files)

    def test_actual_local_elf_agrees_with_independent_readelf(self):
        # This is the local bash, not an attribution to the hosted Python.
        actual = Path("/usr/bin/bash").read_bytes()
        interpreter = S._leaf_elf_interpreter_v1(actual)
        observed = subprocess.run(["/usr/bin/readelf", "--program-headers", "/usr/bin/bash"],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10, check=True)
        self.assertIn(("Requesting program interpreter: " + interpreter + "]").encode(), observed.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
