"""Constructed captured-file controls; no native producer or receiving evidence.

The original 24-test portable bank remains unchanged. These controls exercise
the additional explicit consumer on the same primary/companion pair.
"""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(sys.argv.pop(1)).resolve()
SCRIPT = ROOT / "skills/implementaudit/scripts/operational-evidence.py"
spec = importlib.util.spec_from_file_location("captured_oe", SCRIPT)
oe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(oe)


def public_input():
    issue = {"id": 214000, "number": 214, "title": "R0038 — constructed contract",
             "state": "open", "state_reason": None, "body": "Contract body\n",
             "comments": 1, "created_at": "2026-01-01T00:00:00Z",
             "updated_at": "2026-01-02T00:00:00Z",
             "url": "https://github.com/fixture/project/issues/214"}
    comment = {"id": 101, "body": "Binding comment\n",
               "created_at": "2026-01-02T00:00:00Z", "updated_at": "2026-01-02T00:00:00Z",
               "issue_url": "https://api.github.com/repos/fixture/project/issues/214",
               "html_url": "https://github.com/fixture/project/issues/214#issuecomment-101",
               "url": "https://api.github.com/repos/fixture/project/issues/comments/101"}
    return {"schema": "implementaudit.public-census-input.v1", "repository": "fixture/project",
            "declared_members": [{"id": 214000, "number": 214}], "issues": [issue],
            "comments": [{"issue_number": 214, "pages": [[comment]]}]}


class CapturedConsumerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)

    def tearDown(self):
        self.temp.cleanup()

    def capture(self, value=None, kind="public-census"):
        source = self.root / "captured.json"
        source.write_text(json.dumps(public_input() if value is None else value, indent=2), encoding="utf-8")
        return oe.observe_captured_snapshot_v1(kind, source)

    def test_explicit_cli_capture_and_inspect_without_native_selection(self):
        source = self.root / "input.json"
        source.write_text(json.dumps(public_input()))
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), "capture", "public-census", str(source)],
                                capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        target = self.root / "snapshot.json"
        target.write_bytes(result.stdout)
        inspected = subprocess.run([sys.executable, "-B", str(SCRIPT), "inspect", str(target),
                                    "--family", "RELEASE"], capture_output=True)
        self.assertEqual(inspected.returncode, 0, inspected.stderr.decode())
        self.assertEqual(json.loads(inspected.stdout)["acquisition_scope"], "CAPTURED_OWNER_UNAUTHENTICATED_FILE")

    def test_public_body_comment_and_membership_are_separate_and_complete(self):
        value = self.capture()
        self.assertEqual(value["families"], list(oe.FAMILIES))
        self.assertEqual(value["aggregate"], "DEGRADED")
        rows = [row["record"] for row in oe.query_family(value, "RELEASE")["rows"]]
        self.assertEqual({r["record_type"] for r in rows}, {"PublicContract", "PublicComment", "PublicCensus"})
        self.assertTrue(all(r["currentness"]["state"] == "UNVERIFIED" and r["establishes"] == [] for r in rows))
        census = next(r["observation"] for r in rows if r["record_type"] == "PublicCensus")
        self.assertEqual((census["declared"], census["observed_issues"], census["observed_comments"]), (1, 1, 1))
        self.assertIsNone(census["authoritative_admission"])
        self.assertIsNone(census["original_property_membership"])

    def test_changed_body_comment_identity_and_diff_are_preserved(self):
        before = self.capture()
        changed = public_input()
        changed["issues"][0]["body"] += "Amended\n"
        changed["comments"][0]["pages"][0][0]["body"] += "Changed\n"
        after = self.capture(changed)
        diff = oe.diff_snapshots(before, after)
        self.assertGreater(diff["counts"]["changed"], 0)
        before_rows = {r["record"]["id"]: r["record"] for r in oe.query_family(before, "RELEASE")["rows"]}
        after_rows = {r["record"]["id"]: r["record"] for r in oe.query_family(after, "RELEASE")["rows"]}
        self.assertEqual(set(before_rows), set(after_rows))
        for key in before_rows:
            if before_rows[key]["record_type"] in ("PublicContract", "PublicComment"):
                self.assertNotEqual(before_rows[key]["observation"]["body_sha256"], after_rows[key]["observation"]["body_sha256"])

    def test_missing_comments_are_explicit_and_retained_issues_stay_accessible(self):
        value = public_input()
        value["comments"] = []
        captured = self.capture(value)
        self.assertIn("COMMENTS_NOT_CAPTURED", {r["code"] for r in captured["missing_or_omitted_state"]})
        self.assertTrue(oe.query_family(captured, "RELEASE")["rows"])
        self.assertEqual(oe.query_family(captured, "RELEASE", True)["rows"], [])

    def test_public_duplicates_wrong_urls_and_scalar_lies_refuse(self):
        variants = []
        duplicate = public_input(); duplicate["issues"].append(copy.deepcopy(duplicate["issues"][0])); variants.append(duplicate)
        duplicate = public_input(); duplicate["comments"][0]["pages"][0] *= 2; variants.append(duplicate)
        wrong = public_input(); wrong["comments"][0]["pages"][0][0]["issue_url"] += "0"; variants.append(wrong)
        wrong = public_input(); wrong["issues"][0]["comments"] = True; variants.append(wrong)
        for value in variants:
            with self.subTest(value=value):
                with self.assertRaises(oe.OperationalEvidenceError) as raised:
                    self.capture(value)
                self.assertEqual(raised.exception.code, "OE_CAPTURE_INVALID")

    def test_snapshot_tampering_and_scope_widening_refuse(self):
        value = self.capture()
        for key, changed in (("aggregate", "COMPLETE"), ("scope", "NATIVE_CURRENT"),
                             ("missing_or_omitted_state", [])):
            forged = copy.deepcopy(value); forged[key] = changed
            with self.subTest(key=key), self.assertRaises(oe.OperationalEvidenceError):
                oe.query_family(forged, "RELEASE")
        forged = copy.deepcopy(value)
        forged["collections"]["captured_owner"]["input_text"] += " "
        with self.assertRaises(oe.OperationalEvidenceError):
            oe.diff_snapshots(value, forged)

    def test_query_why_render_diff_have_zero_refresh_and_explicit_bounds(self):
        value = self.capture()
        with patch.object(oe, "collect_native_current", side_effect=AssertionError("native acquisition")), \
                patch.object(subprocess, "run", side_effect=AssertionError("subprocess")), \
                patch.object(socket, "socket", side_effect=AssertionError("network")):
            rows = oe.query_family(value, "RELEASE")["rows"]
            self.assertEqual(oe.diff_snapshots(value, value)["counts"], {"added": 0, "removed": 0, "changed": 0})
            oe.explain_history_why_v1(value, rows[0]["record"]["id"])
            for mode in ("table", "graph"):
                rendered = oe.render_snapshot_projection_v1(value, output_format=mode, max_rows=100, max_bytes=262144)
                self.assertTrue(rendered)
            bounded = oe._bounded_query_result_v1(oe.query_family(value, "RELEASE"), 1, 262144)
            self.assertTrue(bounded["truncated"])
            self.assertEqual(bounded["population_count"], 3)
            self.assertFalse(bounded["decision_usable"])

    def test_explicit_reader_rejects_symlink_hardlink_duplicate_json_and_unknown_kind(self):
        source = self.root / "source.json"
        source.write_text(json.dumps(public_input()))
        link = self.root / "link.json"; link.symlink_to(source)
        with self.assertRaises(oe.OperationalEvidenceError):
            oe.observe_captured_snapshot_v1("public-census", link)
        hard = self.root / "hard.json"; hard.hardlink_to(source)
        with self.assertRaises(oe.OperationalEvidenceError):
            oe.observe_captured_snapshot_v1("public-census", hard)
        hard.unlink()
        source.write_text('{"schema":"x","schema":"y"}')
        with self.assertRaises(oe.OperationalEvidenceError):
            oe.observe_captured_snapshot_v1("public-census", source)
        with self.assertRaises(oe.OperationalEvidenceError):
            oe.observe_captured_snapshot_v1("invented-sensor", source)

    def test_malformed_captured_member_types_have_typed_refusals(self):
        captured = self.capture()
        for malformed in (0, None, [], {}):
            changed = copy.deepcopy(captured)
            changed["collections"]["captured_owner"]["input_text"] = malformed
            with self.subTest(value=malformed):
                with self.assertRaises(oe.OperationalEvidenceError) as caught:
                    oe.query_family(changed, "RELEASE")
                self.assertEqual(caught.exception.code, "OE_DIFF_SNAPSHOT_INVALID")

    def test_named_root_directory_has_typed_unreadable_refusal(self):
        with self.assertRaises(oe.OperationalEvidenceError) as caught:
            oe.observe_captured_snapshot_v1("public-census", Path(self.root.anchor))
        self.assertEqual(caught.exception.code, "OE_CAPTURE_INPUT_UNREADABLE")

    def test_duplicate_surrogate_key_has_serializable_typed_cli_refusal(self):
        source = self.root / "duplicate-surrogate.json"
        source.write_bytes(b'{"\\ud800":0,"\\ud800":1}')
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), "capture", "public-census", str(source)],
                                capture_output=True)
        error = json.loads(result.stderr)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(error["code"], "OE_CAPTURE_INVALID")
        self.assertEqual(result.stdout, b"")


if __name__ == "__main__":
    unittest.main()
