#!/usr/bin/env python3
"""Original105 source/effect controls; actual receiving is separately allocated."""
import ast
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import stat
import struct
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROFILE = "CONTROLLED_TASK_CUSTODY_APPEND_V1"
POLICY = "ORIGINAL105_PRIVATE_WORK_V1"
PROGRAM = "tests/custody-append.test.sh"


def load(name, relative):
    path = ROOT / relative
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


class CatalogCases(unittest.TestCase):
    def test_original105_has_an_explicit_finite_profile(self):
        helper = load("custody_finite", "scripts/qualify-work-graph-finite-leaf.py")
        try:
            contract = helper.contract_for(PROFILE)
        except ValueError:
            self.fail("missing exact original105 profile")
        self.assertEqual((contract["label"], contract["index"], contract["program"]),
                         ("custody-append", 105, PROGRAM))
        q = load("custody_catalog_owner", "scripts/qualify-work-graph-verifier.py")
        p = load("custody_catalog_prefix", "scripts/qualify-work-graph-prefix.py")
        graph, scope, node = helper.select_node(q.WG, (ROOT / helper.REGISTRY).read_bytes(), p.ENVIRONMENT, profile=PROFILE)
        self.assertEqual((len(graph["nodes"]), node), (117, graph["nodes"][105]))
        self.assertEqual((node["id"], node["source"]), ("COMMAND:" + PROGRAM + ":0", "bash " + PROGRAM + "\n"))
        self.assertEqual(scope["nodes"], [node["id"]])
        self.assertEqual(q._FINITE_MODES["custody-append"], PROFILE)
        self.assertEqual(len(helper._CONTRACTS), 36)


class SourceFixture(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix="r0035-custody-source-")
        self.addCleanup(temporary.cleanup)
        self.parent = Path(temporary.name)
        self.source = self.parent / "source"
        self.source.mkdir(mode=0o755)
        self.source.chmod(0o755)
        self.h = load("custody_source_finite", "scripts/qualify-work-graph-finite-leaf.py")
        self.p = load("custody_source_prefix", "scripts/qualify-work-graph-prefix.py")
        for name in self.h.source_paths(PROFILE):
            dest = self.source / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / name, dest)

    def add(self, name, data=b"complete physical source\n", mode=0o644):
        path = self.source / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        path.chmod(mode)
        return path

    def snapshot(self):
        objects = {}
        state, stamps = self.h.snapshot_source(self.p, self.source, objects, profile=PROFILE)
        return state, stamps, objects


class SourceCases(SourceFixture):
    def test_complete_source_bytes_modes_git_and_empty_directories(self):
        inputs = {".git/objects/opaque": (b"\x00\xff full Git data", 0o444),
                  ".hidden/untracked": (b"opaque hidden bytes", 0o644),
                  "new/selected-tool": (b"unexecuted ordinary source", 0o755)}
        for name, (raw, mode) in inputs.items():
            self.add(name, raw, mode)
        (self.source / ".git/empty").mkdir()
        state, _, objects = self.snapshot()
        subject = self.h.image_subject(state, profile=PROFILE)
        expected = {path.relative_to(self.source).as_posix() for path in self.source.rglob("*") if path.is_file()}
        self.assertEqual(set(subject), expected)
        self.assertIn(".git/empty", state["directories"])
        self.assertIn(self.h.REGISTRY, subject)
        for name, (raw, mode) in inputs.items():
            self.assertEqual((objects[subject[name]["sha256"]], subject[name]["mode"]), (raw, mode))

    def test_unsupported_physical_source_refuses(self):
        outside = self.parent / "outside"
        outside.write_bytes(b"unowned")
        target = self.source / "unsupported"
        for kind in ("symlink", "hardlink", "fifo", "mode"):
            if kind == "symlink": target.symlink_to(outside)
            elif kind == "hardlink": os.link(outside, target)
            elif kind == "fifo": os.mkfifo(target)
            else: target.write_bytes(b"bad mode"); target.chmod(0o600)
            with self.subTest(kind=kind), self.assertRaises((ValueError, OSError)):
                self.snapshot()
            target.unlink()
        (self.source / "private-mode-dir").mkdir(mode=0o700)
        with self.assertRaisesRegex(ValueError, "0755"):
            self.snapshot()

    def test_full_root_currentness_includes_hidden_git_and_replacement(self):
        path = self.add(".git/opaque", b"one")
        first, stamps1, _ = self.snapshot()
        path.write_bytes(b"two")
        second, stamps2, _ = self.snapshot()
        self.assertNotEqual(first, second)
        self.assertNotEqual(stamps1, stamps2)
        replacement = self.source / "replacement"
        replacement.write_bytes(b"two")
        replacement.replace(path)
        third, stamps3, _ = self.snapshot()
        self.assertEqual(second["files"], third["files"])
        self.assertNotEqual(stamps2, stamps3)
        (self.source / ".empty-new").mkdir()
        fourth, _, _ = self.snapshot()
        self.assertNotEqual(third["directories"], fourth["directories"])


LIMITS = dict(scratch_bytes=32 * 1024**2, file_bytes=16 * 1024**2,
              address_bytes=1024**3, descriptors=4096, stream_bytes=16 * 1024**2)


def policy_fixture():
    q = load("custody_policy_owner", "scripts/qualify-work-graph-verifier.py")
    owner_type = type("FixedCustodyPolicyUnitOwner", (q.VerifierTaskSession,), dict(SCOPE=PROFILE, LIMITS=dict(LIMITS)))
    owner = object.__new__(owner_type)
    files = {"/work/root.txt": (b"root bytes", 0o644),
             "/work/.git/object": (b"full Git bytes", 0o444),
             "/work/dir/child": (b"protected executable source", 0o755),
             "/usr/bin/closed-tool": (b"unit input, never executed", 0o555)}
    directories = ["/work", "/work/.git", "/work/.git/empty", "/work/dir", "/work/empty", "/usr", "/usr/bin"]
    config, raw, policy = owner._claim_overlay_configuration_v1(files, directories)
    files[policy["config_path"]] = raw, 0o600
    manifest = dict(root_read_only=True, directories=directories, private_source_overlay=policy,
        source_materialization="SINGLE_LINK_FILES_READ_ONLY_ROOT",
        source_permissions="PRESERVE_MODES_PRIVATE_ROOT_READ_ONLY_EXISTING_MEMBERS",
        data_permissions="OWNER_0600_READ_ONLY_MOUNT", copy_umask=0o022)
    node = dict(id="COMMAND:" + PROGRAM + ":0", source="bash " + PROGRAM + "\n")
    return owner, files, manifest, node, config


class ResourceCases(SourceFixture):
    def test_fixed_quotas_and_exact_image_launch_bounds(self):
        state, _, _ = self.snapshot()
        resources = self.h.temporary_requirements(state, profile=PROFILE)
        self.assertEqual((resources["work_capacity_bytes"], resources["tmp_capacity_bytes"]),
                         (2 * 1024**2, 30 * 1024**2))
        self.h.require_resource_capacity(resources, LIMITS)
        oversized = copy.deepcopy(state)
        for i in range(40): oversized["files"]["root-%03d" % i] = dict(bytes=1, mode=0o644, sha256="0" * 64)
        with self.assertRaisesRegex(ValueError, "work quota"):
            self.h.custody_append_output_bounds(oversized)
        owner, files, manifest, _, _ = policy_fixture()
        overlay = manifest["private_source_overlay"]
        reserved = self.h.custody_append_image_reservation(files, manifest["directories"], LIMITS, overlay, self.p.ENVIRONMENT)
        self.assertLess(reserved["descriptors"], LIMITS["descriptors"])
        self.assertEqual((reserved["staged_source_files"], reserved["staged_source_directories"],
                          reserved["source_bind_targets"]), (3, 5, 4))
        self.assertLess(reserved["launcher_argument_count"], 8500)
        # Unicode source names remain actual inputs. The fixed census buffer
        # must charge the bootstrap's ASCII escaping, not shorter UTF-8 text.
        named = {"/work/" + "\u03bb" * 100: (b"actual named source", 0o644)}
        _, _, unicode_policy = owner._claim_overlay_configuration_v1(named, ["/work"])
        ascii_named = {"/work/" + "x" * 100: (b"actual named source", 0o644)}
        _, _, ascii_policy = owner._claim_overlay_configuration_v1(ascii_named, ["/work"])
        self.assertEqual(unicode_policy["census_record_bound"] - ascii_policy["census_record_bound"], 2000)
        with self.assertRaisesRegex(ValueError, "file capacity"):
            self.h.custody_append_image_reservation({"/work/large": (b"x" * (LIMITS["file_bytes"] + 1), 0o644)},
                ["/work"], LIMITS, overlay, self.p.ENVIRONMENT)
        with self.assertRaisesRegex(ValueError, "descriptor|argument"):
            self.h.custody_append_image_reservation(dict(files, **{
                "/usr/a%04d" % i: (b"x", 0o555) for i in range(1800)}),
                manifest["directories"], LIMITS, overlay, self.p.ENVIRONMENT)
        with self.assertRaisesRegex(ValueError, "descriptor"):
            self.h.custody_append_image_reservation({"/work/d/a%04d" % i: (b"x", 0o644) for i in range(4096)},
                ["/work", "/work/d"], LIMITS, overlay, self.p.ENVIRONMENT)
        with self.assertRaisesRegex(ValueError, "memory"):
            self.h.custody_append_image_reservation(files, manifest["directories"], dict(LIMITS, address_bytes=4), overlay, self.p.ENVIRONMENT)
        with self.assertRaisesRegex(ValueError, "fixed resource"):
            self.h.custody_append_image_reservation(files, manifest["directories"], dict(LIMITS, scratch_bytes=64 * 1024**2), overlay, self.p.ENVIRONMENT)


class StageCases(unittest.TestCase):
    def test_complete_captured_bytes_modes_links_and_empty_directories(self):
        helper = load("custody_stage_owner", "scripts/qualify-work-graph-finite-leaf.py")
        _, files, manifest, _, _ = policy_fixture()
        original = copy.deepcopy((files, manifest))
        with tempfile.TemporaryDirectory(prefix="r0035-stage-positive-") as temporary:
            stage = helper.CustodyAppendSourceStage(Path(temporary), files, manifest["directories"],
                                                    manifest["private_source_overlay"], 4096)
            descriptors = tuple(stage._fds)
            try:
                observed = stage.check()
                self.assertEqual(observed["bind_targets"], ["/work/.git", "/work/dir", "/work/empty", "/work/root.txt"])
                root = Path(temporary) / "source-inputs/root"
                self.assertEqual({p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()},
                                 {"root.txt", ".git/object", "dir/child"})
                self.assertEqual({p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_dir()},
                                 {".git", ".git/empty", "dir", "empty"})
                for name, (raw, mode) in files.items():
                    if name.startswith("/work/"):
                        p = root / name[len("/work/"):]
                        self.assertEqual((p.read_bytes(), stat.S_IMODE(p.stat().st_mode), p.stat().st_nlink),
                                         (raw, mode, 1))
                self.assertEqual((files, manifest), original)
            finally:
                stage.close()
            for fd in descriptors:
                with self.assertRaises(OSError):
                    os.fstat(fd)

    def test_staged_currentness_and_unsupported_inputs_refuse(self):
        helper = load("custody_stage_refusal_owner", "scripts/qualify-work-graph-finite-leaf.py")
        _, files, manifest, _, _ = policy_fixture()
        for variant in ("bytes", "mode", "replacement", "extra", "private-ancestor"):
            with self.subTest(variant=variant), tempfile.TemporaryDirectory(prefix="r0035-stage-refusal-") as temporary:
                stage = helper.CustodyAppendSourceStage(Path(temporary), files, manifest["directories"],
                                                        manifest["private_source_overlay"], 4096)
                private = Path(temporary) / "source-inputs"
                path = private / "root/dir/child"
                try:
                    if variant == "bytes":
                        path.write_bytes(b"changed input")
                    elif variant == "mode":
                        path.chmod(0o600)
                    elif variant == "replacement":
                        raw = path.read_bytes(); path.unlink(); path.write_bytes(raw); path.chmod(0o755)
                    elif variant == "extra":
                        (private / "root/dir/extra").write_bytes(b"added")
                    else:
                        aside = Path(temporary) / "aside"
                        private.rename(aside)
                        private.mkdir()
                    with self.assertRaises((ValueError, OSError)):
                        stage.check()
                finally:
                    stage.close()
        for altered, dirs in ((dict(files, **{"/work/private": (b"private", 0o600)}), manifest["directories"]),
                              (files, [n for n in manifest["directories"] if n != "/work/.git"]),
                              (dict(files, **{"/work/../escape": (b"escape", 0o644)}), manifest["directories"])):
            with self.assertRaises(ValueError):
                helper.custody_append_source_plan(altered, dirs, manifest["private_source_overlay"])


class PolicyCases(unittest.TestCase):
    def test_private_root_protects_every_existing_immediate_member(self):
        owner, files, manifest, node, config = policy_fixture()
        self.assertEqual(owner._claim_overlay_guard_v1(files, manifest, node), config)
        policy = manifest["private_source_overlay"]
        self.assertEqual(policy["readonly_subtrees"], ["/work/.git", "/work/dir", "/work/empty"])
        self.assertNotIn("/work", config["immutable_paths"])
        for path in ("/", "/work/root.txt", "/work/.git", "/work/.git/object", "/work/.git/empty", "/work/dir/child"):
            self.assertIn(path, config["immutable_paths"])
        self.assertEqual(config["baseline"]["files"][".git/object"]["sha256"], hashlib.sha256(b"full Git bytes").hexdigest())
        self.assertEqual(config["baseline"]["files"]["dir/child"]["mode"], 0o755)
        self.assertEqual(policy["census"], "BEFORE_AND_AFTER_STATE_NOT_A_TEMPORAL_WRITE_TRACE")

    def test_policy_node_command_and_caller_changes_refuse(self):
        owner, files, manifest, node, _ = policy_fixture()
        for field, value in (("root", "/work/docs"), ("overlay_bytes", 1024**2),
                             ("tmp_bytes", 32 * 1024**2), ("readonly_subtrees", [])):
            changed = copy.deepcopy(manifest)
            changed["private_source_overlay"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                owner._claim_overlay_guard_v1(files, changed, node)
        for changed in (dict(node, id="COMMAND:tests/other.test.sh:0"), dict(node, source="true\n")):
            with self.assertRaises(ValueError): owner._claim_overlay_guard_v1(files, manifest, changed)
        for field, value in (("source_materialization", None), ("source_permissions", None),
                             ("data_permissions", None), ("private_source_overlay", None), ("copy_umask", 0o077)):
            with self.subTest(field=field), self.assertRaises(ValueError):
                owner._claim_overlay_guard_v1(files, dict(manifest, **{field: value}), node)
        with self.assertRaises(ValueError):
            owner._claim_overlay_guard_v1(dict(files, **{"/work/root.txt": (b"replacement", 0o644)}), manifest, node)


def synthetic_phase(config):
    """Explicit unit decoder input; never actual mount or original evidence."""
    return dict(source=dict(files=copy.deepcopy(config["baseline"]["files"]),
        directories={name: dict(mode=mode, read_only=name != ".")
                     for name, mode in config["baseline"]["directories"].items()}),
        tmp=dict(files={}, directories={".": dict(mode=0o755, read_only=False)}),
        immutable_mounts={path: True for path in config["immutable_paths"]})


def decode_record(owner, config, record):
    raw = json.dumps(record, sort_keys=True, separators=(",", ":")).encode()
    data = struct.pack("!Q", len(raw)) + raw
    data += bytes(config["buffer_bytes"] - len(data))
    return owner._claim_effects_decode_v1(data, config)


class EffectsCases(unittest.TestCase):
    def test_complete_restoration_retains_actual_exit(self):
        owner, _, _, _, config = policy_fixture()
        phase = synthetic_phase(config)
        for code in (0, 3, -15):
            record = dict(policy=POLICY, phase="AFTER", original_started=True,
                original_exit=code, before=copy.deepcopy(phase), after=copy.deepcopy(phase))
            result = decode_record(owner, config, record)
            self.assertEqual((result["observation"], result["original_exit"]), ("COMPLETE", code))
            self.assertTrue(result["protected_members_unchanged"])
            self.assertTrue(result["clean_private_namespace"])

    def test_residue_changed_protection_and_partial_census_refuse(self):
        owner, _, _, _, config = policy_fixture()
        phase = synthetic_phase(config)
        original = dict(policy=POLICY, phase="AFTER", original_started=True,
            original_exit=0, before=copy.deepcopy(phase), after=copy.deepcopy(phase))
        for kind in ("extra-file", "extra-directory", "changed-bytes", "changed-mode", "writable-existing", "missing-after"):
            record = copy.deepcopy(original)
            if kind == "extra-file": record["after"]["source"]["files"]["unexpected"] = dict(mode=0o644, bytes=1, sha256="0" * 64)
            elif kind == "extra-directory": record["after"]["source"]["directories"]["unexpected"] = dict(mode=0o755, read_only=False)
            elif kind == "changed-bytes": record["after"]["source"]["files"]["root.txt"]["sha256"] = "0" * 64
            elif kind == "changed-mode": record["after"]["source"]["files"]["root.txt"]["mode"] = 0o600
            elif kind == "writable-existing": record["after"]["immutable_mounts"]["/work/root.txt"] = False
            else: record.pop("after"); record["phase"] = "RUNNING"
            result = decode_record(owner, config, record)
            eligible = result["observation"] == "COMPLETE" and result["clean_private_namespace"] and result["protected_members_unchanged"]
            with self.subTest(kind=kind): self.assertFalse(eligible)
        blank = owner._claim_effects_decode_v1(bytes(config["buffer_bytes"]), config)
        self.assertEqual(blank["observation"], "REFUSED")


def synthetic_selection(helper):
    """Typed controlled fixtures; no host runtime acquisition or receipt."""
    objects = {}
    def datum(name, raw):
        key = hashlib.sha256(raw).hexdigest(); objects[key] = raw
        return dict(kind="FILE", resolved=name, mode=0o644, bytes=len(raw), sha256=key)
    aliases = {name: dict(kind="MISSING") for name in helper._CUSTODY_PYTHON_ALIASES}
    aliases["/usr/bin/python3"] = dict(kind="FILE", resolved="/usr/bin/python3.12", mode=0o755,
        sha256=helper._CUSTODY_PYTHON_PINS["/usr/bin/python3.12"])
    namespaces = {name: dict(observation=dict(kind="DIRECTORY"), names={}, pth={})
                  for name in helper._CUSTODY_SEARCH_ROOTS}
    customizer = datum(helper._CUSTODY_SITE_TARGET, b'# install the apport exception handler if available\ntry:\n    import apport_python_hook\nexcept ImportError:\n    pass\nelse:\n    apport_python_hook.install()\n')
    customizer.update(alias_identity=["controlled alias identity"], link=helper._CUSTODY_SITE_TARGET)
    namespaces["/usr/lib/python3.12"]["names"]["sitecustomize.py"] = customizer["alias_identity"]
    pth = datum(helper._CUSTODY_PTH_PATH, b'import os; exec(\'try: __import__("coloredlogs").auto_install() if os.environ.get("COLOREDLOGS_AUTO_INSTALL") else None\\nexcept ImportError: pass\')\n')
    namespaces["/usr/lib/python3/dist-packages"]["names"]["coloredlogs.pth"] = ["controlled file identity"]
    namespaces["/usr/lib/python3/dist-packages"]["pth"]["coloredlogs.pth"] = pth
    nss = dict(files={"/etc/nsswitch.conf": datum("/etc/nsswitch.conf", b"passwd: files\n"),
        "/etc/passwd": datum("/etc/passwd", b"fixture:x:0:0:Fixture:/fixture:/bin/false\n")},
        absent={name: dict(kind="MISSING") for name in helper._CUSTODY_NSCD_ABSENT},
        native=dict(helper._CUSTODY_NSS_NATIVE_PINS))
    binding = dict(environment=dict(helper._CUSTODY_ENVIRONMENT),
        identity=dict(uid=0, euid=0, gid=0, egid=0), customizer=customizer, nss=nss)
    return dict(aliases=aliases, absent={name: dict(kind="MISSING") for name in helper._CUSTODY_ABSENT_PATHS},
        namespaces=namespaces, startup_binding=binding), objects


class RuntimeCases(unittest.TestCase):
    def test_normal_startup_and_genuine_absence_are_bound(self):
        helper = load("custody_runtime_finite", "scripts/qualify-work-graph-finite-leaf.py")
        selection, objects = synthetic_selection(helper)
        branch = helper.custody_runtime_branch(selection, objects)
        self.assertEqual(branch["selected_python_paths"], ["/usr/bin/python3"])
        self.assertEqual(branch["startup"], "NORMAL_SITE_NO_S_FLAG_NO_USER_SITE_SAFE_PATH")
        self.assertFalse(branch["package_import_failure_is_absence"])
        self.assertFalse(branch["installed_positive_qualified"])
        self.assertEqual(branch["customizer_sha256"], helper._CUSTODY_SITE_SHA256)
        self.assertEqual((branch["nss"]["service"], branch["nss"]["uid"]), ("files", 0))
        self.assertEqual(set(branch["nss"]["input_sha256"]), {"/etc/nsswitch.conf", "/etc/passwd"})
        raw = b"# inert normal-site observation\n\n"
        key = helper.digest(raw)
        namespace = selection["namespaces"][helper._CUSTODY_SITE_ROOTS[0]]
        namespace["names"]["inert.pth"] = ["typed test fixture"]
        namespace["pth"]["inert.pth"] = dict(sha256=key, bytes=len(raw))
        objects[key] = raw
        self.assertEqual(helper.custody_runtime_branch(selection, objects)["branch"], branch["branch"])
        names = set(helper._CUSTODY_UNUSED_BASE_TOOLS) | set(helper._CUSTODY_IMAGE_TOOLS) | {"/usr/bin/uname", "/usr/bin/python3"}
        runtime = dict(files={name: dict(mode=0o555, bytes=1, sha256="a" * 64) for name in names},
                       observations={name: dict(mode=0o755, bytes=1, sha256="a" * 64) for name in names})
        runtime["files"]["/usr/lib/kept-native-dependency"] = dict(mode=0o444, bytes=1, sha256="b" * 64)
        before_observations = copy.deepcopy(runtime["observations"])
        projection = helper.custody_runtime_projection(runtime)
        self.assertEqual(set(projection["removed_image_entries"]), set(helper._CUSTODY_UNUSED_BASE_TOOLS))
        self.assertEqual(runtime["observations"], before_observations)
        self.assertIn("/usr/lib/kept-native-dependency", runtime["files"])
        self.assertIn("/usr/bin/python3", runtime["files"])
        self.assertEqual(projection["source_members"], "COMPLETE_UNCHANGED_NO_SOURCE_OR_GIT_OMISSIONS")
        # Exercise the physical namespace reader on test data only. This is
        # not inspection/acquisition of an installed interpreter or package.
        prefix = load("custody_optional_namespace_prefix", "scripts/qualify-work-graph-prefix.py")
        self.assertEqual(helper._CUSTODY_ENVIRONMENT, prefix.ENVIRONMENT)
        self.assertTrue({"HOME", "PYTHONUSERBASE", "COLOREDLOGS_AUTO_INSTALL"}.isdisjoint(prefix.ENVIRONMENT))
        with tempfile.TemporaryDirectory(prefix="r0035-custody-optional-") as temporary:
            root = Path(temporary)
            data = root / "selected.conf"
            payload = b"passwd: files\n"
            data.write_bytes(payload); data.chmod(0o644)
            captured = {}
            selected = helper._custody_data_file(prefix, str(data), captured,
                resolved=str(data), limit=64, pin=hashlib.sha256(payload).hexdigest())
            self.assertEqual(captured[selected["sha256"]], payload)
            self.assertEqual((selected["kind"], selected["mode"], selected["bytes"]), ("FILE", 0o644, len(payload)))
            alias = root / "selected-alias"
            alias.symlink_to(data)
            linked = helper._custody_data_file(prefix, str(alias), {}, resolved=str(data),
                limit=64, pin=selected["sha256"], alias=str(data))
            self.assertEqual(linked["identity"], selected["identity"])
            self.assertEqual(linked["link"], str(data))
            data.write_bytes(b"passwd: files systemd\n")
            with self.assertRaisesRegex(ValueError, "bytes or metadata differ"):
                helper._custody_data_file(prefix, str(alias), {}, resolved=str(data),
                    limit=64, pin=selected["sha256"], alias=str(data))
            changed = helper._custody_data_file(prefix, str(data), {}, resolved=str(data), limit=64)
            self.assertNotEqual(changed["sha256"], selected["sha256"])
            self.assertNotEqual(changed, selected)
            missing = root / "optional"
            before = helper._custody_path_state(prefix, str(missing))
            self.assertEqual(before["kind"], "MISSING")
            missing.write_bytes(b"present optional test datum")
            self.assertEqual(helper._custody_path_state(prefix, str(missing))["kind"], "FILE")
            (root / "activegraph").mkdir()
            observed = helper._custody_namespace(prefix, str(root), {})
            self.assertIn("activegraph", observed["names"])
            altered, altered_objects = synthetic_selection(helper)
            altered["namespaces"][helper._CUSTODY_SITE_ROOTS[0]] = observed
            with self.assertRaisesRegex(ValueError, "present ActiveGraph"):
                helper.custody_runtime_branch(altered, altered_objects)

    def test_present_or_unclosed_runtime_branch_refuses(self):
        helper = load("custody_runtime_refusals", "scripts/qualify-work-graph-finite-leaf.py")
        prefix = load("custody_runtime_basis_prefix", "scripts/qualify-work-graph-prefix.py")
        with self.assertRaisesRegex(ValueError, "base runtime differs"):
            helper._capture_custody_runtime(prefix, dict(files={}), {})
        for kind in ("package", "customizer", "cli", "interpreter", "zip", "missing-selector", "pth",
                     "apport", "customizer-bytes", "customizer-target", "pth-bytes", "environment", "home",
                     "uid", "nss-service", "passwd-entry", "missing-nss", "nscd", "native"):
            selection, objects = synthetic_selection(helper)
            namespace = selection["namespaces"][helper._CUSTODY_SITE_ROOTS[0]]
            binding = selection["startup_binding"]
            if kind == "package": namespace["names"]["activegraph"] = ["directory, broken import still present"]
            elif kind == "customizer": namespace["names"]["sitecustomize.py"] = ["file"]
            elif kind == "cli": selection["absent"]["/usr/bin/activegraph"] = dict(kind="FILE")
            elif kind == "interpreter": selection["aliases"]["/usr/bin/python3"]["sha256"] = "0" * 64
            elif kind == "zip": selection["absent"]["/usr/lib/python312.zip"] = dict(kind="FILE")
            elif kind == "missing-selector": del selection["namespaces"][helper._CUSTODY_SITE_ROOTS[0]]
            elif kind == "apport": namespace["names"]["apport_python_hook.py"] = ["present even if import would fail"]
            elif kind == "customizer-bytes": binding["customizer"]["sha256"] = "0" * 64
            elif kind == "customizer-target": binding["customizer"]["resolved"] = "/unqualified/sitecustomize.py"
            elif kind == "environment": binding["environment"]["COLOREDLOGS_AUTO_INSTALL"] = "1"
            elif kind == "home": binding["environment"]["HOME"] = "/nonexistent"
            elif kind == "uid": binding["identity"]["uid"] = 1
            elif kind == "missing-nss": del binding["nss"]["files"]["/etc/passwd"]
            elif kind == "nscd": binding["nss"]["absent"]["/var/run/nscd/socket"] = dict(kind="FILE")
            elif kind == "native": binding["nss"]["native"]["/lib/x86_64-linux-gnu/libc.so.6"] = "0" * 64
            elif kind in ("nss-service", "passwd-entry", "pth-bytes"):
                if kind == "nss-service":
                    entry = binding["nss"]["files"]["/etc/nsswitch.conf"]; raw = b"passwd: files systemd\n"
                elif kind == "passwd-entry":
                    entry = binding["nss"]["files"]["/etc/passwd"]; raw = b"fixture:x:1:1:Fixture:/fixture:/bin/false\n"
                else:
                    entry = selection["namespaces"]["/usr/lib/python3/dist-packages"]["pth"]["coloredlogs.pth"]
                    raw = objects[entry["sha256"]] + b"\n"
                key = hashlib.sha256(raw).hexdigest(); objects[key] = raw
                entry.update(sha256=key, bytes=len(raw))
            else:
                raw = b"import an_unclosed_startup_dependency\n"; key = helper.digest(raw); objects[key] = raw
                namespace["names"]["startup.pth"] = ["file"]
                namespace["pth"]["startup.pth"] = dict(sha256=key, bytes=len(raw))
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                helper.custody_runtime_branch(selection, objects)


class WiringCases(unittest.TestCase):
    def test_shared_runner_and_old_contract_semantics_are_preserved(self):
        helper = load("custody_wiring_finite", "scripts/qualify-work-graph-finite-leaf.py")
        runner = (ROOT / helper.RUNNER).read_bytes()
        pin = hashlib.sha256(runner).hexdigest()
        references = [contract[role][helper.RUNNER] for contract in helper._CONTRACTS.values()
                      for role in ("programs", "pinned_data") if helper.RUNNER in contract.get(role, {})]
        self.assertEqual(references, [pin] * 6)
        contract_tree = ast.parse((ROOT / helper.HELPER).read_text().replace(pin, "532b06dbe91298bf71d44c88ecf20186adc93b4e3fb16ee2c4d12bc2edee45ff"))
        contracts = next(n.value for n in contract_tree.body if isinstance(n, ast.Assign)
                         and any(isinstance(t, ast.Name) and t.id == "_CONTRACTS" for t in n.targets))
        keep = [(key, value) for key, value in zip(contracts.keys, contracts.values)
                if not (isinstance(key, ast.Name) and key.id == "CUSTODY_APPEND_PROFILE")]
        contracts.keys, contracts.values = [pair[0] for pair in keep], [pair[1] for pair in keep]
        # Current incoming90 includes repaired87 and the accepted CI repair.
        # Compare all35 incoming contracts after the six forward runner-pin
        # advances; never restore the historical stale RETENTION value.
        self.assertEqual(len(keep), 35)
        self.assertEqual(hashlib.sha256(ast.dump(contracts, include_attributes=False).encode()).hexdigest(),
                         "8de1e9654c055e0291aecf68ae08ea0f65834251df7976976c521248afeff2ab")
        old33 = [(key, value) for key, value in keep
                 if not (isinstance(key, ast.Name) and key.id in ("MINI_AUDIT_PROFILE", "ACTION_SELECTION_PROFILE"))]
        old33_contracts = ast.Dict(keys=[key for key, _ in old33], values=[value for _, value in old33])
        self.assertEqual(len(old33), 33)
        self.assertEqual(hashlib.sha256(ast.dump(old33_contracts, include_attributes=False).encode()).hexdigest(),
                         "74d15a92028e607bf63729a67e5acef566fb5785317dfd79bbf74b694672d280")
        text = runner.decode()
        code = text.split("  exec \"${r0035_census_python[@]}\" -c '\n", 1)[1].split(
            "\n' \"$2\" \"$3\" \"$4\" \"$5\" \"$6\"", 1)[0]
        tree = ast.parse(code)
        table = next(node.value for node in tree.body if isinstance(node, ast.Assign)
                     and any(isinstance(t, ast.Name) and t.id == "policies" for t in node.targets))
        policies = ast.literal_eval(table)
        self.assertEqual(policies[POLICY], (PROGRAM, "/work", "original105", "source"))
        self.assertEqual(policies["ORIGINAL96_PRIVATE_DOCS_V1"],
                         ("tests/claim-boundary-proof-levels.test.sh", "/work/docs", "original96", "docs"))
        self.assertIn("os.set_inheritable(descriptor, False)", code)
        self.assertIn("close_fds=True", code)
        self.assertIn("r0035_census_python=(python -I -B)", text)
        self.assertEqual(helper.contract_for(helper.CLAIM_BOUNDARY_PROFILE)["projection"],
            "COMPLETE_ACTUAL_ROOT_MEMBERSHIP_PUBLIC_READ_BYTES_EXCLUDED_CONTENT_TYPED_PLACEHOLDERS_FIXED_PRIVATE_DOCS_OVERLAY")
        wrapper = (ROOT / "tests/work-graph-verifier.test.sh").read_text()
        self.assertEqual(wrapper.count("tests/work-graph-custody-append-cases.py"), 1)


if __name__ == "__main__":
    unittest.main()
