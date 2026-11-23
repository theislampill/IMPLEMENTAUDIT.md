"""Focused POSIX controls for the inactive verifier property capture and comparison."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE = ROOT / "scripts/qualify-work-graph-verifier-properties.py"
CHECKER = "scripts/check-validation-registry.sh"
REGISTRY = "scripts/verify-package.sh"
WORKFLOW = ".github/workflows/validate.yml"
ROUTE = b"        run: bash scripts/verify-package.sh\n"
IMAGE = b"    runs-on: ubuntu-24.04\n"
NODE = "COMMAND:scripts/check-validation-registry.sh:0"
PROPERTIES = {
    "canonical_route_exactly_once",
    "no_direct_ci_test_dispatch",
    "fixed_python_runner_image",
}


class PropertyEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.scratch = self.enterContext(tempfile.TemporaryDirectory())
        self.source = Path(self.scratch) / "source"
        self.receipt = Path(self.scratch) / "candidate.json"
        for name in (CHECKER, REGISTRY, WORKFLOW):
            target = self.source / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(ROOT / name, target)
        (self.source / "tests").mkdir()
        for file in (ROOT / "tests").glob("*.test.sh"):
            (self.source / "tests" / file.name).touch()
        self.workflow = self.source / WORKFLOW
        self.original_workflow = self.workflow.read_bytes()

    def invoke(self, command):
        args = [sys.executable, "-I", "-B", str(CANDIDATE), command, "--repo-root", str(self.source)]
        if command == "compare":
            args.extend(("--receipt", str(self.receipt)))
        return subprocess.run(args, capture_output=True, timeout=20)

    def capture(self):
        result = self.invoke("capture")
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assertEqual(result.stderr, b"")
        self.receipt.write_bytes(result.stdout)
        return json.loads(result.stdout)

    def write(self, record):
        data = json.dumps(record, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        self.receipt.write_bytes(data.encode() + b"\n")

    def compare(self, expected, *, error=""):
        result = self.invoke("compare")
        if error:
            self.assertEqual(result.returncode, 1, result.stderr.decode())
            self.assertEqual(result.stdout, b"")
            self.assertIn(error, result.stderr.decode())
            return
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        compared = json.loads(result.stdout)
        self.assertEqual(compared["relation"], expected)
        self.assertEqual(compared["authority"], "NONE")
        self.assertEqual(compared["population"], "INCOMPLETE_REST_UNQUALIFIED")

    def canonical_checker(self, expected):
        result = subprocess.run(
            ["bash", str(ROOT / CHECKER), "--repo-root", str(self.source)],
            capture_output=True, timeout=10,
        )
        self.assertEqual(result.returncode, expected["exit"])
        self.assertEqual(result.stdout.decode(), expected["stdout"])
        self.assertEqual(result.stderr.decode(), expected["stderr"])

    def test_exact_valid_candidate_and_canonical_raw_checker(self):
        record = self.capture()
        self.assertEqual({row["id"] for row in record["properties"]}, PROPERTIES)
        self.assertEqual(record["node"]["id"], NODE)
        self.assertEqual(record["graph"]["command_stream"]["sha256"],
                         "50a794c866dd2b35cf5f10875c409a8e2347ea13f9ea3fb188582fca7dc6fc28")
        self.assertEqual(record["graph"]["nodes"], 119)
        self.assertEqual(record["node"]["ordinal"], 114)
        self.assertEqual(record["node"]["requires"], ["COMMAND:tests/operational-evidence-portable.test.sh:0"])
        self.assertEqual(record["node"]["writer_resource_constraint"], "SHARED_SHELL_AND_REPOSITORY_SERIAL")
        self.assertEqual(record["scope"]["population"], "INCOMPLETE_REST_UNQUALIFIED")
        self.assertEqual(record["authority"], "NONE")
        self.assertEqual(record["observation"]["exit"], 0)
        self.assertTrue(all(row["observation"] == "NO_OWNER_DIAGNOSTIC" for row in record["properties"]))
        for row in record["properties"]:
            self.assertEqual(row["owner"], CHECKER)
            self.assertEqual(row["node"], NODE)
            self.assertTrue({CHECKER, REGISTRY, WORKFLOW} <= set(row["inputs"]))
            self.assertEqual("tests/*.test.sh" in row["inputs"], row["id"] == "no_direct_ci_test_dispatch")
            self.assertTrue(set(row["inputs"]) <= set(row["invalidated_by"]))
            self.assertEqual(row["output"], {"record_field": "observation", "stderr_lines_1_based": []})
        self.canonical_checker(record["observation"])
        self.compare("SAME_PROSPECTIVE_PROPERTY_EVIDENCE")

    def test_three_distinct_owner_failures_remain_negative_evidence(self):
        variants = {
            "canonical_route_exactly_once": self.original_workflow.replace(ROUTE, ROUTE + ROUTE),
            "no_direct_ci_test_dispatch": self.original_workflow.replace(
                ROUTE, ROUTE + b"        run: bash tests/phase-validation.test.sh\n"),
            "fixed_python_runner_image": self.original_workflow.replace(
                IMAGE, b"    runs-on: ubuntu-latest\n"),
        }
        for prop, data in variants.items():
            with self.subTest(prop=prop):
                self.assertNotEqual(data, self.original_workflow)
                self.workflow.write_bytes(data)
                record = self.capture()
                self.assertEqual(record["observation"]["exit"], 1)
                failures = [row for row in record["properties"]
                            if row["observation"] == "OWNER_DIAGNOSTIC_OBSERVED"]
                self.assertEqual([row["id"] for row in failures], [prop])
                self.assertEqual(failures[0]["output"]["stderr_lines_1_based"], [1])
                self.canonical_checker(record["observation"])
                self.compare("SAME_PROSPECTIVE_PROPERTY_EVIDENCE")

    def test_fixed_python_condition_can_be_inactive(self):
        self.workflow.write_bytes(self.original_workflow.replace(
            b"/usr/bin/python3.12", b"/usr/bin/python").replace(IMAGE, b"    runs-on: ubuntu-latest\n"))
        record = self.capture()
        image = next(row for row in record["properties"] if row["id"] == "fixed_python_runner_image")
        self.assertEqual(image["observation"], "CONDITION_NOT_APPLICABLE")
        self.canonical_checker(record["observation"])
        self.compare("SAME_PROSPECTIVE_PROPERTY_EVIDENCE")

    def test_comparator_refuses_missing_extra_duplicate_and_reordered(self):
        record = self.capture()
        original = record["properties"]
        variants = {
            "missing or extra": original[:-1],
            "duplicate": original[:2] + original[:1],
            "order": original[::-1],
        }
        for error, properties in variants.items():
            with self.subTest(error=error):
                record["properties"] = properties
                self.write(record)
                self.compare(None, error=error)
        record["properties"] = original + [dict(original[0], id="foreign")]
        self.write(record)
        self.compare(None, error="missing or extra")

    def test_same_semantics_workflow_byte_change_invalidates_receipt(self):
        self.capture()
        self.workflow.write_bytes(self.original_workflow + b"\n# ordinary textual edit\n")
        self.compare(None, error="stale or altered")

    def test_tampered_observation_and_dependency_binding_are_refused(self):
        for change in ("output", "dependency"):
            with self.subTest(change=change):
                record = self.capture()
                if change == "output":
                    record["observation"]["exit"] = False
                else:
                    record["node"]["requires"].clear()
                self.write(record)
                self.compare(None, error="stale or altered")

    def test_altered_checker_and_nonordinary_member_are_refused(self):
        checker = self.source / CHECKER
        checker.write_bytes(checker.read_bytes() + b"\n")
        result = self.invoke("capture")
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, b"")
        self.assertIn(b"unsupported source pin", result.stderr)
        shutil.copyfile(ROOT / CHECKER, checker)
        member = self.source / "tests/phase-validation.test.sh"
        member.unlink()
        member.mkdir()
        result = self.invoke("capture")
        self.assertEqual(result.returncode, 1)
        self.assertIn(b"ordinary file", result.stderr)

    def test_duplicate_json_key_and_excessive_receipt_are_refused(self):
        self.capture()
        raw = self.receipt.read_bytes()
        self.receipt.write_bytes(b'{"authority":"NONE",' + raw[1:])
        self.compare(None, error="duplicate key")
        self.receipt.write_bytes(b" " * (256 * 1024 + 1))
        self.compare(None, error="byte limit")


if __name__ == "__main__":
    unittest.main()
