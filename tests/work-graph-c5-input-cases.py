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
            original_index=48, original_argv=["bash", "tests/reproducible-release-asset.test.sh"]),
            CORRESPONDENCE_PROFILE="FIXED_GENUINE_C5_SHARED_IMAGE_CORRESPONDENCE_20261031_V1",
            Q=types.SimpleNamespace(REPRO_CORRESPONDENCE_PRODUCER_SHA256="550a92a48989a2a9987b3d51c26a3198cf4828aad28fd3ffe8815fea6399019d"))
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
        n = dict(os=os, stat=stat, need=need)
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


@unittest.skipUnless(sys.platform.startswith('linux') and hasattr(os,'pidfd_open'), 'Linux live child custody required')
class C5CorrespondenceLiveCases(unittest.TestCase):
    """Actual tiny C5 channels/children; no acquired-image or original claim."""
    def test_closed_shared_profile_buffers_and_source_drift_refuse(self):
        path=ROOT/'scripts/load-work-graph-c5-executor.py';tree=ast.parse(path.read_bytes())
        assignment=next(n for n in tree.body if isinstance(n,ast.Assign) and
            any(isinstance(t,ast.Name) and t.id=='CORRESPONDENCE_PINS' for t in n.targets))
        pins=ast.literal_eval(assignment.value.args[0])
        with tempfile.TemporaryDirectory(prefix='c5-correspondence-source-') as temporary:
            source=Path(temporary)
            for name in [*pins,'scripts/load-work-graph-c5-executor.py']:
                target=source/name;target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes((ROOT/name).read_bytes());target.chmod(0o644)
            spec=importlib.util.spec_from_file_location('closed_current_pair_source',source/'scripts/load-work-graph-c5-executor.py')
            owner=importlib.util.module_from_spec(spec);spec.loader.exec_module(owner)
            captured=owner._Engine(owner.CORRESPONDENCE_PROFILE);engine=captured.load()
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
        for name in [*pins,'scripts/load-work-graph-c5-executor.py']:
            target=source/name;target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes((ROOT/name).read_bytes());target.chmod(0o644)
        selected=importlib.util.spec_from_file_location('actual_closed_correspondence_owner',source/'scripts/load-work-graph-c5-executor.py')
        owner=importlib.util.module_from_spec(selected);selected.loader.exec_module(owner)
        engine=owner._Engine(owner.CORRESPONDENCE_PROFILE).load()
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
            ast.unparse(ast.Module(body=functions,type_ignores=[]))+'\n'+
            'bootstrap_correspondence_pair(dict(scope=CORRESPONDENCE_PROFILE,correspondence_pair=CORRESPONDENCE_POLICY),int(sys.argv[1]))\n')
        parent,child=socket.socketpair();self.addCleanup(parent.close);self.addCleanup(child.close)
        env=dict(fixture.env,TMPDIR=str(work),R0035_REPRO_EVENT_CAPTURE_DIR=str(work/'capture'),
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
            path=Path(shutil.which(name)).resolve();executables[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
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
        for name in [*ast.literal_eval(node.value.args[0]),'scripts/load-work-graph-c5-executor.py']:
            target=source/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes((ROOT/name).read_bytes());target.chmod(0o644)
        spec=importlib.util.spec_from_file_location('actual_abort_source_owner',source/'scripts/load-work-graph-c5-executor.py')
        owner=importlib.util.module_from_spec(spec);spec.loader.exec_module(owner)
        engine=owner._Engine(owner.CORRESPONDENCE_PROFILE).load()
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
            ast.unparse(ast.Module(body=functions,type_ignores=[]))+'\n'+
            'bootstrap_correspondence_pair(dict(scope=CORRESPONDENCE_PROFILE,correspondence_pair=CORRESPONDENCE_POLICY),int(sys.argv[1]))\n')
        parent,child=socket.socketpair()
        env=dict(fixture.env,TMPDIR=str(work),R0035_REPRO_EVENT_CAPTURE_DIR=str(work/'capture'),
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


if __name__ == "__main__":
    unittest.main()
