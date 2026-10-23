#!/usr/bin/env python3
"""Focused value-level regressions for the existing audit-implement child."""

import copy
import hashlib
import json
import os
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "skills/implementaudit/scripts/validate-audit-implement-return.py"
CHILD = ROOT / "skills/audit-implement/SKILL.md"
VERSION = "implementaudit.evidential-support.v2"
RELEASE = "REALISED_IMPLEMENTATION_OR_RELEASE"
NONRELEASE = "NON_RELEASE_PROPOSITION"
SUBPROCESS_CASES = 0


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode()).hexdigest()


def envelope(subject_class=NONRELEASE):
    manifest = [{"evidence_id": "e1", "sha256": "a" * 64,
                 "scope": "the exact observed configuration",
                 "common_source": "laboratory-A", "independence": "one observation"}]
    value = {
        "contract_version": VERSION, "child": "audit-implement",
        "routing_owner": "/implementaudit", "entry": "GOVERNOR",
        "subject_class": subject_class, "semantic_need": "REQUIRED",
        "subject": {"identity": "subject-A", "configuration": "configuration-A",
                    "proposition": "The observation supports the stated boundary.",
                    "boundary": "configuration-A only", "consumer": "governor-A",
                    "consequence": "choose the bounded next evidence request",
                    "decision_time": "2026-10-23T12:00:00Z"},
        "package": {"identity": "executing-package-A", "sha256": "b" * 64},
        "evidence_set": {"identity": "evidence-set-A", "sha256": digest(manifest),
                         "manifest": manifest},
        "claims": [{"claim_id": "c1", "subject_class": subject_class,
                    "proposition": "The observation supports the stated boundary.",
                    "boundary": "configuration-A only", "evidence_ids": ["e1"]}],
        "assumptions": ["The declared configuration is the relevant one."],
        "limitations": ["No broader deployment transport is asserted."],
        "defeaters": [], "unresolved_obligations": [],
        "mechanical": {"identity": "VERIFIED", "hashes": "VERIFIED", "parity": "VERIFIED",
                       "package": "VERIFIED", "reachability": "VERIFIED", "version": "VERIFIED",
                       "authority": "VERIFIED", "custody": "VERIFIED", "writer_conflict": "CLEAR",
                       "required_tests": "SATISFIED", "known_invalidators": "CLEAR"},
        "currentness": {"subject": "VERIFIED", "configuration": "VERIFIED",
                        "evidence_set": "VERIFIED", "consumer": "VERIFIED", "decision_time": "VERIFIED"},
        "release_currentness": "NOT_APPLICABLE", "maintainer_scope": "VERIFIED",
    }
    if subject_class == RELEASE:
        value.update(release_currentness="VERIFIED",
                     candidate={"source": "source-A", "commit": "c" * 40, "tree": "d" * 40,
                                "artifact_sha256": "e" * 64, "package_sha256": "f" * 64,
                                "install": "isolated-install-A", "host": "host-A"})
    return value


def result_for(packet, state="SUPPORTED", legacy=None):
    value = {
        "contract_version": VERSION, "subject_class": packet["subject_class"],
        "envelope_sha256": digest(packet), "authority": "NONE",
        "rationale": "The claim is bounded to the supplied observation and configuration.",
        "limitations": ["Values do not authenticate the observation."],
        "gaps": [], "progression_advice": "The governor must determine its next action.",
    }
    if legacy is not None:
        value["legacy_disposition"] = legacy
    if legacy not in ("stale", "identity mismatch"):
        value["support_state"] = state
        value["claims"] = [{
            "claim_id": claim["claim_id"], "support_state": state,
            "rationale": "The named evidence supports only this claim's declared boundary.",
            "limitations": ["One observation; no independent corroboration."],
            "gaps": ["Missing relevant evidence."] if state == "UNRESOLVED" else [],
            "conditions": ["Verify transport to the named deployment."] if state == "CONDITIONAL" else [],
            "defeaters": ["The observed failure contradicts the claim."] if legacy == "contradicted" else [],
        } for claim in packet["claims"]]
    return value


def snapshot(directory):
    return {p.name: (p.read_bytes() if p.is_file() else None, p.lstat().st_mode, p.lstat().st_mtime_ns)
            for p in directory.iterdir()}


class SubprocessTests(unittest.TestCase):
    def invoke(self, packet=None, result=None, current=None, *, raw=None, code=0, status="VALID"):
        """Every schema expectation executes the actual script, never imports it."""
        global SUBPROCESS_CASES
        self.assertTrue(VALIDATOR.is_file(), "the exact runtime consumer must exist")
        with tempfile.TemporaryDirectory(prefix="evidential-support-") as tmp:
            directory = Path(tmp)
            files = {"envelope": packet if packet is not None else envelope()}
            if result is not None:
                files["result"] = result
                files["current-envelope"] = current if current is not None else files["envelope"]
            args = [str(VALIDATOR)]
            for name, value in files.items():
                path = directory / (name + ".json")
                path.write_text((raw or {}).get(name, json.dumps(value)), encoding="utf-8")
                args.extend(["--" + name, str(path)])
            before = snapshot(directory)
            process = subprocess.run(args, cwd=directory, capture_output=True, text=True, timeout=5)
            SUBPROCESS_CASES += 1
            self.assertEqual(snapshot(directory), before, "validator mutated an input or created a file")
            self.assertEqual(process.returncode, code, process.stdout + process.stderr)
            self.assertEqual(process.stderr, "")
            output = json.loads(process.stdout)
            self.assertEqual(output["status"], status)
            self.assertEqual(output["validation"], "VALUE_VALIDATION")
            self.assertEqual(output["authority"], "NONE")
            self.assertIn("does not authenticate", output["proof_limit"])
            self.assertIn("semantic sufficiency", output["proof_limit"])
            return output

    def reject(self, packet=None, result=None, current=None, *, raw=None):
        return self.invoke(packet, result, current, raw=raw, code=2, status="INVALID")

    def test_help_and_executable(self):
        self.assertEqual(stat.S_IMODE(VALIDATOR.stat().st_mode), 0o755)
        process = subprocess.run([str(VALIDATOR), "--help"], capture_output=True, text=True, timeout=5)
        self.assertEqual(process.returncode, 0)
        for option in ("--envelope", "--result", "--current-envelope"):
            self.assertIn(option, process.stdout)

    def test_both_preload_branches(self):
        for subject_class in (RELEASE, NONRELEASE):
            with self.subTest(subject_class=subject_class):
                packet = envelope(subject_class)
                output = self.invoke(packet)
                self.assertEqual(output["mode"], "PRE_LOAD")
                self.assertEqual(output["envelope_sha256"], digest(packet))

    def test_complete_literal_legacy_mapping(self):
        # Expectations are the issue's literal crosswalk, not the validator's map.
        cases = [("established", "SUPPORTED"), ("contradicted", "NOT_SUPPORTED"),
                 ("insufficient", "UNRESOLVED"), ("qualification gap", "CONDITIONAL"),
                 ("unresolved", "UNRESOLVED"), ("boundary not supportable", "NOT_SUPPORTED")]
        for legacy, state in cases:
            with self.subTest(legacy=legacy):
                packet = envelope(RELEASE)
                output = self.invoke(packet, result_for(packet, state, legacy))
                self.assertEqual(output["mode"], "POST_RETURN")
                wrong = "NOT_SUPPORTED" if state == "SUPPORTED" else "SUPPORTED"
                self.reject(packet, result_for(packet, wrong, legacy))

    def test_legacy_refusals_have_no_semantic_state(self):
        for legacy in ("stale", "identity mismatch"):
            with self.subTest(legacy=legacy):
                packet = envelope(RELEASE)
                result = result_for(packet, legacy=legacy)
                output = self.invoke(packet, result, code=1, status="REFUSED")
                self.assertEqual(output["legacy_disposition"], legacy)
                self.assertNotIn("support_state", output)
                self.reject(packet, dict(result, support_state="UNRESOLVED"))
                self.reject(packet, dict(result, claims=[]))

    def test_all_nonrelease_states(self):
        for state in ("SUPPORTED", "NOT_SUPPORTED", "CONDITIONAL", "UNRESOLVED"):
            with self.subTest(state=state):
                packet = envelope()
                self.invoke(packet, result_for(packet, state))
        packet = envelope()
        packet["evidence_set"]["manifest"] = []
        packet["evidence_set"]["sha256"] = digest([])
        packet["claims"][0]["evidence_ids"] = []
        self.invoke(packet, result_for(packet, "UNRESOLVED"))

    def test_nonrelease_has_no_legacy_disposition(self):
        packet = envelope()
        for legacy in ("established", "contradicted", "insufficient", "qualification gap",
                       "unresolved", "boundary not supportable", "stale", "identity mismatch"):
            with self.subTest(legacy=legacy):
                self.reject(packet, result_for(packet, legacy=legacy))

    def test_unknown_version_state_and_type(self):
        packet = envelope()
        for version in ("implementaudit.evidential-support.v1",
                        "implementaudit.audit-implement.evidential-support.v2", 2, None):
            with self.subTest(version=version):
                self.reject(dict(packet, contract_version=version))
                self.reject(packet, dict(result_for(packet), contract_version=version))
        for state in ("established", "PASS", "not-applicable", "stale", "identity mismatch", None, True):
            with self.subTest(state=state):
                self.reject(packet, dict(result_for(packet), support_state=state))
        self.reject(packet, dict(result_for(packet), subject_class=RELEASE))

    def test_direct_mixed_and_cross_branch_inputs(self):
        packet = envelope()
        for key, value in (("entry", "DIRECT"), ("routing_owner", "audit-implement"),
                           ("child", "audit-assess"), ("subject_class", "MIXED"),
                           ("subject_class", [RELEASE, NONRELEASE])):
            with self.subTest(key=key, value=value):
                self.reject(dict(packet, **{key: value}))
        mixed = copy.deepcopy(packet)
        mixed["claims"][0]["subject_class"] = RELEASE
        self.reject(mixed)
        release = envelope(RELEASE)
        self.reject(dict(release, release_currentness="NOT_APPLICABLE"))
        self.reject(dict(release, release_currentness="STALE"))
        self.reject(dict(release, maintainer_scope="ABSENT"))
        self.reject(dict(packet, release_currentness="VERIFIED"))
        self.reject(dict(packet, candidate=release["candidate"]))

    def test_package_maintainer_admission_applies_to_both_subjects(self):
        for branch in (NONRELEASE, RELEASE):
            packet = envelope(branch)
            missing = dict(packet)
            missing.pop("maintainer_scope", None)
            self.reject(missing)
            self.reject(dict(packet, maintainer_scope="ABSENT"))

    def test_all_mechanical_and_currentness_preconditions(self):
        packet = envelope()
        for key in packet["mechanical"]:
            with self.subTest(mechanical=key):
                bad = copy.deepcopy(packet)
                bad["mechanical"][key] = "FAILED" if key == "required_tests" else "ABSENT"
                self.reject(bad)
        for key in packet["currentness"]:
            with self.subTest(currentness=key):
                bad = copy.deepcopy(packet)
                bad["currentness"][key] = "STALE"
                self.reject(bad)
        for package in ({"identity": "", "sha256": "b" * 64},
                        {"identity": "executing-package-A", "sha256": "wrong-hash"}):
            self.reject(dict(packet, package=package))

    def test_manifest_checksum_and_evidence_references(self):
        packet = envelope()
        bad = copy.deepcopy(packet)
        bad["evidence_set"]["sha256"] = "0" * 64
        self.reject(bad)
        for ids in (["unknown-evidence"], ["e1", "e1"], "e1"):
            bad = copy.deepcopy(packet)
            bad["claims"][0]["evidence_ids"] = ids
            self.reject(bad)
        bad = copy.deepcopy(packet)
        bad["evidence_set"]["manifest"] *= 2
        bad["evidence_set"]["sha256"] = digest(bad["evidence_set"]["manifest"])
        self.reject(bad)

    def test_exact_keys_and_authority_injection(self):
        packet = envelope()
        self.reject(dict(packet, authority="MERGE"))
        self.reject(packet, dict(result_for(packet), authority="RELEASE"))
        self.reject(packet, dict(result_for(packet), global_pass=True))
        for section in ("subject", "package", "evidence_set", "mechanical", "currentness"):
            bad = copy.deepcopy(packet)
            bad[section]["authority"] = "NONE"
            self.reject(bad)
        bad_result = result_for(packet)
        bad_result["claims"][0]["authority"] = "NONE"
        self.reject(packet, bad_result)
        for key in ("subject", "package", "claims", "currentness"):
            bad = copy.deepcopy(packet)
            del bad[key]
            self.reject(bad)

    def test_claim_structure_and_qualification_conditions(self):
        packet = envelope()
        self.reject(dict(packet, claims=[]))
        self.reject(dict(packet, claims=packet["claims"] * 2))
        for key, value in (("claims", []), ("rationale", ""), ("gaps", "none")):
            self.reject(packet, dict(result_for(packet), **{key: value}))
        for key, value in (("claim_id", "wrong-claim"), ("rationale", ""),
                           ("support_state", "UNKNOWN"), ("conditions", ["hidden condition"])):
            bad = result_for(packet)
            bad["claims"][0][key] = value
            self.reject(packet, bad)
        for subject_class, legacy in ((NONRELEASE, None), (RELEASE, "qualification gap")):
            conditional_packet = envelope(subject_class)
            conditional = result_for(conditional_packet, "CONDITIONAL", legacy)
            conditional["claims"][0]["conditions"] = []
            self.reject(conditional_packet, conditional)
        release = envelope(RELEASE)
        contradiction = result_for(release, "NOT_SUPPORTED", "contradicted")
        contradiction["claims"][0]["defeaters"] = []
        self.reject(release, contradiction)

    def test_conservative_multiclaim_summary(self):
        packet = envelope()
        packet["claims"].append(dict(packet["claims"][0], claim_id="c2"))
        result = result_for(packet)
        result["claims"][1].update(support_state="CONDITIONAL", conditions=["Qualify deployment transport."])
        self.reject(packet, result)
        result["support_state"] = "CONDITIONAL"
        self.invoke(packet, result)
        result["claims"][0].update(support_state="UNRESOLVED", gaps=["Missing independent evidence."])
        self.reject(packet, result)
        result["support_state"] = "UNRESOLVED"
        self.invoke(packet, result)

    def test_post_child_subject_evidence_package_and_candidate_drift(self):
        packet = envelope()
        result = result_for(packet)
        for key in packet["subject"]:
            with self.subTest(subject=key):
                current = copy.deepcopy(packet)
                current["subject"][key] = "2026-10-23T12:01:00Z" if key == "decision_time" else "changed"
                output = self.reject(packet, result, current)
                self.assertIn("envelope drift", output["error"])
        for section, key, value in (("package", "identity", "package-B"),
                                    ("package", "sha256", "1" * 64),
                                    ("evidence_set", "identity", "evidence-set-B")):
            current = copy.deepcopy(packet)
            current[section][key] = value
            self.reject(packet, result, current)
        current = copy.deepcopy(packet)
        current["evidence_set"]["manifest"][0]["sha256"] = "2" * 64
        current["evidence_set"]["sha256"] = digest(current["evidence_set"]["manifest"])
        self.reject(packet, result, current)
        release = envelope(RELEASE)
        current = copy.deepcopy(release)
        current["candidate"]["commit"] = "3" * 40
        self.reject(release, result_for(release, legacy="established"), current)
        self.reject(packet, dict(result, envelope_sha256="4" * 64))

    def test_drift_and_preconditions_precede_reading_result(self):
        packet = envelope()
        current = copy.deepcopy(packet)
        current["subject"]["identity"] = "changed"
        output = self.reject(packet, result_for(packet), current, raw={"result": "not even JSON"})
        self.assertIn("envelope drift", output["error"])
        bad = copy.deepcopy(packet)
        bad["mechanical"]["required_tests"] = "FAILED"
        output = self.reject(bad, result_for(packet), raw={"result": "not even JSON"})
        self.assertIn("required_tests", output["error"])

    def test_mechanically_settled_and_ordinary_work_bypass(self):
        for need in ("MECHANICALLY_SETTLED", "ORDINARY_REVERSIBLE"):
            with self.subTest(need=need):
                packet = dict(envelope(), semantic_need=need)
                self.invoke(packet, status="BYPASS")
                self.reject(packet, result_for(packet))
        self.reject(dict(envelope(), semantic_need="SHOULD_I_PROCEED"))

    def test_duplicate_json_and_nonstandard_constants(self):
        packet = envelope()
        duplicates = json.dumps(packet)[:-1] + ',"entry":"GOVERNOR"}'
        self.reject(packet, raw={"envelope": duplicates})
        nested = json.dumps(packet).replace('"identity": "subject-A"',
                                           '"identity":"subject-A","identity":"subject-A"')
        self.reject(packet, raw={"envelope": nested})
        result = result_for(packet)
        duplicate_result = json.dumps(result)[:-1] + ',"authority":"NONE"}'
        self.reject(packet, result, raw={"result": duplicate_result})
        self.reject(packet, result, raw={"current-envelope": duplicates})
        self.reject(packet, raw={"envelope": json.dumps(packet).replace('"entry": "GOVERNOR"', '"entry": NaN')})

    def test_no_input_execution_or_mutation(self):
        packet = envelope()
        with tempfile.TemporaryDirectory(prefix="evidential-nonexecution-") as tmp:
            marker = Path(tmp) / "must-not-exist"
            result = result_for(packet)
            result["progression_advice"] = '$(touch "' + str(marker) + '"); __import__("os").system("touch ' + str(marker) + '")'
            self.invoke(packet, result)
            self.assertFalse(marker.exists(), "input was executed")

    def test_bounded_regular_file_reads(self):
        with tempfile.TemporaryDirectory(prefix="evidential-files-") as tmp:
            directory = Path(tmp)
            valid = directory / "valid.json"
            valid.write_text(json.dumps(envelope()), encoding="utf-8")
            huge = directory / "huge.json"
            huge.write_bytes(b" " * 131073)
            invalid_utf8 = directory / "invalid-utf8.json"
            invalid_utf8.write_bytes(b"\xff")
            symlink = directory / "link.json"
            symlink.symlink_to(valid)
            fifo = directory / "fifo"
            os.mkfifo(fifo)
            for path in (directory, huge, invalid_utf8, symlink, fifo, directory / "absent"):
                with self.subTest(path=path.name):
                    process = subprocess.run([str(VALIDATOR), "--envelope", str(path)],
                                             capture_output=True, text=True, timeout=5)
                    self.assertEqual(process.returncode, 2, process.stdout + process.stderr)
                    self.assertEqual(json.loads(process.stdout)["status"], "INVALID")
            self.reject(raw={"envelope": "[" * 2000 + "]" * 2000})
            self.reject(dict(envelope(), assumptions=["x" * 4097]))

    def test_cli_requires_the_fresh_envelope_pair(self):
        for args in (["--envelope", "unused", "--result", "unused"],
                     ["--envelope", "unused", "--current-envelope", "unused"]):
            process = subprocess.run([str(VALIDATOR), *args], capture_output=True, text=True, timeout=5)
            self.assertEqual(process.returncode, 2)
            self.assertIn("paired", process.stderr)


class ExactContractTests(unittest.TestCase):
    def test_exact_consumer_exists(self):
        self.assertTrue(
            VALIDATOR.is_file(),
            "R0033 exact v2 consumer is absent; a donor or test-local predicate is not it",
        )

    def test_exact_same_child_contract(self):
        text = CHILD.read_text(encoding="utf-8")
        required = (
            "implementaudit.evidential-support.v2",
            "SUBJECT_CLASS=REALISED_IMPLEMENTATION_OR_RELEASE",
            "SUBJECT_CLASS=NON_RELEASE_PROPOSITION",
            "SUPPORTED|NOT_SUPPORTED|CONDITIONAL|UNRESOLVED",
            "legacy_disposition",
        )
        missing = [token for token in required if token not in text]
        self.assertEqual(missing, [], "current child contract is not the accepted exact v2 contract")


if __name__ == "__main__":
    suite = unittest.main(verbosity=2, exit=False)
    print("SCHEMA_SUBPROCESS_CASES=" + str(SUBPROCESS_CASES))
    raise SystemExit(0 if suite.result.wasSuccessful() else 1)
