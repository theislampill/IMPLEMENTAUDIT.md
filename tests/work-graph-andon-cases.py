#!/usr/bin/env python3
"""Finite original andon-class node controls; no canonical/native claim."""
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]

_historical_spec = importlib.util.spec_from_file_location("historical_fixture", ROOT / "tests/work-graph-historical-fixture.py")
H = importlib.util.module_from_spec(_historical_spec)
_historical_spec.loader.exec_module(H)
HELPER = ROOT / "scripts/qualify-work-graph-finite-leaf.py"
PROFILE = "CONTROLLED_TASK_ANDON_CLASS_V1"
DATA = ("skills/implementaudit/SKILL.md", "skills/implementaudit/templates/PROTOCOL.md",
        "skills/implementaudit/references/transcript-contract.md")


def load(name, path):
    data = path.read_bytes()
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    exec(compile(data, str(path), "exec"), module.__dict__)
    return module


shared = load("andon_case_support", ROOT / "tests/work-graph-audit-spec-cases.py")
Q, P = shared.Q, shared.P


class AdmissionCases(shared.ProfileFixture, unittest.TestCase):
    PROFILE = PROFILE

    def setUp(self):
        self.assertTrue(HELPER.is_file(), "shared finite andon profile is absent")
        super().setUp()

    def test_exact_original_andon_node_and_no_other_admission(self):
        registry = H.original("scripts/verify-package.sh")
        graph, scope, node = self.A.select_node(Q.WG, registry, P.ENVIRONMENT, profile=PROFILE)
        self.assertEqual(len(graph["nodes"]), 117)
        self.assertEqual(node, graph["nodes"][25])
        self.assertEqual(node["id"], "COMMAND:tests/andon-class-contract.test.sh:0")
        self.assertEqual(node["source"], "bash tests/andon-class-contract.test.sh\n")
        self.assertEqual(scope["profile"], PROFILE)
        self.assertEqual(scope["nodes"], [node["id"]])
        self.assertEqual(len(scope["omitted_nodes"]), 116)

    def test_exact_five_input_closure_and_pinned_original_program(self):
        state, _, _ = self.snapshot()
        expected = {"scripts/verify-package.sh", "tests/andon-class-contract.test.sh", *DATA}
        self.assertEqual(set(state["files"]), expected)
        session = self.session()
        path = self.source / "tests/andon-class-contract.test.sh"
        path.write_bytes(path.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "executable"):
            session.run()
        self.assertEqual(session.dispatch_count, 0)

    def test_unknown_profile_refuses_before_output_creation(self):
        for profile in ("andon", "CONTROLLED_TASK_FUTURE_V1", None, [], {}):
            with self.subTest(profile=profile), self.assertRaisesRegex(ValueError, "profile"):
                cls = self.A.bind_session(Q.VerifierTaskSession, Q.WG, Q.ROOT, self.helper, profile=profile)
                cls(self.source, self.base / "unexpected")
            self.assertFalse((self.base / "unexpected").exists())

    def test_missing_owner_data_and_byte_overflow_refuse(self):
        path = self.source / DATA[1]
        original = path.read_bytes()
        path.unlink()
        with self.assertRaises((ValueError, OSError)):
            self.snapshot()
        path.write_bytes(b"x" * (256 * 1024 + 1))
        with self.assertRaisesRegex(ValueError, "bound"):
            self.snapshot()
        path.write_bytes(original)

    def test_actual_size_scratch_reservation_and_source_mode_policy(self):
        state, _, _ = self.snapshot()
        reservation = self.A.temporary_requirements(state, profile=PROFILE)
        self.assertEqual(reservation["copies"], 3)
        self.assertEqual(reservation["files"], 9)
        self.assertEqual(reservation["directories"], 16)
        self.assertGreaterEqual(reservation["required_bytes"], 3 * sum(state["files"][name]["bytes"] for name in DATA))
        self.assertEqual(self.A.contract_for(PROFILE)["source_modes"], "PRESERVE_READ_ONLY_MOUNT")
        session = self.session()
        session.LIMITS = dict(session.LIMITS, scratch_bytes=reservation["required_bytes"] - 1)
        with self.assertRaisesRegex(ValueError, "scratch|temporary"):
            session.run()
        self.assertEqual(session.dispatch_count, 0)
        self.assertFalse((session.output / "objects").exists())


class LiveCases(shared.RetainedFixture, unittest.TestCase):
    PROFILE = PROFILE
    LIVE_ENV = "R0035_ANDON_LIVE"
    EVIDENCE_ENV = "R0035_ANDON_EVIDENCE"
    OBJECTS_ENV = "R0035_ANDON_OBJECTS"
    TEST_SOURCE = "tests/work-graph-andon-cases.py"

    def run_original(self, session):
        result = session.run()
        directory = Path(result["evidence_directory"])
        stdout, stderr = ((directory / name).read_bytes() for name in ("stdout.log", "stderr.log"))
        self.assertEqual((directory / "exit-code.txt").read_bytes(), (str(result["exit"]) + "\n").encode())
        receipt = json.loads((directory / "receipt.json").read_bytes())
        self.assertEqual(receipt["node"], "COMMAND:tests/andon-class-contract.test.sh:0")
        self.assertEqual(receipt["scope"], PROFILE)
        self.assertEqual(result["group"]["nodes"], [receipt["node"]])
        self.assertEqual(len(result["group"]["omitted_nodes"]), 116)
        return result, stdout, stderr

    def test_actual_original_positive_internal_negatives_and_reuse(self):
        session = self.session()
        first, stdout, stderr = self.run_original(session)
        self.assertEqual(first["exit"], 0, stderr)
        self.assertEqual(stderr, b"")
        self.assertEqual(stdout, b"andon-class-contract: ok (13 classes, 3 files consistent, 7 boundary fixtures)\nandon-class-contract: negative controls ok (3 mutations rejected)\n")
        second, _, _ = self.run_original(session)
        self.assertEqual((first["disposition"], second["disposition"]), ("EXECUTED", "REUSED"))
        self.assertEqual(first["receipt_digest"], second["receipt_digest"])
        self.assertEqual(session.dispatch_count, 1)
        acquisition = json.loads((session.output / "generation-000001/acquisition.json").read_bytes())
        self.assertEqual(acquisition["source_files"], "PRESERVE_READ_ONLY_MOUNT")
        self.assertEqual(acquisition["startup_umask"], 0o022)
        self.assertLess(acquisition["temporary_reservation"]["required_bytes"], session.LIMITS["scratch_bytes"])

    def test_actual_enumeration_omission_fails_despite_prose_token(self):
        path = self.source / DATA[0]
        text = path.read_text()
        match = re.search(r"`Class:` is an abnormality class.*?\n\n", text, re.S)
        self.assertIsNotNone(match)
        # Current SKILL no longer has the historical prose occurrence mentioned
        # by the original test comment. Supply it explicitly in this private
        # data fixture so the region-vs-whole-file discriminator stays real.
        prose = "\nConstructed prose example: evidence-mismatch.\n"
        outside = text[:match.start()] + text[match.end():] + prose
        self.assertTrue("evidence-mismatch" in outside, "private prose witness is absent")
        region = match.group(0)
        self.assertIn("evidence-mismatch", region)
        path.write_text(text[:match.start()] + region.replace("evidence-mismatch", "", 1) + text[match.end():] + prose)
        session = self.session()
        result, stdout, stderr = self.run_original(session)
        self.assertEqual(result["exit"], 1, stderr)
        self.assertEqual(stdout, b"andon-class-contract: SKILL.md class set diverges from canonical: missing=['evidence-mismatch'] extra=[]\n")
        self.assertEqual(stderr, b"")
        self.assertEqual(session._issued, {})
        with self.assertRaisesRegex(ValueError, "failed or interrupted"):
            session.run()
        self.assertEqual(session.dispatch_count, 1)

    def test_actual_wrong_boundary_classification_fails(self):
        path = self.source / DATA[2]
        text = path.read_text()
        start = text.index("Boundary fixtures")
        row = next(line for line in text[start:].splitlines() if "wrong instance/copy" in line.lower())
        self.assertIn("`misplacement`", row)
        replacement = row.replace("`misplacement`", "`stale-sidecar`", 1)
        path.write_text(text[:start] + text[start:].replace(row, replacement, 1))
        session = self.session()
        result, stdout, stderr = self.run_original(session)
        self.assertEqual(result["exit"], 1, stderr)
        self.assertEqual(stdout, b"andon-class-contract: fixture row 'wrong instance/copy' does not classify as misplacement\n")
        self.assertEqual(stderr, b"")
        self.assertEqual(session._issued, {})

    def test_actual_child_mask_discriminates_fixed_startup(self):
        """Real component control; its synthetic command earns no node credit."""
        observer_mask = subprocess.check_output(["/usr/bin/bash", "--noprofile", "--norc", "-c", "umask"], env=P.ENVIRONMENT)
        (self.base / "observer-umask.log").write_bytes(observer_mask)
        session = self.session()
        acquired = session._acquire()
        original_node = acquired["node"]["id"]
        control = dict(id="CONSTRUCTED:finite-startup-umask", source="umask\n", source_sha256=Q.sha(b"umask\n"))
        real_popen = subprocess.Popen
        def launch(argv, **kwargs):
            self.assertEqual(argv[0], "/usr/bin/bwrap")
            return real_popen(argv, **dict(kwargs, umask=0o077))
        for fixed in (False, True):
            files = dict(acquired["images"][original_node][0])
            wrapper = (b'#!/usr/bin/bash\n' + (b'umask 022\n' if fixed else b'') +
                       b'exec /usr/bin/python3.12 -P -S -B "$@"\n')
            for name in ("/usr/bin/python", "/usr/bin/python3"):
                files[name] = (wrapper, 0o555)
            manifest, image_key = session._image(files, dict(purpose="CONSTRUCTED_STARTUP_CONTROL_NOT_ORIGINAL_NODE"))
            record = dict(state=acquired["state"], images={control["id"]: (files, manifest)},
                acquired=dict(scope="CONSTRUCTED_FINITE_STARTUP_CONTROL_V1",
                              inputs={control["id"]: dict(image_digest=image_key)}))
            directory = session.output / ("startup-fixed" if fixed else "startup-inherited")
            with mock.patch.object(subprocess, "Popen", side_effect=launch):
                receipt, _ = Q.VerifierTaskSession._execute(session, record, control, {"key": image_key}, directory)
            self.assertEqual(receipt["exit"], 0, (directory / "stderr.log").read_bytes())
            self.assertEqual((directory / "stdout.log").read_bytes(), b"0022\n" if fixed else b"0077\n")
            self.assertEqual((directory / "exit-code.txt").read_bytes(), b"0\n")
            (directory / "control.json").write_text(json.dumps(dict(
                purpose="CONSTRUCTED_STARTUP_INTERFACE_NOT_ORIGINAL_NODE_QUALIFICATION",
                actual_launch_umask=0o077, wrapper_sha256=Q.sha(wrapper), fixed_umask=0o022 if fixed else None,
                original_command_unchanged=True, authority="NONE"), sort_keys=True) + "\n")
        self.assertEqual(session._issued, {}, "component controls must never issue original-node reuse")


if __name__ == "__main__":
    unittest.main()
