#!/usr/bin/env python3
"""Source capture and actual image-environment controls; no original48 or package import."""
import ast
import copy
import json
import os
import stat
import subprocess
import sys
import types
import hashlib
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
LOADER = "scripts/load-work-graph-readme-effect.py"


def loader(root=ROOT):
    path = root / LOADER
    spec = importlib.util.spec_from_file_location("c5_control_loader", path)
    module = importlib.util.module_from_spec(spec)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


class C5InputCases(unittest.TestCase):
    def test_actual_selected_normal_startup_and_alias(self):
        """Break caught: synthetic no-site alias or unbound alias ancestry."""
        owner = loader()._load_c5_owner()
        objects = {}
        observed = owner.selected_startup(objects)
        self.assertEqual(observed["selected_command"], "python3")
        self.assertEqual(observed["selected_target"], "/usr/bin/python3.12")
        self.assertEqual(observed["startup"], "NORMAL_SITE_NO_ORIGINAL_S_OR_I")
        self.assertEqual(observed["compressor"]["status"], "MISSING_GENUINE_PROVIDER")
        self.assertIn("/etc/passwd", observed["files"])
        self.assertIn("/usr/lib/python3.12/sitecustomize.py", observed["files"])
        for row in observed["files"].values():
            self.assertEqual(hashlib.sha256(objects[row["sha256"]]).hexdigest(), row["sha256"])
            self.assertTrue(row["ancestors"])
        with tempfile.TemporaryDirectory(prefix="c5-alias-") as temporary:
            parent = Path(temporary) / "parent"
            parent.mkdir()
            target = parent / "data"
            target.write_bytes(b"actual captured bytes\n")
            alias = Path(temporary) / "alias"
            alias.symlink_to(target)
            captured = owner.capture_selector(alias, {})
            self.assertEqual(captured["link"], str(target))
            moved = Path(temporary) / "old-parent"
            parent.rename(moved)
            parent.mkdir()
            (moved / "data").rename(target)
            current = owner.capture_selector(alias, {})
            self.assertEqual(captured["sha256"], current["sha256"])
            with self.assertRaises(ValueError):
                owner.require_same(captured, current, "ancestor")

    def test_complete_inputs_and_added_selector_refuse(self):
        """Break caught: omitted inputs, added startup code or unbounded final union."""
        owner = loader()._load_c5_owner()
        with tempfile.TemporaryDirectory(prefix="c5-inputs-") as temporary:
            root = Path(temporary)
            (root / ".git").mkdir()
            (root / ".git" / "index").write_bytes(b"controlled index bytes\n")
            (root / ".hidden").write_bytes(b"hidden bytes\n")
            (root / "empty").mkdir()
            objects = {}
            first = owner.complete_source(root, objects)
            self.assertEqual(set(first["state"]["files"]), {".git/index", ".hidden"})
            self.assertIn("empty", first["state"]["directories"])
            self.assertEqual(sum(row["bytes"] for row in first["state"]["files"].values()), 36)
            (root / ".added").write_bytes(b"new selector\n")
            with self.assertRaises(ValueError):
                owner.require_same(first, owner.complete_source(root, {}), "source")
        startup_objects = {}
        startup = owner.selected_startup(startup_objects)
        actual_startup_objects = dict(startup_objects)
        altered = copy.deepcopy(startup)
        root = "/usr/local/lib/python3.12/dist-packages"
        altered["namespaces"][root]["names"]["added.pth"] = ["present controlled selector"]
        raw = b"import unclosed_provider\n"
        key = hashlib.sha256(raw).hexdigest()
        altered["namespaces"][root]["pth"]["added.pth"] = {"sha256": key, "bytes": len(raw), "mode": 0o644}
        startup_objects[key] = raw
        with self.assertRaises(ValueError):
            owner.validate_startup(altered, startup_objects)

        # Merge-only fixtures use the actual descriptors and bytes captured above.
        # The .pth-only case must cross the boundary after the last merge, so a
        # guard placed before that merge cannot satisfy this discriminator.
        empty_startup = dict(aliases={}, files={}, namespaces={})
        with mock.patch.object(owner, "selected_startup", return_value=empty_startup):
            base_runtime = owner._runtime_inputs(dict(actual_startup_objects))
        base_files = base_runtime["files"]
        base_bytes = sum(row["bytes"] for row in base_files.values())
        added_pth = {root + "/" + name: row
                     for root, namespace in startup["namespaces"].items()
                     for name, row in namespace["pth"].items()
                     if root + "/" + name not in base_files}
        self.assertGreater(sum(row["bytes"] for row in added_pth.values()), 0)
        for row in added_pth.values():
            self.assertEqual(len(actual_startup_objects[row["sha256"]]), row["bytes"])
            self.assertEqual(hashlib.sha256(actual_startup_objects[row["sha256"]]).hexdigest(), row["sha256"])
        bounds = dict(owner.P.RUNTIME_BOUNDS)
        pth_only = dict(aliases={}, files={}, namespaces=startup["namespaces"])
        with mock.patch.object(owner, "selected_startup", return_value=pth_only):
            with mock.patch.dict(owner.P.RUNTIME_BOUNDS, {"mounted_bytes": base_bytes}):
                with self.assertRaisesRegex(ValueError, "^runtime image bound exceeded$"):
                    owner._runtime_inputs(dict(actual_startup_objects))
        self.assertEqual(owner.P.RUNTIME_BOUNDS, bounds)

    def test_no_dispatch_and_default_owner_compatibility(self):
        """Break caught: C5 widens default inputs or source capture dispatches."""
        outer = loader()
        with tempfile.TemporaryDirectory(prefix="c5-default-") as temporary:
            root = Path(temporary)
            for name in [LOADER, *outer.PINS]:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / name, target)
            legacy = loader(root)
            engine = legacy._Engine()
            self.assertEqual(set(engine.sources), set(outer.PINS))
            with self.assertRaises(ValueError):
                legacy._read("scripts/work-graph-c5-inputs.py")
            # C5 files are absent, yet default capture remains fully usable.
            engine.check()
            with self.assertRaises((ValueError, FileNotFoundError)):
                legacy.create_c5_input_capture(root)
        with mock.patch("subprocess.Popen", side_effect=AssertionError("source capture attempted dispatch")):
            capture = outer.create_c5_input_capture(ROOT)
            result = capture.acquire()
        self.assertEqual(result["record"]["dispatch_count"], 0)
        self.assertFalse(result["record"]["runtime_complete"])
        self.assertEqual(result["record"]["canonical_acceptance"], "UNQUALIFIED")
        self.assertIn("ZOPFLI_PROVIDER_MISSING", result["record"]["blockers"])
        self.assertEqual(len(result["record"]["producer_contract"]["roles"]), 19)
        self.assertEqual(len(result["record"]["producer_contract"]["release_producers"]), 6)
        self.assertFalse(hasattr(capture, "run"))


@unittest.skipUnless(sys.platform.startswith("linux") and shutil.which("bwrap"), "Linux Bubblewrap required")
class C5ImageEnvironmentCases(unittest.TestCase):
    def test_actual_image_environment_and_foreign_input_refusal(self):
        """Actual bwrap cwd insertion must equal the strict bootstrap declaration."""
        prefix = ast.parse((ROOT / "scripts/qualify-work-graph-prefix.py").read_bytes())
        base = next(n.value for n in prefix.body if isinstance(n, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == "ENVIRONMENT" for t in n.targets))
        values = eval(compile(ast.Expression(base), "<fixed-environment>", "eval"), {"dict": dict})
        executor = ast.parse((ROOT / "scripts/work-graph-c5-executor.py").read_bytes())
        owner = next(n for n in executor.body if isinstance(n, ast.ClassDef) and n.name == "GenuineC5Session")
        image = next(n for n in owner.body if isinstance(n, ast.FunctionDef) and n.name == "_image")
        selected = next(n.value for n in image.body if isinstance(n, ast.Assign)
                        and any(isinstance(t, ast.Name) and t.id == "environment" for t in n.targets))
        planned = eval(compile(ast.Expression(selected), "<actual-image-environment>", "eval"),
                       {"dict": dict, "D": types.SimpleNamespace(_ENVIRONMENT=values),
                        "SOURCE_MOUNT": "/work", "WORK_MOUNT": "/c5-work", "gate_fd": 9})
        command = [shutil.which("bwrap"), "--unshare-all", "--unshare-user", "--die-with-parent",
                   "--new-session", "--clearenv", "--cap-drop", "ALL"]
        for name, value in sorted(planned.items()):
            command += ["--setenv", name, value]
        command += ["--ro-bind", "/usr", "/usr", "--ro-bind", "/lib", "/lib", "--ro-bind", "/lib64", "/lib64", "--proc", "/proc", "--dir", "/work", "--chdir", "/work"]
        program = [sys.executable, "-I", "-S", "-B", "-c", "import os,json; print(json.dumps(dict(os.environ)))"]
        for foreign in (False, True):
            actual_command = command + (["--setenv", "UNSELECTED_C5_INPUT", "foreign"] if foreign else []) + ["--", *program]
            outcome = subprocess.run(actual_command, capture_output=True, text=True, timeout=15)
            self.assertEqual(outcome.returncode, 0, outcome.stderr)
            observed = json.loads(outcome.stdout)
            self.assertEqual(observed == planned, not foreign, (planned, observed))


class C5TaskEntropyCases(unittest.TestCase):
    TASK = "FIXED_GENUINE_C5_PRODUCER_EFFECT_SOL_TASK_LINUX_20261029_V1"
    def guard(self):
        tree = ast.parse((ROOT / "scripts/work-graph-c5-executor.py").read_bytes())
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "task_kernel_entropy_v1")
        namespace = dict(PROFILE=self.TASK, SPEC=dict(kernel_entropy_policy="C5_TASK_FIXED_GIT_REAL_URANDOM_V1",
            original_index=48, original_argv=["bash", "tests/reproducible-release-asset.test.sh"]))
        def need(value, message):
            if not value: raise ValueError(message)
        namespace.update(need=need, fixed_task_entropy_device_v1=mock.Mock(return_value={"observed": "real-device-facts"}))
        exec(compile(ast.Module(body=[function], type_ignores=[]), "<actual-entropy-admission>", "exec"), namespace)
        return namespace

    def test_exact_task_program_and_git_only(self):
        n = self.guard()
        source = dict(source=dict(state=dict(files={"tests/reproducible-release-asset.test.sh":
            dict(sha256="a27521758cc71e312052d7eaa7c8b488dbbe2dcc5089d6054be0923455763310")})))
        runtime = dict(files={"/usr/bin/git":dict(sha256="2a8c18fbf43da9f692d75474c72bea9dfd796c260b0f3dfe456376abc3bbd668")})
        self.assertEqual(n["task_kernel_entropy_v1"](source, runtime), {"observed": "real-device-facts"})
        for which in ("policy", "index", "argv", "program", "git"):
            candidate = self.guard(); a, b = copy.deepcopy(source), copy.deepcopy(runtime)
            if which == "policy": candidate["SPEC"]["kernel_entropy_policy"] = "arbitrary-device-policy"
            elif which == "index": candidate["SPEC"]["original_index"] = 87
            elif which == "argv": candidate["SPEC"]["original_argv"] = ["bash", "other.sh"]
            elif which == "program": a["source"]["state"]["files"]["tests/reproducible-release-asset.test.sh"]["sha256"] = "0"*64
            else: b["files"]["/usr/bin/git"]["sha256"] = "0"*64
            with self.subTest(which=which), self.assertRaises(ValueError): candidate["task_kernel_entropy_v1"](a,b)
            candidate["fixed_task_entropy_device_v1"].assert_not_called()

    def test_device_type_identity_and_alias_refusals(self):
        tree = ast.parse((ROOT / "scripts/work-graph-c5-executor.py").read_bytes())
        functions = [n for n in tree.body if isinstance(n, ast.FunctionDef)
                     and n.name in ("stamp", "fixed_task_entropy_device_v1")]
        def need(value, message):
            if not value: raise ValueError(message)
        n = dict(os=os, stat=stat, need=need)
        exec(compile(ast.Module(body=functions,type_ignores=[]), "<actual-device-observer>", "exec"), n)
        valid = dict(st_dev=1,st_ino=7,st_mode=stat.S_IFCHR|0o666,st_nlink=1,st_size=0,
                     st_mtime_ns=11,st_ctime_ns=12,st_uid=65534,st_gid=65534,st_rdev=os.makedev(1,9))
        for mutation in (None, "regular", "minor", "owner", "link", "identity"):
            first = dict(valid)
            if mutation == "regular": first["st_mode"] = stat.S_IFREG|0o666
            if mutation == "minor": first["st_rdev"] = os.makedev(1,8)
            if mutation == "owner": first["st_uid"] = 0
            path = mock.Mock();path.resolve.return_value = path if mutation != "link" else Path("/other-device")
            second = dict(first)
            if mutation == "identity": second["st_ino"] += 1
            path.lstat.side_effect = [types.SimpleNamespace(**first), types.SimpleNamespace(**second)]
            n["Path"] = mock.Mock(return_value=path)
            with self.subTest(mutation=mutation):
                if mutation is None:
                    result = n["fixed_task_entropy_device_v1"]()
                    self.assertEqual(result["identity"][-1], os.makedev(1,9))
                else:
                    with self.assertRaises(ValueError): n["fixed_task_entropy_device_v1"]()
            path.open.assert_not_called()

    def test_other_profiles_never_observe_or_expose_device(self):
        for profile in ("FIXED_GENUINE_C5_PRODUCER_EFFECT_ORIGINAL48_V1",
                        "FIXED_GENUINE_C5_PRODUCER_EFFECT_CURRENT_COMPOSITE_20261027_V1"):
            n = self.guard(); n["PROFILE"] = profile; n["SPEC"] = {}
            self.assertIsNone(n["task_kernel_entropy_v1"]({}, {}))
            n["fixed_task_entropy_device_v1"].assert_not_called()
            n["SPEC"]["kernel_entropy_policy"] = "C5_TASK_FIXED_GIT_REAL_URANDOM_V1"
            with self.assertRaises(ValueError): n["task_kernel_entropy_v1"]({}, {})
            n["fixed_task_entropy_device_v1"].assert_not_called()


if __name__ == "__main__":
    unittest.main()
