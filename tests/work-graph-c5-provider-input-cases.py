#!/usr/bin/env python3
"""Three data-only provider controls; no provider import, original or build."""
import builtins
from contextlib import contextmanager
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


@contextmanager
def retained_temporary(*, prefix):
    """Retain each physical negative fixture under the observer-owned TMPDIR."""
    temporary = tempfile.mkdtemp(prefix=prefix)
    try:
        yield temporary
    finally:
        print("RETAINED_CONTROL_FIXTURE=" + temporary, flush=True)


def loader():
    path = ROOT / "scripts/load-work-graph-readme-effect.py"
    spec = importlib.util.spec_from_file_location("c5_provider_control_loader", path)
    module = importlib.util.module_from_spec(spec)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


class C5ProviderInputCases(unittest.TestCase):
    def test_actual_provider_complete_data_only(self):
        """Break caught: substituted provider, omitted inputs or false runtime credit."""
        original_import = builtins.__import__
        def no_provider_import(name, *args, **kwargs):
            if name == "zopfli" or name.startswith("zopfli."):
                raise AssertionError("data acquisition attempted a provider import")
            return original_import(name, *args, **kwargs)
        with mock.patch.object(builtins, "__import__", side_effect=no_provider_import), \
                mock.patch("subprocess.Popen", side_effect=AssertionError("data acquisition attempted dispatch")):
            capture = loader().create_c5_provider_input_capture(ROOT)
            observed = capture.acquire()
        record = observed["record"]
        runtime = record["runtime"]
        provider = runtime["provider"]
        self.assertEqual(provider["status"], "GENUINE_PROVIDER_INPUTS_CAPTURED")
        self.assertEqual(len(provider["installation"]["files"]), 28)
        self.assertEqual(sum(row["bytes"] for row in provider["installation"]["files"].values()), 26980874)
        self.assertEqual(provider["installation"]["links"]["lib64"]["link"], "lib")
        self.assertEqual(len(provider["native"]), 3)
        self.assertEqual(runtime["startup"]["selected_command"], "python")
        self.assertEqual(runtime["startup"]["selected_target"], provider["installation"]["root"] + "/bin/python")
        self.assertEqual(record["dispatch_count"], 0)
        self.assertEqual(record["provider_imports"], 0)
        self.assertFalse(record["runtime_complete"])
        self.assertEqual(record["canonical_acceptance"], "UNQUALIFIED")
        self.assertIn("PROVIDER_NATIVE_EXECUTION_CUSTODY_UNQUALIFIED", record["blockers"])
        self.assertIn("BEFORE_CONSUMER_JOIN_UNIMPLEMENTED", record["blockers"])
        self.assertFalse(hasattr(capture, "run"))
        # A genuine fixed-budget refusal remains a failed positive control.
        # It is never caught and converted into full-runtime qualification.

    def test_actual_provider_ancestor_currentness_refuses(self):
        """Break caught: accepting same bytes after an actual ancestor replacement."""
        owner = loader()._load_c5_provider_owner()
        with retained_temporary(prefix="c5-provider-current-") as temporary:
            root = Path(temporary) / "venv"
            shutil.copytree(owner.VENV, root, symlinks=True, copy_function=shutil.copy2)
            captured = owner._capture_tree(root, {})
            site = root / "lib/python3.12/site-packages"
            old = Path(temporary) / "old-site"
            site.rename(old)
            shutil.copytree(old, site, symlinks=True, copy_function=shutil.copy2)
            current = owner._capture_tree(root, {})
            self.assertEqual({n: r["sha256"] for n, r in captured["files"].items()},
                             {n: r["sha256"] for n, r in current["files"].items()})
            with self.assertRaisesRegex(ValueError, "provider bytes/namespace/ancestors"):
                owner._require_tree_current(root, captured)

    def test_added_startup_and_changed_native_bytes_refuse(self):
        """Break caught: new startup code or changed installed native bytes admitted."""
        owner = loader()._load_c5_provider_owner()
        with retained_temporary(prefix="c5-provider-refuse-") as temporary:
            root = Path(temporary) / "venv"
            shutil.copytree(owner.VENV, root, symlinks=True, copy_function=shutil.copy2)
            added = root / "lib/python3.12/site-packages/added.pth"
            added.write_bytes(b"import unsupported_provider_selector\n")
            with self.assertRaisesRegex(ValueError, "provider namespace differs"):
                owner._capture_tree(root, {})
            shutil.copy2(added, Path(temporary) / "added.pth.refused")
            added.unlink()
            native = root / "lib/python3.12/site-packages/zopfli/zopfli.cpython-312-x86_64-linux-gnu.so"
            raw = native.read_bytes()
            native.write_bytes(raw[:-1] + bytes([raw[-1] ^ 1]))
            self.assertEqual(native.stat().st_size, len(raw))
            with self.assertRaisesRegex(ValueError, "provider file differs"):
                owner._capture_tree(root, {})


if __name__ == "__main__":
    unittest.main()
