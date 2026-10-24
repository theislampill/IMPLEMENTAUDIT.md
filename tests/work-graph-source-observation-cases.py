#!/usr/bin/env python3
"""Constructed envelope and real held-source receiver controls; no native credit."""
from __future__ import annotations

import contextlib
import copy
import hashlib
import inspect
import json
import os
from pathlib import Path
import shutil
import tempfile
import types
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def load(path, name):
    module = types.ModuleType(name)
    module.__file__ = str(path)
    exec(compile(path.read_bytes(), str(path), "exec"), module.__dict__)
    return module


WG = load(ROOT / "skills/implementaudit/scripts/compile-work-graph.py", "closure_graph")
OE = load(ROOT / "scripts/operational-evidence.py", "closure_receiver")


class EnvelopeControls(unittest.TestCase):
    def setUp(self):
        self.pair = dict(zip(("claim_sha256", "validate_sha256"), WG._NATIVE_REQUIRE_VERIFICATION_EQUIVALENCE))
        self.closure = None
        self.late_change = False
        self.omit_closure = False

    @contextlib.contextmanager
    def constructed_observation(self, run, repo, **kw):
        """Declared test boundary only: this does not run a continuity owner."""
        graph = dict(binding=dict(continuity_helper_digest=self.pair["claim_sha256"]))
        for entering in (True, False):
            kw["_continuity_sources"].append(copy.deepcopy(self.pair))
            closure = kw.get("_continuity_closures")
            if closure is not None and not self.omit_closure:
                closure.append(copy.deepcopy(self.closure) if entering or not self.late_change else {"changed": True})
            if entering:
                if kw.get("_episode_outputs") is not None:
                    kw["_episode_outputs"].append(None)
                yield json.dumps(graph).encode()

    def observe(self, method):
        with patch.object(WG, "observe_native_run_v1", self.constructed_observation):
            with getattr(WG, method)(Path("/constructed/run"), Path("/constructed/repo")) as raw:
                return json.loads(raw)

    def test_01_old_envelopes_keep_exact_fields_and_schema(self):
        for episode in (False, True):
            suffix = "episode_sources" if episode else "sources"
            value = self.observe("observe_native_run_" + suffix + "_v1")
            expected = {"schema", "projection", "continuity_sources"}
            if episode:
                expected.add("ordinary_episode")
            self.assertEqual(set(value), expected)
            self.assertTrue(value["schema"].endswith(".v1"))
            self.assertEqual(value["continuity_sources"], self.pair)

    def test_02_v2_explicitly_represents_old_two_source_scope(self):
        value = self.observe("observe_native_run_sources_v2")
        self.assertEqual(value["schema"], "implementaudit.native-run-source-observation.v2")
        self.assertIsNone(value["continuity_closure"])

    def test_03_six_sources_cannot_be_presented_as_v1(self):
        self.pair = dict(zip(("claim_sha256", "validate_sha256"), WG._NATIVE_SIX_SOURCE_PAIR_V1))
        self.closure = {"constructed": "complete output sink is separately tested below"}
        for method in ("observe_native_run_sources_v1", "observe_native_run_episode_sources_v1"):
            with self.subTest(method=method), self.assertRaisesRegex(WG.WorkGraphError, "requires the v2"):
                self.observe(method)

    def test_04_v2_carries_complete_output_and_episode_without_caller_authority(self):
        self.closure = {"constructed": "owned output"}
        for method in ("observe_native_run_sources_v2", "observe_native_run_episode_sources_v2"):
            self.assertEqual(list(inspect.signature(getattr(WG, method)).parameters),
                             ["run_root", "repo_root", "input_root", "expected_current"])
            self.assertEqual(self.observe(method)["continuity_closure"], self.closure)

    def test_05_missing_or_changed_closure_refuses(self):
        unknown = dict(claim_sha256="1" * 64, validate_sha256="2" * 64)
        self.pair = unknown
        with self.assertRaisesRegex(WG.WorkGraphError, "requires the v2"):
            self.observe("observe_native_run_sources_v1")
        self.omit_closure = True
        with self.assertRaisesRegex(WG.WorkGraphError, "absent or malformed"):
            self.observe("observe_native_run_sources_v2")
        self.omit_closure = False
        self.late_change = True
        with self.assertRaisesRegex(WG.WorkGraphError, "closure changed"):
            self.observe("observe_native_run_sources_v2")


@unittest.skipUnless(os.name == "posix", "the six-source transport has a POSIX source-mode profile")
class ReceivingClosureControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="r0035-source-closure-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "skills/implementaudit/scripts"
        self.source.mkdir(parents=True)
        self.compiler = self.source / "compile-work-graph.py"
        self.compiler.write_bytes(b"constructed path anchor; compiler bytes checked by enclosing owner")
        self.rows = []
        for name, size, digest, mode in OE._NATIVE_CONTINUITY_SIX_SOURCE_PROFILE_V1:
            path = self.source / name
            shutil.copyfile(ROOT / "skills/implementaudit/scripts" / name, path)
            path.chmod(mode)
            self.rows.append(dict(name=name, path=str(path), bytes=size, sha256=digest,
                                 mode=mode, links=1, readonly=True, seals=15))
        self.adapter = self.root / "scripts/work-graph-continuity-transport.py"
        self.adapter.parent.mkdir()
        shutil.copy2(ROOT / "scripts/work-graph-continuity-transport.py", self.adapter)
        raw = self.adapter.read_bytes()
        self.value = dict(schema="implementaudit.native-continuity-closure.v1",
            execution=dict(schema="implementaudit.continuity-source-closure.v2",
                           repository=str(self.root), members=self.rows,
                           startup=dict(profile="ISOLATED_CPYTHON_V1", isolated=True,
                                        no_site=True, dont_write_bytecode=True)),
            transport=dict(path=str(self.adapter), bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest(),
                           mode=self.adapter.stat().st_mode & 4095))
        self.pair = dict(claim_sha256=self.rows[0]["sha256"], validate_sha256=self.rows[1]["sha256"])
        self.owner_file = patch.object(OE, "__file__", str(self.root / "scripts/operational-evidence.py"))
        self.owner_file.start()
        self.addCleanup(self.owner_file.stop)

    def check(self, value=None):
        OE._native_check_continuity_closure_v1(self.value if value is None else value,
                                              self.root, self.compiler, self.pair)

    def test_06_real_held_source_reads_accept_only_complete_same_checkout_closure(self):
        self.check()
        for mutation in (lambda v: v["execution"]["members"].pop(),
                         lambda v: v["execution"]["members"].reverse(),
                         lambda v: v["execution"].update(repository="/foreign/repository"),
                         lambda v: v.update(extra="unacquired"),
                         lambda v: v["execution"]["members"][0].update(bytes=float(self.rows[0]["bytes"])),
                         lambda v: v["execution"]["members"][0].update(readonly=1),
                         lambda v: v["execution"]["members"][0].update(seals=7),
                         lambda v: v["execution"].pop("startup"),
                         lambda v: v["execution"].update(schema="implementaudit.continuity-source-closure.v1"),
                         lambda v: v["execution"]["startup"].update(isolated=False),
                         lambda v: v["execution"]["startup"].update(no_site=1),
                         lambda v: v["execution"]["startup"].update(dont_write_bytecode=False)):
            value = copy.deepcopy(self.value)
            mutation(value)
            with self.subTest(value=value), self.assertRaises(OE.OperationalEvidenceError):
                self.check(value)

    def test_07_captured_path_never_selects_a_read(self):
        value = copy.deepcopy(self.value)
        value["execution"]["members"][2]["path"] = "/foreign/do-not-open"
        with patch.object(OE, "_native_file", wraps=OE._native_file) as reads:
            with self.assertRaises(OE.OperationalEvidenceError):
                self.check(value)
        self.assertNotIn(Path("/foreign/do-not-open"), [call.args[0] for call in reads.call_args_list])

    def test_08_changed_companion_and_adapter_refuse(self):
        for path in (self.source / "canonical_custody.py", self.adapter):
            original = path.read_bytes()
            try:
                path.write_bytes(original + b"\n# changed after source acquisition\n")
                with self.subTest(path=path), self.assertRaises(OE.OperationalEvidenceError):
                    self.check()
            finally:
                path.write_bytes(original)

    def test_09_symlink_and_hardlink_companions_refuse(self):
        path = self.source / "canonical_custody.py"
        real = path.with_name("retained-custody.py")
        path.rename(real)
        path.symlink_to(real)
        with self.assertRaises(OE.OperationalEvidenceError):
            self.check()
        path.unlink()
        path.hardlink_to(real)
        with self.assertRaises(OE.OperationalEvidenceError):
            self.check()

    def test_10_legacy_none_is_explicit_and_never_promotes_current_six_sources(self):
        legacy = dict(zip(("claim_sha256", "validate_sha256"), WG._NATIVE_REQUIRE_VERIFICATION_EQUIVALENCE))
        OE._native_check_continuity_closure_v1(None, self.root, self.compiler, legacy)
        with self.assertRaises(OE.OperationalEvidenceError):
            OE._native_check_continuity_closure_v1(None, self.root, self.compiler, self.pair)
        with self.assertRaises(OE.OperationalEvidenceError):
            OE._native_check_continuity_closure_v1(self.value, self.root, self.compiler, legacy)


if __name__ == "__main__":
    unittest.main(verbosity=2)
