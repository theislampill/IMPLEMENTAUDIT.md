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
import socket
import time
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



def correspondence_profile_globals():
    # Context for extracted maintained functions. The full module declares
    # these same closed names; fragment tests must supply their actual globals.
    old = 'FIXED_GENUINE_C5_SHARED_IMAGE_CORRESPONDENCE_20261031_V1'
    fresh = 'FIXED_GENUINE_C5_SHARED_IMAGE_CORRESPONDENCE_R4_CURRENT_HOST_20261104_V1'
    cache = 'FIXED_GENUINE_C5_SHARED_IMAGE_CORRESPONDENCE_R4_BUILD_LOCAL_COMPRESSION_20261104_V1'
    hosted = 'FIXED_GENUINE_C5_SHARED_IMAGE_R5_HOSTED_UBUNTU24_SINGLE_COPY_20261105_V1'
    return dict(CORRESPONDENCE_PROFILE=old, R4_CORRESPONDENCE_PROFILE=fresh,
                R4_BUILD_CACHE_PROFILE=cache, R4_HOST_PROFILES=(fresh, cache),
                R5_HOSTED_PROFILE=hosted, UID0_HOST_PROFILES=(fresh, cache, hosted),
                CORRESPONDENCE_PROFILES=(old, fresh, cache, hosted))


def _selected_source_fixture():
    path = ROOT / 'tests/c5-selected-source-fixture.py'
    module = types.ModuleType('c5_input_cases_selected_source_fixture')
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    return module


def copy_c5_closed_source(destination, *, current_builder=False, profile=None, revision=None):
    """Materialize exact selected physical members, including historical owners."""
    fixture = _selected_source_fixture()
    path = ROOT / 'scripts/load-work-graph-c5-executor.py'
    module = types.ModuleType('c5_fixture_selected_source'); module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), 'exec'), module.__dict__)
    if profile is None:
        profile = module.R4_BUILD_CACHE_PROFILE if current_builder else module.CORRESPONDENCE_PROFILE
    if revision is None:
        revision = module.R4_BUILD_CACHE_SOURCE_REVISION if current_builder else module.R4_COMPOSED_SOURCE_REVISION
    pins = module._selection(profile, revision)[0]
    planned = {module.LOADER: module.LOADER}
    for name, pin in pins.items():
        physical = fixture.physical_member(module, name, pin, profile, revision)
        source_name = fixture.RETAINED.get((name, pin), physical)
        planned[physical] = source_name
        planned.setdefault(name, source_name)
    for physical, source_name in sorted(planned.items()):
        target = destination / physical; target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((ROOT / source_name).read_bytes()); target.chmod(0o644)
    return planned


def c5_ubuntu24_uid0_startup_host():
    if os.name != "posix" or (os.getuid(), os.geteuid(), os.getgid(), os.getegid()) != (0, 0, 0, 0):
        return False
    target = Path("/usr/bin/python3.12")
    if not target.is_file():
        return False
    pin = json.loads((ROOT / "fixtures/work-graph-c5-inputs/execution-current-composite-python312.json").read_bytes())["runtime_pins"]["/usr/bin/python3.12"]
    return hashlib.sha256(target.read_bytes()).hexdigest() == pin["sha256"]


class C5InputFixture:
    def data_owner(self):
        # These controls concern maintained data capture, not the legacy
        # README route's historical source identity. Select the exact closed
        # explicit composed R4 tuple; loading its bound base owner dispatches nothing.
        temporary = tempfile.TemporaryDirectory(prefix='c5-current-input-owner-')
        self.addCleanup(temporary.cleanup)
        source = Path(temporary.name) / 'source'
        _selected_source_fixture().materialize(ROOT, source, 'R4_CURRENT')
        path = source / 'scripts/load-work-graph-c5-executor.py'
        spec = importlib.util.spec_from_file_location('c5_current_input_controls', path)
        outer = importlib.util.module_from_spec(spec)
        exec(compile(path.read_bytes(), str(path), 'exec'), outer.__dict__)
        return outer._Engine(outer.CURRENT_PROFILE,
                             source_revision=outer.R4_COMPOSED_SOURCE_REVISION).load().B

    def historical_engine(self, destination):
        path = ROOT / 'tests/work-graph-historical-fixture.py'
        spec = importlib.util.spec_from_file_location('c5_historical_input_controls', path)
        historical = importlib.util.module_from_spec(spec)
        exec(compile(path.read_bytes(), str(path), 'exec'), historical.__dict__)
        return historical.copy_readme_engine(destination)

    def data_subject(self, owner, destination):
        # A standalone physical source for the fixed current-system selection.
        # Its two older producers are retained bytes, never reconstructed or run.
        history = ROOT / 'test-support/work-graph-c5-profile-history/current-system-producers-20261104'
        manifest = json.loads((history / 'MANIFEST.json').read_bytes())
        retained = {row['path']: row for row in manifest['files']}
        for name in sorted(set(owner.SPEC['programs']) | set(owner.SPEC['payload_sources'])):
            selected = history / name if name in retained else ROOT / name
            if name == "scripts/package-contract.py":
                selected = ROOT / "fixtures/work-graph-c5-inputs/r4-package-contract-before-build-cache.py"
                if hashlib.sha256(selected.read_bytes()).hexdigest() != owner.SPEC["programs"][name]:
                    raise ValueError("historical C5 builder preimage differs")
            raw = selected.read_bytes()
            if name in retained:
                row = retained[name]
                if len(raw) != row['bytes'] or hashlib.sha256(raw).hexdigest() != row['sha256']:
                    raise ValueError('historical C5 producer fixture changed: ' + name)
            target = destination / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(raw)
            target.chmod(selected.stat().st_mode & 0o777)
        return destination


@unittest.skipUnless(c5_ubuntu24_uid0_startup_host(),
                     "fixed Ubuntu 24.04 uid0 Python 3.12 startup host absent; no host-startup credit")
class C5InputCases(C5InputFixture, unittest.TestCase):
    def test_actual_selected_normal_startup_and_alias(self):
        """Break caught: synthetic no-site alias or unbound alias ancestry."""
        owner = self.data_owner()
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
        owner = self.data_owner()
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
            root = self.historical_engine(Path(temporary) / 'historical-default')
            legacy = loader(root)
            engine = legacy._Engine()
            self.assertEqual(set(engine.sources), set(outer.PINS))
            with self.assertRaises(ValueError):
                legacy._read("scripts/work-graph-c5-inputs.py")
            # C5 files are absent, yet default capture remains fully usable.
            engine.check()
            with self.assertRaises((ValueError, FileNotFoundError)):
                legacy.create_c5_input_capture(root)
        with tempfile.TemporaryDirectory(prefix='c5-selected-source-') as temporary:
            owner = self.data_owner()
            subject = self.data_subject(owner, Path(temporary) / 'source')
            with mock.patch("subprocess.Popen", side_effect=AssertionError("source capture attempted dispatch")):
                capture = owner.C5Inputs(subject)
                result = capture.acquire()
        self.assertEqual(result["record"]["dispatch_count"], 0)
        self.assertFalse(result["record"]["runtime_complete"])
        self.assertEqual(result["record"]["canonical_acceptance"], "UNQUALIFIED")
        self.assertIn("ZOPFLI_PROVIDER_MISSING", result["record"]["blockers"])
        self.assertEqual(len(result["record"]["producer_contract"]["roles"]), 19)
        self.assertEqual(len(result["record"]["producer_contract"]["release_producers"]), 6)
        self.assertFalse(hasattr(capture, "run"))


class C5InputFixtureRefusalCases(C5InputFixture, unittest.TestCase):
    """Fixture selection cannot repin either production source population."""

    def test_historical_c5_closure_refuses_current_data_module(self):
        with tempfile.TemporaryDirectory(prefix='c5-historical-refusal-') as temporary:
            root = self.historical_engine(Path(temporary) / 'historical')
            owner = loader(root)
            for name in owner._C5_PINS:
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((ROOT / name).read_bytes())
                target.chmod(0o644)
            with self.assertRaisesRegex(ValueError, 'unsupported fixed C5 source: scripts/work-graph-c5-inputs.py'):
                owner._load_c5_owner()

    def test_current105_closure_refuses_historical_prefix(self):
        with tempfile.TemporaryDirectory(prefix='c5-current-refusal-') as temporary:
            root = Path(temporary)
            path = ROOT / 'scripts/load-work-graph-c5-executor.py'
            spec = importlib.util.spec_from_file_location('c5_current_fixture_catalog', path)
            outer = importlib.util.module_from_spec(spec)
            exec(compile(path.read_bytes(), str(path), 'exec'), outer.__dict__)
            copy_c5_closed_source(root, profile=outer.CORRESPONDENCE_PROFILE,
                                  revision=outer.R4_COMPOSED_SOURCE_REVISION)
            historical = self.historical_engine(root / 'historical')
            (root / outer.PREFIX).write_bytes((historical / outer.PREFIX).read_bytes())
            selected = importlib.util.spec_from_file_location('c5_current_fixture_refusal', root / outer.LOADER)
            current = importlib.util.module_from_spec(selected)
            exec(compile((root / outer.LOADER).read_bytes(), str(root / outer.LOADER), 'exec'), current.__dict__)
            with self.assertRaisesRegex(ValueError, 'Unsupported fixed C5 execution member'):
                current._Engine(current.CORRESPONDENCE_PROFILE, source_revision=current.R4_COMPOSED_SOURCE_REVISION)


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
            original_index=48, original_argv=["bash", "tests/reproducible-release-asset.test.sh"]),
            CORRESPONDENCE_PROFILE="FIXED_GENUINE_C5_SHARED_IMAGE_CORRESPONDENCE_20261031_V1",
            Q=types.SimpleNamespace(REPRO_CORRESPONDENCE_PRODUCER_SHA256="550a92a48989a2a9987b3d51c26a3198cf4828aad28fd3ffe8815fea6399019d"))
        def need(value, message):
            if not value: raise ValueError(message)
        namespace.update(correspondence_profile_globals())
        namespace.update(need=need, fixed_task_entropy_device_v1=mock.Mock(return_value={"observed": "real-device-facts"}))
        exec(compile(ast.Module(body=[function], type_ignores=[]), "<actual-entropy-admission>", "exec"), namespace)
        return namespace

    def test_exact_task_program_and_git_only(self):
        n = self.guard()
        source = dict(source=dict(state=dict(files={"tests/reproducible-release-asset.test.sh":
            dict(sha256="a27521758cc71e312052d7eaa7c8b488dbbe2dcc5089d6054be0923455763310")})))
        runtime = dict(files={"/usr/bin/git":dict(sha256="2a8c18fbf43da9f692d75474c72bea9dfd796c260b0f3dfe456376abc3bbd668")})
        self.assertEqual(n["task_kernel_entropy_v1"](source, runtime), {"observed": "real-device-facts"})
        current=copy.deepcopy(source)
        current['source']['state']['files']['tests/reproducible-release-asset.test.sh']['sha256']=n['Q'].REPRO_CORRESPONDENCE_PRODUCER_SHA256
        self.assertEqual(n['task_kernel_entropy_v1'](current,runtime), {'observed':'real-device-facts'})
        prospective=self.guard();prospective['PROFILE']=prospective['CORRESPONDENCE_PROFILE']
        with self.assertRaises(ValueError):prospective['task_kernel_entropy_v1'](source,runtime)
        self.assertEqual(prospective['task_kernel_entropy_v1'](current,runtime), {'observed':'real-device-facts'})
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
        n = dict(os=os, stat=stat, need=need, **correspondence_profile_globals())
        exec(compile(ast.Module(body=functions,type_ignores=[]), "<actual-device-observer>", "exec"), n)
        valid = dict(st_dev=1,st_ino=7,st_mode=stat.S_IFCHR|0o666,st_nlink=1,st_size=0,
                     st_mtime_ns=11,st_ctime_ns=12,st_uid=65534,st_gid=65534,st_rdev=os.makedev(1,9))
        for mutation in (None, "regular", "minor", "owner", "link", "identity", "nodev"):
            first = dict(valid)
            if mutation == "regular": first["st_mode"] = stat.S_IFREG|0o666
            if mutation == "minor": first["st_rdev"] = os.makedev(1,8)
            if mutation == "owner": first["st_uid"] = 0
            path = mock.Mock();path.resolve.return_value = path if mutation != "link" else Path("/other-device")
            second = dict(first)
            if mutation == "identity": second["st_ino"] += 1
            path.lstat.side_effect = [types.SimpleNamespace(**first), types.SimpleNamespace(**second)]
            n["Path"] = mock.Mock(return_value=path)
            n["os"] = types.SimpleNamespace(major=os.major, minor=os.minor, ST_NODEV=os.ST_NODEV,
                statvfs=mock.Mock(return_value=types.SimpleNamespace(f_flag=os.ST_NOSUID | (os.ST_NODEV if mutation=="nodev" else 0))))
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


class C5TaskResourceCases(unittest.TestCase):
    TASK = "FIXED_GENUINE_C5_PRODUCER_EFFECT_SOL_TASK_LINUX_20261029_V1"
    POLICY = dict(schema="implementaudit.c5-task-resource-policy.v1",
        identity="C5_TASK_ORIGINAL48_FILE64_V1", inherited_file_bytes=16*1024**2, file_bytes=64*1024**2)
    def selection(self, profile, policy=None):
        tree = ast.parse((ROOT / "scripts/work-graph-c5-executor.py").read_bytes())
        function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name=="execution_limits_v1")
        n = dict(PROFILE=profile,SPEC={} if policy is None else dict(task_resource_policy=policy),
                 CORRESPONDENCE_PROFILE="FIXED_GENUINE_C5_SHARED_IMAGE_CORRESPONDENCE_20261031_V1")
        def need(value,message):
            if not value: raise ValueError(message)
        n.update(correspondence_profile_globals())
        n["need"] = need
        exec(compile(ast.Module(body=[function],type_ignores=[]),"<actual-task-resource-owner>","exec"),n)
        return n["execution_limits_v1"]

    def test_only_task_increases_one_declared_limit(self):
        inherited = dict(file_bytes=16*1024**2,work_bytes=512*1024**2,scratch_bytes=32*1024**2,
            cpu_seconds=90,wall_seconds=120,address_bytes=1024**3,descriptors=4096,
            stream_bytes=16*1024**2,retained_object_bytes=1024**3,evidence_bytes=2*1024**3)
        original = dict(inherited)
        task = self.selection(self.TASK,dict(self.POLICY))(inherited)
        self.assertEqual(task,dict(inherited,file_bytes=64*1024**2))
        self.assertEqual(inherited,original)
        paired=self.selection('FIXED_GENUINE_C5_SHARED_IMAGE_CORRESPONDENCE_20261031_V1',dict(self.POLICY))(inherited)
        self.assertEqual(paired,task)
        for profile in ("FIXED_GENUINE_C5_PRODUCER_EFFECT_ORIGINAL48_V1",
                        "FIXED_GENUINE_C5_PRODUCER_EFFECT_CURRENT_COMPOSITE_20261027_V1"):
            self.assertEqual(self.selection(profile)(inherited),inherited)
            with self.assertRaises(ValueError):self.selection(profile,dict(self.POLICY))(inherited)

    def test_unreviewed_resource_values_refuse(self):
        inherited = dict(file_bytes=16*1024**2)
        policies = [None,dict(self.POLICY,file_bytes=128*1024**2),dict(self.POLICY,unbounded=True),
                    dict(self.POLICY,identity="arbitrary")]
        for policy in policies:
            with self.subTest(policy=policy),self.assertRaises(ValueError):
                self.selection(self.TASK,policy)(inherited)
        with self.assertRaises(ValueError):self.selection(self.TASK,dict(self.POLICY))(dict(file_bytes=32*1024**2))


class C5PublicStreamingSourceRevisionCases(unittest.TestCase):
    """Explicit public-base source composition; no native session or producer."""
    HISTORY = ROOT / 'test-support/work-graph-c5-profile-history/pro-dg16-public-cost-20261101'
    SOURCE_LOADER = 'scripts/load-work-graph-c5-executor.py'
    EXECUTOR = 'scripts/work-graph-c5-executor.py'
    REVISION = 'DG16_PUBLIC_BASE_STREAMING_OWNED_DIGEST_SOURCE_20261101_V1'
    EXECUTOR_SHA = '5b9d9fea7f67dd3ab3a58ee4ff648ee07c0f3ce9cbf069629f33906c04c6cfcf'
    REVISION_ATTRIBUTE = 'PUBLIC_STREAMING_SOURCE_REVISION'
    QUALIFIER_SHA = 'c090833db1049c5922d78875fab4630ed686e23e56f5aca1926db482457c6c13'

    def module(self, root):
        path = root / self.SOURCE_LOADER
        value = types.ModuleType('public_streaming_source_control')
        value.__file__ = str(path)
        exec(compile(path.read_bytes(), str(path), 'exec'), value.__dict__)
        return value

    def source(self, profile_name='CORRESPONDENCE_PROFILE'):
        owner = self.module(ROOT)
        self.assertEqual(getattr(owner, self.REVISION_ATTRIBUTE, None), self.REVISION,
                         'the public-base streaming tuple must be explicitly supported')
        profile = getattr(owner, profile_name)
        temporary = tempfile.TemporaryDirectory(prefix='c5-public-streaming-')
        self.addCleanup(temporary.cleanup)
        source = Path(temporary.name)
        for name in (owner.LOADER, *owner._selection(profile, self.REVISION)[0]):
            path = source / name
            path.parent.mkdir(parents=True, exist_ok=True)
            history = ROOT / 'test-support/work-graph-c5-profile-history/pre-current105-qualifier-20261104'
            retained = ROOT / 'test-support/work-graph-c5-profile-history/pre-r4-fresh-canary-20261104' / name
            selected = retained if retained.is_file() and name != owner.LOADER else ROOT / name
            if name == owner.QUALIFIER and self.REVISION_ATTRIBUTE == 'PUBLIC_STREAMING_SOURCE_REVISION':
                selected = history / name
            if name == owner.COMPILER:
                compiler_history = ROOT / 'test-support/work-graph-c5-profile-history/pre-composed-compiler-20261104'
                manifest = json.loads((compiler_history / 'MANIFEST.json').read_bytes())
                row = next(row for row in manifest['files'] if row['path'] == name)
                selected = compiler_history / name
                retained = selected.read_bytes()
                self.assertEqual((len(retained), hashlib.sha256(retained).hexdigest()),
                                 (row['bytes'], row['sha256']))
                self.assertEqual(row['sha256'], owner._selection(profile, self.REVISION)[0][name])
            path.write_bytes(selected.read_bytes())
            path.chmod(0o644)
        return self.module(source), source, profile

    def candidate(self):
        owner, source, profile = self.source()
        captured = owner._Engine(profile, source_revision=self.REVISION)
        return owner, source, profile, captured, captured.load()

    def owned(self, engine, raw):
        temporary = tempfile.TemporaryDirectory(prefix='c5-public-owned-')
        self.addCleanup(temporary.cleanup)
        root = Path(temporary.name)
        path = root / 'owned.bin'
        path.write_bytes(raw)
        path.chmod(0o400)
        row = dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(),
                   identity=engine.stamp(path.stat()), mode=0o400)
        actor = types.SimpleNamespace(closed=False, owner=os.getpid(), output=root,
            output_anchor=engine.anchor(root.stat()), owned={'owned.bin': row},
            sealed={}, stage=None, retained_directories=None)
        return actor, path, row

    def test_exact_public_tuple_preserves_compiler_qualifier_and_budget(self):
        for profile_name in ('CURRENT_PROFILE', 'CORRESPONDENCE_PROFILE'):
            with self.subTest(profile=profile_name):
                owner, _, profile = self.source(profile_name)
                captured = owner._Engine(profile, source_revision=self.REVISION)
                engine = captured.load()
                self.assertEqual(captured.pins[self.EXECUTOR], self.EXECUTOR_SHA)
                self.assertEqual(captured.pins[owner.COMPILER],
                    '25f2c24645cc65ed4b9bfbd70bb2d0ce26eb6accc51de0af0df06b3bdff5b627')
                self.assertEqual(captured.pins[owner.QUALIFIER], self.QUALIFIER_SHA)
                self.assertEqual(hashlib.sha256(engine.Q.LOADED_COMPILER).hexdigest(),
                                 captured.pins[owner.COMPILER])
                self.assertEqual(engine.PROFILE, profile)
                self.assertEqual(engine.LIMITS['wall_seconds'], 120)
                captured.check()

    def test_historical_maps_buffers_and_default_refusal_remain_exact(self):
        owner, source, profile, _, _ = self.candidate()
        old = self.module(self.HISTORY)
        for name in ('PINS', 'CURRENT_PINS', 'TASK_PINS', 'CORRESPONDENCE_PINS'):
            self.assertEqual(dict(getattr(owner, name)), dict(getattr(old, name)), name)
        manifest = json.loads((self.HISTORY / 'MANIFEST.json').read_bytes())
        for row in manifest['files']:
            raw = (self.HISTORY / row['path']).read_bytes()
            self.assertEqual((len(raw), hashlib.sha256(raw).hexdigest()),
                             (row['bytes'], row['sha256']))
        with self.assertRaisesRegex(ValueError, 'Unsupported fixed C5 execution member'):
            owner._Engine(profile)
        for name in (owner.LOADER, owner.EXECUTOR):
            (source / name).write_bytes((self.HISTORY / name).read_bytes())
        qualifier_history = ROOT / 'test-support/work-graph-c5-profile-history/pre-current105-qualifier-20261104'
        manifest = json.loads((qualifier_history / 'MANIFEST.json').read_bytes())
        for row in manifest['files']:
            raw = (qualifier_history / row['path']).read_bytes()
            self.assertEqual((len(raw), hashlib.sha256(raw).hexdigest()), (row['bytes'], row['sha256']))
            (source / row['path']).write_bytes(raw)
        historical = self.module(source)
        self.assertEqual(historical._Engine(profile).load().PROFILE, profile)

    def test_unknown_mixed_missing_and_changed_source_refuse_before_loading(self):
        owner, _, profile, _, _ = self.candidate()
        for revision in ('unknown', {}, 1, 'DG16_STREAMING_OWNED_DIGEST_SOURCE_20261101_V1'):
            with self.subTest(revision=revision), self.assertRaisesRegex(ValueError, 'source revision'):
                owner._Engine(profile, source_revision=revision)
        for wrong in (owner.PROFILE, owner.TASK_PROFILE, None):
            with self.subTest(profile=wrong), self.assertRaisesRegex(ValueError, 'source revision'):
                owner._Engine(wrong, source_revision=self.REVISION)
        for change in ('mixed', 'missing', 'changed'):
            with self.subTest(change=change):
                selected, source, profile = self.source()
                path = source / selected.EXECUTOR
                if change == 'mixed':
                    path.write_bytes((self.HISTORY / selected.EXECUTOR).read_bytes())
                elif change == 'missing':
                    path.unlink()
                else:
                    path.write_bytes(b"raise AssertionError('unbound executor ran')\n")
                with self.assertRaises((ValueError, OSError)):
                    selected._Engine(profile, source_revision=self.REVISION)

    def test_captured_source_content_and_identity_drift_refuse(self):
        for change in ('content', 'replacement', 'ancestor'):
            with self.subTest(change=change):
                owner, source, _, captured, _ = self.candidate()
                path = source / owner.EXECUTOR
                if change == 'content':
                    path.write_bytes(path.read_bytes() + b'\n')
                elif change == 'replacement':
                    raw = path.read_bytes()
                    held = os.open(path, os.O_RDONLY)
                    self.addCleanup(os.close, held)
                    path.unlink()
                    path.write_bytes(raw)
                else:
                    target = source / 'old-scripts'
                    path.parent.rename(target)
                    shutil.copytree(target, source / 'scripts')
                with self.assertRaisesRegex(ValueError, 'source|current|ancestor'):
                    captured.check()

    def test_fresh_bytes_chunk_boundaries_short_reads_and_metadata_refusals(self):
        _, _, _, _, engine = self.candidate()
        for size in (0, 1, 1024**2-1, 1024**2, 1024**2+1):
            raw = (b'fresh\x00data' * (size // 10 + 1))[:size]
            actor, path, _ = self.owned(engine, raw)
            self.assertEqual(engine.read_owned_digest(path, size)['sha256'], hashlib.sha256(raw).hexdigest())
            engine.GenuineC5Session._check_owned(actor)
        _, path, _ = self.owned(engine, b'abc' * 71)
        real_read = os.read
        with mock.patch('os.read', side_effect=lambda fd, size: real_read(fd, min(size, 7))):
            self.assertEqual(engine.read_owned_digest(path, 213)['sha256'], hashlib.sha256(b'abc'*71).hexdigest())
        with self.assertRaisesRegex(ValueError, 'bound'):
            engine.read_owned_digest(path, 212)
        path.chmod(0o600)
        os.setxattr(path, 'user.c5_public_streaming', b'refuse')
        path.chmod(0o400)
        with self.assertRaisesRegex(ValueError, 'metadata'):
            engine.read_owned_digest(path, 213)

    def test_real_hash_length_mode_identity_and_link_changes_refuse(self):
        _, _, _, _, engine = self.candidate()
        for change in ('hash', 'growth', 'shrink', 'mode', 'identity', 'link'):
            with self.subTest(change=change):
                actor, path, row = self.owned(engine, b'fresh owned bytes')
                if change == 'hash':
                    row['sha256'] = '0' * 64
                elif change in ('growth', 'shrink'):
                    path.chmod(0o600)
                    raw = path.read_bytes()
                    path.write_bytes(raw+b'x' if change == 'growth' else raw[:-1])
                    path.chmod(0o400)
                    row['identity'] = engine.stamp(path.stat())
                elif change == 'mode':
                    path.chmod(0o600)
                elif change == 'identity':
                    raw = path.read_bytes()
                    held = os.open(path, os.O_RDONLY)
                    self.addCleanup(os.close, held)
                    path.unlink()
                    path.write_bytes(raw)
                    path.chmod(0o400)
                else:
                    os.link(path, path.parent / 'alias')
                with self.assertRaises((ValueError, OSError)):
                    engine.GenuineC5Session._check_owned(actor)

    def test_large_fresh_input_keeps_bounded_allocation(self):
        import tracemalloc
        _, _, _, _, engine = self.candidate()
        actor, _, _ = self.owned(engine, b'x' * (16 * 1024**2 + 1))
        tracemalloc.start()
        try:
            engine.GenuineC5Session._check_owned(actor)
            _, peak = tracemalloc.get_traced_memory()
        finally:
            tracemalloc.stop()
        self.assertLess(peak, 4 * 1024**2)



class C5Current105SourceRevisionCases(C5PublicStreamingSourceRevisionCases):
    REVISION = 'DG16_CURRENT105_CLOSED_RUNTIME_SOURCE_20261104_V1'
    REVISION_ATTRIBUTE = 'CURRENT105_SOURCE_REVISION'
    QUALIFIER_SHA = '0f148dc343a955dde59c7b6a22d89d5885c920cd4c6ceeba455cec80b88adc23'

    def test_revision_qualifier_hybrid_refuses_and_prior_revision_remains_exact(self):
        owner, source, profile = self.source()
        self.assertEqual(owner.PUBLIC_STREAMING_PINS[profile][owner.QUALIFIER],
                         'c090833db1049c5922d78875fab4630ed686e23e56f5aca1926db482457c6c13')
        with self.assertRaisesRegex(ValueError, 'Unsupported fixed C5 execution member'):
            owner._Engine(profile, source_revision=owner.PUBLIC_STREAMING_SOURCE_REVISION)
        history = ROOT / 'test-support/work-graph-c5-profile-history/pre-current105-qualifier-20261104'
        (source / owner.QUALIFIER).write_bytes((history / owner.QUALIFIER).read_bytes())
        with self.assertRaisesRegex(ValueError, 'Unsupported fixed C5 execution member'):
            owner._Engine(profile, source_revision=self.REVISION)
        self.assertEqual(owner._Engine(profile, source_revision=owner.PUBLIC_STREAMING_SOURCE_REVISION).load().PROFILE,
                         profile)


@unittest.skipUnless(sys.platform.startswith('linux') and hasattr(os,'pidfd_open'), 'Linux live child custody required')
class C5CorrespondenceLiveCases(unittest.TestCase):
    """Actual tiny C5 channels/children; no acquired-image or original claim."""
    def source_contract(self):
        path=ROOT/'scripts/load-work-graph-c5-executor.py';tree=ast.parse(path.read_bytes())
        assignment=next(n for n in tree.body if isinstance(n,ast.Assign) and
            any(isinstance(t,ast.Name) and t.id=='CORRESPONDENCE_PINS' for t in n.targets))
        pins=ast.literal_eval(assignment.value.args[0])
        temporary=tempfile.TemporaryDirectory(prefix='c5-correspondence-contract-')
        self.addCleanup(temporary.cleanup);source=Path(temporary.name)
        copy_c5_closed_source(source, current_builder=True)
        spec=importlib.util.spec_from_file_location('correspondence_contract_source',source/'scripts/load-work-graph-c5-executor.py')
        owner=importlib.util.module_from_spec(spec);spec.loader.exec_module(owner)
        engine=owner._Engine(owner.R4_BUILD_CACHE_PROFILE,source_revision=owner.R4_BUILD_CACHE_SOURCE_REVISION).load()
        names=set(engine.B.SPEC['payload_sources'])|set(engine.B.SPEC['programs'])
        names|={p.relative_to(ROOT).as_posix() for p in (ROOT/'skills/implementaudit').rglob('*') if p.is_file()}
        state=dict(files={name:dict(sha256=hashlib.sha256((ROOT/name).read_bytes()).hexdigest()) for name in names})
        return owner,engine,state

    def test_correspondence_actual_source_contract_uses_separate_current_base(self):
        owner,engine,state=self.source_contract()
        try:contract=engine.B._producer_contract(state)
        except ValueError as error:self.fail('Actual source producer contract refused: '+str(error))
        self.assertEqual(len(contract['roles']),19)
        self.assertEqual(contract['original_index'],48)
        self.assertEqual(set(contract['selected_programs']),{'scripts/build-release-asset.sh',
            'scripts/check-package-contract.sh','scripts/package-contract.py',
            'scripts/repro-event-capture.py','scripts/write-release-checksums.sh',
            'tests/reproducible-release-asset.test.sh'})
        self.assertNotEqual(owner.R4_BUILD_CACHE_BASE_SELECTION,owner.TASK_BASE_SELECTION)
        self.assertEqual(engine.SPEC['selection_origins']['base_actual_member'],owner.R4_BUILD_CACHE_BASE_SELECTION)

    def test_correspondence_stale_producer_field_refuses(self):
        owner,engine,state=self.source_contract()
        try:engine.B._producer_contract(state)
        except ValueError as error:self.fail('Positive source contract refused before mutation: '+str(error))
        historical=json.loads((ROOT/'fixtures/work-graph-c5-inputs/execution-sol-task-python312.json').read_bytes())
        for name in ('scripts/repro-event-capture.py','tests/reproducible-release-asset.test.sh'):
            changed=copy.deepcopy(state);changed['files'][name]['sha256']=historical['programs'][name]
            self.assertNotEqual(changed['files'][name]['sha256'],state['files'][name]['sha256'])
            with self.subTest(name=name),self.assertRaisesRegex(ValueError,'producer source differs'):
                engine.B._producer_contract(changed)

    def test_closed_shared_profile_buffers_and_source_drift_refuse(self):
        path=ROOT/'scripts/load-work-graph-c5-executor.py';tree=ast.parse(path.read_bytes())
        assignment=next(n for n in tree.body if isinstance(n,ast.Assign) and
            any(isinstance(t,ast.Name) and t.id=='CORRESPONDENCE_PINS' for t in n.targets))
        pins=ast.literal_eval(assignment.value.args[0])
        with tempfile.TemporaryDirectory(prefix='c5-correspondence-source-') as temporary:
            source=Path(temporary)
            copy_c5_closed_source(source)
            spec=importlib.util.spec_from_file_location('closed_current_pair_source',source/'scripts/load-work-graph-c5-executor.py')
            owner=importlib.util.module_from_spec(spec);spec.loader.exec_module(owner)
            captured=owner._Engine(owner.CORRESPONDENCE_PROFILE,source_revision=owner.R4_COMPOSED_SOURCE_REVISION);engine=captured.load()
            self.assertEqual(engine.CORRESPONDENCE_POLICY['runs'],2)
            self.assertEqual(engine.LIMITS['wall_seconds'],120)
            self.assertEqual(engine.LIMITS['file_bytes'],64*1024**2)
            captured.check()
            with self.assertRaises(ValueError):owner._Engine('unknown')
            member=source/'scripts/repro-event-capture.py';member.write_bytes(member.read_bytes()+b'\n')
            with self.assertRaisesRegex(ValueError,'source|current'):captured.check()

    def test_two_actual_profiles_share_one_wait_and_refuse_copy_or_window_omission(self):
        fixture_spec=importlib.util.spec_from_file_location('existing_c5_fixture',ROOT/'tests/work-graph-repro-events-cases.py')
        fixtures=importlib.util.module_from_spec(fixture_spec);fixture_spec.loader.exec_module(fixtures)
        fixture=fixtures.Fixture();self.addCleanup(fixture.clean)
        source=fixture.base/'closed-owner';source.mkdir()
        loader_path=ROOT/'scripts/load-work-graph-c5-executor.py'
        tree=ast.parse(loader_path.read_bytes())
        assignment=next(n for n in tree.body if isinstance(n,ast.Assign) and
            any(isinstance(t,ast.Name) and t.id=='CORRESPONDENCE_PINS' for t in n.targets))
        pins=ast.literal_eval(assignment.value.args[0])
        copy_c5_closed_source(source)
        selected=importlib.util.spec_from_file_location('actual_closed_correspondence_owner',source/'scripts/load-work-graph-c5-executor.py')
        owner=importlib.util.module_from_spec(selected);selected.loader.exec_module(owner)
        engine=owner._Engine(owner.CORRESPONDENCE_PROFILE,source_revision=owner.R4_COMPOSED_SOURCE_REVISION).load()
        self.assertEqual(engine.PROFILE,owner.CORRESPONDENCE_PROFILE)
        with self.assertRaisesRegex(ValueError,'Unknown fixed C5 execution profile'):
            owner._Engine('unknown')
        work=fixture.base/'private-work';work.mkdir()
        executor_tree=ast.parse((ROOT/'scripts/work-graph-c5-executor.py').read_bytes())
        functions=[n for n in executor_tree.body if isinstance(n,ast.FunctionDef) and n.name in
            ('need','encode','sha','send','read_fd','bootstrap_correspondence_pair')]
        script=fixture.base/'actual-source-supervisor.py'
        script.write_text('import os,json,sys,hashlib,subprocess,time\nfrom pathlib import Path\n'+
            'SOURCE_MOUNT='+repr(str(fixture.repo))+'\nWORK_MOUNT='+repr(str(work))+'\nMAX_HEADER=4194304\n'+
            'CORRESPONDENCE_PROFILE='+repr(engine.CORRESPONDENCE_PROFILE)+'\nCORRESPONDENCE_POLICY='+repr(engine.CORRESPONDENCE_POLICY)+'\n'+
            ''.join(key+'='+repr(value)+'\n' for key,value in correspondence_profile_globals().items())+
            ast.unparse(ast.Module(body=functions,type_ignores=[]))+'\n'+
            'bootstrap_correspondence_pair(dict(scope=CORRESPONDENCE_PROFILE,correspondence_pair=CORRESPONDENCE_POLICY),int(sys.argv[1]))\n')
        parent,child=socket.socketpair();self.addCleanup(parent.close);self.addCleanup(child.close)
        python_bin=fixture.base/'python-bin';python_bin.mkdir()
        (python_bin/'python').symlink_to(Path(sys.executable).resolve(strict=True))
        env=dict(fixture.env,PATH=str(python_bin)+':/usr/bin:/bin',TMPDIR=str(work),
                 R0035_REPRO_EVENT_CAPTURE_DIR=str(work/'capture'),
                 R0035_C5_CORRESPONDENCE_CAPTURE='FINITE_C5_ROLE_CORRESPONDENCE_V1',
                 R0035_C5_LIVE_GATE_FD=str(child.fileno()),C5_CASE_PROGRESS_LABELS='1')
        stdout=(fixture.base/'outer-stdout').open('wb');stderr=(fixture.base/'outer-stderr').open('wb')
        process=subprocess.Popen([sys.executable,'-B',str(script),str(child.fileno())],cwd=fixture.repo,
            env=env,pass_fds=(child.fileno(),),start_new_session=True,stdout=stdout,stderr=stderr)
        child.close()
        source_identity=dict(source_commit=fixture.commit,
            source_tree=subprocess.check_output(['git','-C',str(fixture.repo),'rev-parse','HEAD^{tree}']).decode().strip())
        for label,name in (('producer',engine.G.E.PRODUCER),('capture_owner',engine.G.E.OWNER)):
            path=fixture.repo/name;raw=path.read_bytes()
            source_identity[label]=dict(path=name,bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),mode=stat.S_IMODE(path.stat().st_mode))
        executables={}
        for name in ('bash','git','cmp','python'):
            path=Path(shutil.which(name,path=env['PATH'])).resolve();executables[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
        gates=[];outcomes=[]
        try:
            for ordinal in range(2):
                gate=engine.G.LiveC5Gate(fixture.base/('gate-'+str(ordinal)),process,parent,
                    expected_source=source_identity,expected_context=dict(repository=str(fixture.repo),cwd=str(fixture.repo),
                    python_command='python',work_parent=str(work)),executable_inputs=executables,
                    acquisition_digest='0'*64,require_current=lambda:None,wall_seconds=20,correspondence=True)
                gates.append(gate)
                while not gate._finished:gate.handle_next()
                count=int.from_bytes(gate._read_exact(8),'big');outcome=json.loads(gate._read_exact(count));outcomes.append(outcome)
                self.assertEqual((outcome['ordinal'],outcome['exit_code']),(ordinal,0))
                reply=engine.encode(dict(schema='implementaudit.c5-pair-child-release.v1',
                    image_sha256=outcome['image_sha256'],ordinal=ordinal,accepted=True))
                parent.sendall(len(reply).to_bytes(8,'big')+reply)
            first=gates[0].finalize();second=gates[1].finalize(shared_wait_owner=gates[0])
            self.assertEqual(first['actual_outer_process'],second['actual_outer_process'])
            self.assertNotEqual(outcomes[0]['actual_pid'],outcomes[1]['actual_pid'])
            self.assertEqual([g._event_count for g in gates],[19,19])
            comparison=engine.Q.compare_c5_correspondence(gates[0].capture,gates[1].capture,None)
            self.assertTrue(comparison['equivalent']);self.assertFalse(comparison['raw_observables_equal'])
            target=gates[1].capture/'allocations/18-after.json';row=json.loads(target.read_bytes())
            row['members'].remove('checkout-a');target.write_bytes(engine.G.E.canonical(row))
            with self.assertRaises(engine.Q.WG.WorkGraphError):
                engine.Q.compare_c5_correspondence(gates[0].capture,gates[1].capture,None)
        finally:
            for gate in reversed(gates):
                if not gate._reaped and any(g._reaped for g in gates):
                    peer=next(g for g in gates if g._reaped);gate._reaped=True;gate._wait_result=dict(peer._wait_result)
                gate.close()
            if process.returncode is None:process.kill();process.wait(timeout=5)
            stdout.close();stderr.close()

    def test_failed_or_unreleased_first_actual_child_never_starts_suffix(self):
        tree=ast.parse((ROOT/'scripts/work-graph-c5-executor.py').read_bytes())
        functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in
            ('need','encode','sha','send','read_fd','bootstrap_correspondence_pair')]
        selection=json.loads((ROOT/'fixtures/work-graph-c5-inputs/genuine-correspondence-execution-profile.json').read_bytes())
        for disposition in ('failed','unreleased'):
            with self.subTest(disposition=disposition),tempfile.TemporaryDirectory(prefix='c5-pair-stop-') as temporary:
                base=Path(temporary);source=base/'source';(source/'tests').mkdir(parents=True);work=base/'work';work.mkdir()
                script=source/'tests/reproducible-release-asset.test.sh'
                script.write_text("printf 'started\\n' >> starts\nexit "+('47' if disposition=='failed' else '0')+'\n')
                actor=base/'source-supervisor.py'
                actor.write_text('import os,json,sys,hashlib,subprocess,time\nfrom pathlib import Path\n'+
                    'SOURCE_MOUNT='+repr(str(source))+'\nWORK_MOUNT='+repr(str(work))+'\nMAX_HEADER=4194304\n'+
                    'CORRESPONDENCE_PROFILE='+repr(selection['profile'])+'\nCORRESPONDENCE_POLICY='+repr(selection['correspondence_pair'])+'\n'+
                    ''.join(key+'='+repr(value)+'\n' for key,value in correspondence_profile_globals().items())+
            ast.unparse(ast.Module(body=functions,type_ignores=[]))+'\n'+
                    'bootstrap_correspondence_pair(dict(scope=CORRESPONDENCE_PROFILE,correspondence_pair=CORRESPONDENCE_POLICY),int(sys.argv[1]))\n')
                parent,child=socket.socketpair();parent.settimeout(10)
                with (base/'stderr').open('wb') as errors:
                    process=subprocess.Popen([sys.executable,'-B',str(actor),str(child.fileno())],
                        pass_fds=(child.fileno(),),stdout=subprocess.DEVNULL,stderr=errors)
                    child.close()
                    def receive(count):
                        result=b''
                        while len(result)<count:
                            chunk=parent.recv(count-len(result));self.assertTrue(chunk);result+=chunk
                        return result
                    try:
                        count=int.from_bytes(receive(8),'big');outcome=json.loads(receive(count))
                        self.assertEqual(outcome['exit_code'],47 if disposition=='failed' else 0)
                        parent.close()  # Missing continuation is never success.
                        self.assertNotEqual(process.wait(timeout=10),0)
                        self.assertEqual((source/'starts').read_text().splitlines(),['started'])
                        self.assertEqual(json.loads((work/'pair-processes/0.json').read_bytes()),outcome)
                        self.assertFalse((work/'pair-processes/1.json').exists())
                    finally:
                        parent.close()
                        if process.poll() is None:process.kill();process.wait(timeout=5)

    def test_pre_event_abort_retains_actual_first_clone_exit(self):
        """One failed clone/control only; not an original or acquired-image pair."""
        selected=importlib.util.spec_from_file_location('c5_abort_fixture',ROOT/'tests/work-graph-repro-events-cases.py')
        fixtures=importlib.util.module_from_spec(selected);selected.loader.exec_module(fixtures)
        fixture=fixtures.Fixture();self.addCleanup(fixture.clean)
        source=fixture.base/'closed-owner';source.mkdir()
        tree=ast.parse((ROOT/'scripts/load-work-graph-c5-executor.py').read_bytes())
        node=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='CORRESPONDENCE_PINS' for t in n.targets))
        copy_c5_closed_source(source)
        spec=importlib.util.spec_from_file_location('actual_abort_source_owner',source/'scripts/load-work-graph-c5-executor.py')
        owner=importlib.util.module_from_spec(spec);spec.loader.exec_module(owner)
        engine=owner._Engine(owner.CORRESPONDENCE_PROFILE,source_revision=owner.R4_COMPOSED_SOURCE_REVISION).load()
        source_tree=subprocess.check_output(['git','-C',str(fixture.repo),'rev-parse','HEAD^{tree}']).decode().strip()
        producer=fixture.repo/'tests/reproducible-release-asset.test.sh'
        raw=producer.read_text().replace('for lane in a b; do\n',
            'mv "$repo_root/.git" "$repo_root/.git-unavailable"\nfor lane in a b; do\n',1)
        producer.write_text(raw)
        expected=dict(source_commit=fixture.commit,source_tree=source_tree)
        for label,name in (('producer',engine.G.E.PRODUCER),('capture_owner',engine.G.E.OWNER)):
            path=fixture.repo/name;data=path.read_bytes();expected[label]=dict(path=name,bytes=len(data),sha256=hashlib.sha256(data).hexdigest(),mode=stat.S_IMODE(path.stat().st_mode))
        work=fixture.base/'private-work';work.mkdir()
        tree=ast.parse((ROOT/'scripts/work-graph-c5-executor.py').read_bytes())
        functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ('need','encode','sha','send','read_fd','bootstrap_correspondence_pair')]
        script=fixture.base/'abort-supervisor.py'
        script.write_text('import os,json,sys,hashlib,subprocess,time\nfrom pathlib import Path\n'+
            'SOURCE_MOUNT='+repr(str(fixture.repo))+'\nWORK_MOUNT='+repr(str(work))+'\nMAX_HEADER=4194304\n'+
            'CORRESPONDENCE_PROFILE='+repr(engine.CORRESPONDENCE_PROFILE)+'\nCORRESPONDENCE_POLICY='+repr(engine.CORRESPONDENCE_POLICY)+'\n'+
            ''.join(key+'='+repr(value)+'\n' for key,value in correspondence_profile_globals().items())+
            ast.unparse(ast.Module(body=functions,type_ignores=[]))+'\n'+
            'bootstrap_correspondence_pair(dict(scope=CORRESPONDENCE_PROFILE,correspondence_pair=CORRESPONDENCE_POLICY),int(sys.argv[1]))\n')
        parent,child=socket.socketpair()
        python_bin=fixture.base/'python-bin';python_bin.mkdir()
        (python_bin/'python').symlink_to(Path(sys.executable).resolve(strict=True))
        env=dict(fixture.env,PATH=str(python_bin)+':/usr/bin:/bin',TMPDIR=str(work),
            R0035_REPRO_EVENT_CAPTURE_DIR=str(work/'capture'),
            R0035_C5_CORRESPONDENCE_CAPTURE='FINITE_C5_ROLE_CORRESPONDENCE_V1',R0035_C5_LIVE_GATE_FD=str(child.fileno()))
        with (fixture.base/'outer-stderr').open('wb') as errors:
            process=subprocess.Popen([sys.executable,'-B',str(script),str(child.fileno())],cwd=fixture.repo,env=env,
                pass_fds=(child.fileno(),),start_new_session=True,stdout=subprocess.DEVNULL,stderr=errors)
            child.close();gate=None
            try:
                gate=engine.G.LiveC5Gate(fixture.base/'aborted-live',process,parent,expected_source=expected,
                    expected_context=dict(repository=str(fixture.repo),cwd=str(fixture.repo),python_command='python',work_parent=str(work)),
                    executable_inputs={},acquisition_digest='0'*64,require_current=lambda:None,wall_seconds=20,correspondence=True)
                self.assertEqual(gate.handle_next()['phase'],'INIT')
                with self.assertRaisesRegex(engine.G.LiveGateError,'aborted'):
                    gate.handle_next()
                self.assertEqual(json.loads((gate.capture/'copy-processes/a-0.json').read_bytes())['exit_code'],128)
                self.assertEqual(json.loads((gate.output/'original-child-abort.json').read_bytes())['exit_code'],128)
                self.assertEqual(gate._event_count,0)
                self.assertFalse((work/'pair-processes/1.json').exists())
            finally:
                if gate is not None:gate.close()
                parent.close()
                if process.returncode is None:process.kill();process.wait(timeout=5)


class C5ComposedSourceRevisionCases(unittest.TestCase):
    """Exact shared-repair source selection; never acquires or launches C5."""
    REVISION = 'DG16_CURRENT105_COMPOSED_CONTINUITY_SOURCE_20261104_V2'
    COMPILER_SHA = 'bce6f3bad3a98f850cb5d30e1df21ca8da237ba20609d49a609cccef1a81f21e'
    OLD_COMPILER_SHA = '25f2c24645cc65ed4b9bfbd70bb2d0ce26eb6accc51de0af0df06b3bdff5b627'
    HISTORY = ROOT / 'test-support/work-graph-c5-profile-history/pre-composed-compiler-20261104'

    def module(self, root):
        path = root / 'scripts/load-work-graph-c5-executor.py'
        value = types.ModuleType('c5_composed_source_control')
        value.__file__ = str(path)
        exec(compile(path.read_bytes(), str(path), 'exec'), value.__dict__)
        return value

    def source(self, profile_name='CORRESPONDENCE_PROFILE'):
        current = self.module(ROOT)
        profile = getattr(current, profile_name)
        temporary = tempfile.TemporaryDirectory(prefix='c5-composed-source-')
        self.addCleanup(temporary.cleanup)
        source = Path(temporary.name)
        # Identical member population, independently selected through the old
        # revision. The behavior under test must admit the exact new bytes.
        for name in (current.LOADER, *current._selection(profile, current.CURRENT105_SOURCE_REVISION)[0]):
            target = source / name
            target.parent.mkdir(parents=True, exist_ok=True)
            retained = ROOT / 'test-support/work-graph-c5-profile-history/pre-r4-fresh-canary-20261104' / name
            selected = retained if retained.is_file() and name != current.LOADER else ROOT / name
            target.write_bytes(selected.read_bytes())
            target.chmod(0o644)
        return self.module(source), source, profile

    def test_exact_composed_source_loads_two_runtime_profiles_without_dispatch(self):
        for profile_name in ('CURRENT_PROFILE', 'CORRESPONDENCE_PROFILE'):
            with self.subTest(profile=profile_name):
                owner, _, profile = self.source(profile_name)
                captured = owner._Engine(profile, source_revision=self.REVISION)
                engine = captured.load()
                expected = dict(owner.CURRENT105_PINS[profile])
                expected[owner.COMPILER] = self.COMPILER_SHA
                self.assertEqual(dict(captured.pins), expected)
                self.assertEqual(owner._selection(profile, self.REVISION)[1:],
                                 owner._selection(profile, owner.CURRENT105_SOURCE_REVISION)[1:])
                self.assertEqual(hashlib.sha256(engine.Q.LOADED_COMPILER).hexdigest(), self.COMPILER_SHA)
                self.assertEqual(engine.PROFILE, profile)
                self.assertEqual(engine.LIMITS['wall_seconds'], 120)
                captured.check()

    def test_new_factories_reach_existing_metadata_gate_without_creating_session(self):
        for profile_name, factory in (
            ('CURRENT_PROFILE', 'create_current105_composed_source_current_composite_c5_session_v2'),
            ('CORRESPONDENCE_PROFILE', 'create_current105_composed_source_correspondence_c5_session_v2')):
            with self.subTest(factory=factory):
                owner, source, _ = self.source(profile_name)
                output = source.parent / (source.name + '-not-created')
                self.assertFalse(output.exists())
                with self.assertRaisesRegex(ValueError, 'C5 post-commit comparison metadata is malformed'):
                    getattr(owner, factory)(source, output, expected_source={})
                self.assertFalse(output.exists())

    def test_old_revisions_refuse_new_compiler_before_loading(self):
        owner, _, profile = self.source()
        for revision in (owner.PUBLIC_STREAMING_SOURCE_REVISION, owner.CURRENT105_SOURCE_REVISION):
            with self.subTest(revision=revision):
                with self.assertRaisesRegex(ValueError, 'Unsupported fixed C5 execution member: ' + owner.COMPILER):
                    owner._Engine(profile, source_revision=revision)

    def test_exact_retained_compiler_keeps_both_old_revisions_executable(self):
        owner, source, profile = self.source()
        manifest = json.loads((self.HISTORY / 'MANIFEST.json').read_bytes())
        self.assertEqual(len(manifest['files']), 1)
        row = manifest['files'][0]
        self.assertEqual(row['path'], owner.COMPILER)
        raw = (self.HISTORY / row['path']).read_bytes()
        self.assertEqual((len(raw), hashlib.sha256(raw).hexdigest()), (261851, self.OLD_COMPILER_SHA))
        self.assertEqual((row['bytes'], row['sha256']), (len(raw), self.OLD_COMPILER_SHA))
        self.assertEqual(owner.CURRENT105_PINS[profile][owner.COMPILER], self.OLD_COMPILER_SHA)
        (source / owner.COMPILER).write_bytes(raw)
        old = owner._Engine(profile, source_revision=owner.CURRENT105_SOURCE_REVISION).load()
        self.assertEqual(hashlib.sha256(old.Q.LOADED_COMPILER).hexdigest(), self.OLD_COMPILER_SHA)
        with self.assertRaisesRegex(ValueError, 'Unsupported fixed C5 execution member: ' + owner.COMPILER):
            owner._Engine(profile, source_revision=self.REVISION)
        history = ROOT / 'test-support/work-graph-c5-profile-history/pre-current105-qualifier-20261104'
        (source / owner.QUALIFIER).write_bytes((history / owner.QUALIFIER).read_bytes())
        prior = owner._Engine(profile, source_revision=owner.PUBLIC_STREAMING_SOURCE_REVISION).load()
        self.assertEqual(hashlib.sha256(prior.Q.LOADED_COMPILER).hexdigest(), self.OLD_COMPILER_SHA)
        self.assertEqual(prior.PROFILE, profile)

    def test_unknown_revision_profile_and_unbound_compiler_fail_closed(self):
        owner, source, profile = self.source()
        for revision in ('unknown', {}, 1, self.REVISION.replace('_V2', '_V1')):
            with self.subTest(revision=revision), self.assertRaisesRegex(ValueError, 'source revision'):
                owner._Engine(profile, source_revision=revision)
        for wrong in (owner.PROFILE, owner.TASK_PROFILE, None):
            with self.subTest(profile=wrong), self.assertRaisesRegex(ValueError, 'source revision'):
                owner._Engine(wrong, source_revision=self.REVISION)
        (source / owner.COMPILER).write_bytes(b"raise AssertionError('unbound compiler executed')\n")
        with self.assertRaisesRegex(ValueError, 'Unsupported fixed C5 execution member: ' + owner.COMPILER):
            owner._Engine(profile, source_revision=self.REVISION)

    def test_captured_composed_compiler_identity_drift_refuses(self):
        owner, source, profile = self.source()
        captured = owner._Engine(profile, source_revision=self.REVISION)
        path = source / owner.COMPILER
        replacement = path.with_name('replacement.py')
        replacement.write_bytes(path.read_bytes())
        replacement.chmod(0o644)
        replacement.replace(path)
        with self.assertRaises(ValueError):
            captured.load()


class C5CurrentnessWitnessCases(unittest.TestCase):
    def owner_method(self):
        tree=ast.parse((ROOT / "scripts/work-graph-c5-executor.py").read_bytes())
        owner=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=="GenuineC5Session")
        method=next(n for n in owner.body if isinstance(n,ast.FunctionDef) and n.name=="_same_inputs")
        def need(value,message):
            if not value:raise ValueError(message)
        n=dict(need=need,encode=lambda value:json.dumps(value,sort_keys=True).encode())
        exec(compile(ast.Module(body=[method],type_ignores=[]),"<actual-closing-currentness>","exec"),n)
        return n["_same_inputs"]

    def test_changed_observation_is_retained_and_still_refused(self):
        before=dict(observation=dict(physical_input=dict(ctime_ns=11,sha256="old")),key="before")
        after=dict(observation=dict(physical_input=dict(ctime_ns=12,sha256="new")),key="after")
        writes={}
        actor=types.SimpleNamespace(acquired=before,_acquire=lambda:after,
            _write=lambda name,raw:writes.__setitem__(name,raw),_check_owned=mock.Mock())
        with self.assertRaisesRegex(ValueError,"^C5 source/runtime/provider/clone-input currentness changed$"):
            self.owner_method()(actor)
        self.assertEqual(json.loads(writes["input-currentness-before.json"]),before["observation"])
        self.assertEqual(json.loads(writes["input-currentness-after.json"]),after["observation"])
        receipt=json.loads(writes["input-currentness-refusal.json"])
        self.assertEqual((receipt["before_key"],receipt["after_key"]),("before","after"))
        self.assertEqual(receipt["decision"],"REFUSED_UNCHANGED_COMPARATOR")
        actor._check_owned.assert_not_called()

    def test_unchanged_inputs_keep_no_receipt_cheap_path(self):
        before=dict(observation=dict(physical_input=dict(ctime_ns=11,sha256="same")),key="same")
        writer=mock.Mock();check=mock.Mock()
        actor=types.SimpleNamespace(acquired=before,_acquire=lambda:copy.deepcopy(before),_write=writer,_check_owned=check)
        self.owner_method()(actor)
        writer.assert_not_called();check.assert_called_once_with()


@unittest.skipUnless(sys.platform.startswith("linux") and shutil.which("bwrap"), "Linux Bubblewrap required")
class C5RuntimeMaterializationCases(unittest.TestCase):
    def test_actual_materialization_is_linked_and_readonly_to_original_reader(self):
        import fcntl
        tree=ast.parse((ROOT / "scripts/work-graph-c5-executor.py").read_bytes())
        owner=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=="GenuineC5Session")
        image=next(n for n in owner.body if isinstance(n,ast.FunctionDef) and n.name=="_image")
        loop=next(n for n in image.body if isinstance(n,ast.For) and any(
            isinstance(x,ast.Subscript) and isinstance(x.value,ast.Name) and x.value.id=="layout"
            and isinstance(x.slice,ast.Constant) and x.slice.value=="files" for x in ast.walk(n.iter)))
        append=next(n for n in loop.body if isinstance(n,ast.AugAssign) and isinstance(n.target,ast.Name) and n.target.id=="args")
        operation=ast.literal_eval(append.value.elts[2])
        raw=b"captured runtime bytes\n"
        fd=os.memfd_create("actual-selected-runtime-input",os.MFD_ALLOW_SEALING)
        try:
            os.write(fd,raw);os.lseek(fd,0,0);fcntl.fcntl(fd,fcntl.F_ADD_SEALS,15)
            program=("import importlib.util,json,os,errno;from pathlib import Path;"
                "s=importlib.util.spec_from_file_location('original_capture','/capture.py');"
                "m=importlib.util.module_from_spec(s);s.loader.exec_module(m);"
                "r=m.observe(Path('/evidence'),Path('/subject'));"
                "\ntry:\n f=os.open('/subject',os.O_WRONLY);os.close(f);r['readonly']=False"
                "\nexcept OSError as e:r['readonly']=e.errno==errno.EROFS"
                "\nprint(json.dumps(r))")
            command=[shutil.which("bwrap"),"--unshare-all","--unshare-user","--die-with-parent",
                "--new-session","--clearenv","--cap-drop","ALL","--ro-bind","/usr","/usr",
                "--ro-bind","/lib","/lib","--ro-bind","/lib64","/lib64","--proc","/proc",
                "--ro-bind",str(ROOT / "scripts/repro-event-capture.py"),"/capture.py",
                "--perms","0755",operation,str(fd),"/subject","--perms","0755","--tmpfs","/evidence",
                "--dir","/evidence/blobs","--remount-ro","/","--",sys.executable,"-I","-S","-B","-c",program]
            p=subprocess.run(command,capture_output=True,text=True,pass_fds=(fd,),timeout=15)
            self.assertEqual(p.returncode,0,p.stderr)
            observed=json.loads(p.stdout)
            self.assertEqual(observed["kind"],"FILE",observed)
            self.assertEqual(observed["stat"]["links"],1)
            self.assertEqual(observed["stat"]["mode"],0o755)
            self.assertEqual(observed["blob"],dict(bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest()))
            self.assertTrue(observed["readonly"],observed)
        finally:os.close(fd)


class C5R4ComposedSourceCases(unittest.TestCase):
    """Receive actual composed bytes; refuse drift before any output or child."""

    def module(self, root):
        path = root / 'scripts/load-work-graph-c5-executor.py'
        value = types.ModuleType('r4_composed_source_control')
        value.__file__ = str(path)
        exec(compile(path.read_bytes(), str(path), 'exec'), value.__dict__)
        return value

    def test_three_explicit_profiles_load_without_widening_execution_limits(self):
        current = self.module(ROOT)
        expected = (current.CURRENT_PROFILE, current.CORRESPONDENCE_PROFILE,
                    current.R4_CORRESPONDENCE_PROFILE)
        self.assertEqual(set(current.R4_COMPOSED_PINS), set(expected))
        with mock.patch('subprocess.Popen', side_effect=AssertionError('source receiving dispatched')):
            for profile in expected:
                with self.subTest(profile=profile), tempfile.TemporaryDirectory(prefix='c5-r4-profile-') as temporary:
                    root = Path(temporary) / 'source'; root.mkdir()
                    copy_c5_closed_source(root, profile=profile,
                                          revision=current.R4_COMPOSED_SOURCE_REVISION)
                    owner = self.module(root)
                    captured = owner._Engine(profile, source_revision=owner.R4_COMPOSED_SOURCE_REVISION)
                    engine = captured.load()
                    self.assertEqual(engine.PROFILE, profile)
                    self.assertEqual(engine.LIMITS['wall_seconds'], 120)
                    self.assertEqual(engine.LIMITS['work_bytes'], 512 * 1024**2)
                    self.assertEqual(engine.LIMITS['scratch_bytes'], 32 * 1024**2)
                    self.assertEqual(engine.LIMITS['file_bytes'],
                                     (16 if profile == owner.CURRENT_PROFILE else 64) * 1024**2)
                    captured.check()

    def test_three_factories_and_unbound_source_refuse_before_output(self):
        current = self.module(ROOT)
        fixture = _selected_source_fixture()
        factories = (
            (current.CURRENT_PROFILE, 'create_r4_composed_source_current_c5_session_v4'),
            (current.CORRESPONDENCE_PROFILE, 'create_r4_composed_source_correspondence_c5_session_v4'),
            (current.R4_CORRESPONDENCE_PROFILE, 'create_r4_composed_source_owned_correspondence_c5_session_v4'))
        for profile, factory in factories:
            with self.subTest(profile=profile), tempfile.TemporaryDirectory(prefix='c5-r4-source-') as temporary:
                root = Path(temporary) / 'source'; root.mkdir()
                output = Path(temporary) / 'must-not-exist'
                copy_c5_closed_source(root, profile=profile,
                                      revision=current.R4_COMPOSED_SOURCE_REVISION)
                base_physical = fixture.physical_member(
                    current, current.BASE, current.R4_COMPOSED_PINS[profile][current.BASE],
                    profile, current.R4_COMPOSED_SOURCE_REVISION)
                owner = self.module(root)
                with mock.patch('subprocess.Popen', side_effect=AssertionError('invalid source dispatched')):
                    with self.assertRaisesRegex(ValueError, 'C5 post-commit comparison metadata is malformed'):
                        getattr(owner, factory)(root, output, expected_source={})
                    self.assertFalse(output.exists())
                    (root / base_physical).write_bytes(b"raise AssertionError('unbound source executed')\n")
                    with self.assertRaisesRegex(ValueError, 'Unsupported fixed C5 execution member: ' + owner.BASE):
                        getattr(owner, factory)(root, output, expected_source={})
                    self.assertFalse(output.exists())

    def test_all_r3_closed_selection_maps_remain_exact(self):
        owner = self.module(ROOT)
        old = self.module(ROOT / 'test-support/work-graph-c5-profile-history/pre-r4-fresh-canary-20261104')
        for profile in (old.PROFILE, old.CURRENT_PROFILE, old.TASK_PROFILE, old.CORRESPONDENCE_PROFILE):
            with self.subTest(profile=profile):
                self.assertEqual(owner._selection(profile), old._selection(profile))
        for profile in (old.CURRENT_PROFILE, old.CORRESPONDENCE_PROFILE):
            for revision in (old.PUBLIC_STREAMING_SOURCE_REVISION, old.CURRENT105_SOURCE_REVISION,
                             old.CURRENT105_COMPOSED_SOURCE_REVISION):
                with self.subTest(profile=profile, revision=revision):
                    self.assertEqual(owner._selection(profile, revision), old._selection(profile, revision))
        for profile in ('unreviewed', None, {}, 1):
            with self.subTest(unknown_profile=profile), self.assertRaisesRegex(ValueError, 'R4 composed C5 profile'):
                owner._Engine(profile, source_revision=owner.R4_COMPOSED_SOURCE_REVISION)


if __name__ == "__main__":
    unittest.main()
