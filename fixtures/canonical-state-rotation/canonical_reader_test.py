#!/usr/bin/env python3
"""Read-only adapter controls in disposable Git repositories; no native-host claim."""
from __future__ import annotations

import hashlib
import ast
import importlib.util
import json
import os
from pathlib import Path
import shutil
import re
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "skills/implementaudit/scripts"
CONTROLLER = "canonical-reader-test"


def command(argv, cwd, data=None):
    if os.name == "nt" and argv[0] == "bash":
        argv = [r"C:\Program Files\Git\bin\bash.exe", *argv[1:]]
    env = {key: value for key, value in os.environ.items()
           if not key.startswith(("GIT_", "IMPLEMENTAUDIT_"))}
    env.update(PYTHONDONTWRITEBYTECODE="1", LC_ALL="C")
    return subprocess.run([str(x) for x in argv], cwd=cwd, input=data,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env)


class CanonicalReaderTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="reader-", dir=ROOT / "fixtures/canonical-state-rotation")
        self.addCleanup(self.temporary.cleanup)
        self.repo = Path(self.temporary.name)
        self.scripts = self.repo / "skills/implementaudit/scripts"
        shutil.copytree(SCRIPTS, self.scripts)
        shutil.copytree(ROOT / "skills/implementaudit/templates", self.scripts.parent / "templates")
        self.git("init", "-q")
        self.git("config", "user.name", "constructed canonical reader")
        self.git("config", "user.email", "canonical-reader@example.invalid")
        (self.repo / "fixture.txt").write_text("Constructed reader subject.\n")
        self.git("add", "fixture.txt")
        self.git("-c", "commit.gpgsign=false", "commit", "-qm", "constructed reader subject")
        claimed = self.claim("--controller", CONTROLLER, "canonical reader")
        self.assertEqual(claimed.returncode, 0, claimed.stderr.decode())
        self.run = self.repo / claimed.stdout.decode().strip()
        for name in ("STATE.md", "ROADMAP.md", "PROTOCOL.md", "THINKING.md", "sidecars.md", "tools.md", "context.md"):
            shutil.copyfile(self.scripts.parent / "templates" / name, self.run / name)
        (self.run / "phases").mkdir()
        (self.run / "phases/phase-1.md").write_text("open fixture phase\n")
        self.output = self.repo / "read-output"
        self.output.mkdir()

    def git(self, *args, data=None):
        result = command(["git", *args], self.repo, data)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        return result.stdout.decode().strip()

    def claim(self, *args):
        return command(["bash", self.scripts / "claim-run.sh", *args], self.repo)

    def validate(self):
        return command(["bash", self.scripts / "validate-run-root.sh", self.run], self.repo)

    def read(self, *args):
        return command([sys.executable, "-B", self.scripts / "read-canonical-pair.py",
                        "--run-root", self.run, "--output", self.output, *args], self.repo)

    def put_ref(self, role, data=b"malformed canonical authority\n"):
        oid = self.git("hash-object", "-w", "--stdin", data=data)
        self.git("update-ref", f"refs/implementaudit/{role}/{CONTROLLER}", oid)

    def test_legacy_structural_validation_preserves_original_guards(self):
        self.assertEqual(self.validate().returncode, 0)
        path = self.run / "STATE.md"
        path.write_text(path.read_text().replace("## Andon log", "## Removed native Andon log"))
        result = self.validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"Andon log", result.stderr)

    def test_present_broken_marker_never_reads_valid_root_compatibility_pair(self):
        self.assertEqual(self.validate().returncode, 0)
        self.put_ref("current-generation-migrations")
        result = self.validate()
        self.assertNotEqual(result.returncode, 0, "native validator accepted stale root pair around a present marker")

    def test_present_broken_pointer_never_reads_valid_root_compatibility_pair(self):
        self.put_ref("current-generations")
        self.assertNotEqual(self.validate().returncode, 0, "native validator ignored a malformed pointer")

    def test_missing_controller_hint_cannot_hide_migrated_v2_claim(self):
        self.put_ref("current-generation-migrations")
        (self.run / ".controller").unlink()
        self.assertNotEqual(self.validate().returncode, 0, "deleted discovery hint re-enabled legacy root validation")

    def test_missing_controller_record_and_hint_cannot_hide_a_retained_marker(self):
        self.put_ref("current-generation-migrations")
        (self.run / ".controller").unlink()
        self.git("update-ref", "-d", f"refs/implementaudit/controllers/{CONTROLLER}")
        self.assertNotEqual(self.validate().returncode, 0, "retained marker disappeared from missing-hint discovery")

    def test_unbound_legacy_v2_claim_keeps_its_original_structural_path(self):
        (self.run / ".controller").unlink()
        self.git("update-ref", "-d", f"refs/implementaudit/controllers/{CONTROLLER}")
        result = self.validate()
        self.assertEqual(result.returncode, 0, result.stderr.decode())

    def test_symlink_controller_hint_refuses_without_following_it(self):
        hint = self.run / ".controller"
        outside = self.repo / "outside-controller"
        hint.rename(outside)
        hint.symlink_to(outside)
        self.assertNotEqual(self.validate().returncode, 0, "linked discovery hint was admitted")

    def test_adapter_exit_three_means_native_authorities_absent(self):
        result = self.read()
        self.assertEqual(result.returncode, 3, result.stderr.decode())
        self.assertEqual(list(self.output.iterdir()), [], "legacy preflight wrote a current projection")

    def write_phase(self):
        path = self.run / "phases/phase-1.md"
        text = (ROOT / "fixtures/run-root-example/phases/phase-1.md").read_text()
        text = text.replace("Task: fix greeting casing in app.txt", "Phase: 1\nTask: fix greeting casing in app.txt")
        text = re.sub(r"(?m)^Run root:.*$", "Run root: " + self.run.relative_to(self.repo).as_posix(), text)
        text = text.replace("In scope: app.txt", 'In scope: app.txt\nMutation scope: {"in":["app.txt"],"out":[]}')
        text = text.replace("expected: exit 0\n", 'expected: exit 0\n  mutation-authority: {"operation":"replace","source":"app.txt","destination":null}\n', 1)
        path.write_text(text)
        return path

    def phase_authority(self):
        path = self.write_phase()
        return command(["bash", self.scripts / "validate-phase.sh", "--mutation-authority", path,
                        "--phase", "1", "--step", "1", "--repo-root", self.repo, "--run-root", self.run], self.repo)

    def test_phase_authority_retains_legacy_guards_and_rejects_broken_migration(self):
        result = self.phase_authority()
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.put_ref("current-generation-migrations")
        self.assertNotEqual(self.phase_authority().returncode, 0, "phase authority used a retired ROADMAP")

    def make_real_generation(self, *, native=False, state_edit=None, roadmap_edit=None, extra_artifacts=None):
        factory_path = ROOT / "fixtures/canonical-state-rotation/protected_projection_v2_test.py"
        spec = importlib.util.spec_from_file_location("canonical_reader_factory", factory_path)
        factory = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(factory)
        source = json.loads((factory_path.parent / "v2/source.json").read_text())
        bodies = source["bodies"]
        claim = dict(line.split("=", 1) for line in (self.run / ".claimed").read_text().splitlines())
        identity = bodies["STATE"]["payload"]["identity"]["value"]
        identity.update(controller_id=CONTROLLER, claim_id=claim["claim_id"],
                        run_root_identity=self.run.relative_to(self.repo).as_posix(),
                        candidate=self.git("rev-parse", "HEAD"), tree=self.git("rev-parse", "HEAD^{tree}"))
        receipt_ref = f"refs/implementaudit/continuity-receipts/{CONTROLLER}/G0001"
        for role in ("STATE", "ROADMAP"):
            bodies[role]["continuity"].update(boundary="new-session", invalidation_oid=None,
                                               expected_receipt_ref=receipt_ref)
            for item in bodies[role]["artifact_refs"]:
                if item["role"] == "CONTINUITY_RECEIPT":
                    item["locator"] = receipt_ref
        artifacts = {key: text.encode() for key, text in source["artifact_texts"].items()}
        if native:
            self.write_phase()
            continuation = bodies["STATE"]["payload"]["continuation"]["value"]
            continuation.update(status="IN_PHASE", phase="1")
            native_state = (self.run / "STATE.md").read_text().replace("| Status | open |", "| Status | IN_PHASE |")
            native_state = native_state.replace("| Next action |  |", "| Next action | " + continuation["next_action"] + " |")
            native_state = re.sub(r"(?m)^Current epoch:.*\n", "", native_state)
            native_roadmap = (self.run / "ROADMAP.md").read_text()
            if state_edit:
                native_state = state_edit(native_state)
            if roadmap_edit:
                native_roadmap = roadmap_edit(native_roadmap)
            self.native_source = {"STATE": native_state, "ROADMAP": native_roadmap}
            for role, text in self.native_source.items():
                bodies[role]["payload"]["native_guards"] = {"owner": role + ".md", "value": {
                    "schema_version": "implementaudit.native-guard-profile.v1", "lines": text.splitlines()}}
            for name, data in (extra_artifacts or {}).items():
                path = self.run / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            native_files = sorted(path for path in self.run.rglob("*") if path.is_file()
                                  and path.name not in {"STATE.md", "ROADMAP.md", ".claimed", ".controller"})
            for index, path in enumerate(native_files):
                artifact_id = "native-" + str(index)
                locator = path.relative_to(self.run).as_posix()
                bodies["ROADMAP"]["artifact_refs"].append({"artifact_id": artifact_id, "owner": "ROADMAP.md",
                    "role": "EVIDENCE", "locator": locator, "object_format": "sha1"})
                bodies["STATE"]["payload"]["runtime_artifacts"]["value"].append(artifact_id)
                artifacts[artifact_id] = path.read_bytes()
        bodies["STATE"]["history"][0]["payload"]["text"] += " Exact constructed historical observation." * 6500
        pair = factory.render_pair(bodies)
        for role, data in pair.items():
            (self.run / (role + ".md")).write_bytes(data)
        receipt = self.claim("--resume-controller", CONTROLLER, "--boundary", "new-session", "--epoch", "G0001")
        self.assertEqual(receipt.returncode, 0, receipt.stderr.decode())
        artifacts["receipt"] = command(["git", "cat-file", "blob", receipt.stdout.decode().strip().split("@")[1]], self.repo).stdout
        for body in bodies.values():
            for item in body["artifact_refs"]:
                if item["role"] != "CONTINUITY_RECEIPT":
                    path = self.run / item["locator"]
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(artifacts[item["artifact_id"]])
        owner_map = self.run / "owner-map.json"
        owner_map.write_text(json.dumps({"schema": "implementaudit.rotation-owner-map.v2",
                                        "owner_map": factory.build_owner_map(bodies, pair, artifacts)},
                                       sort_keys=True, separators=(",", ":")))
        result = self.claim("--rotate-canonical-state", CONTROLLER, "--owner-map", owner_map)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.preimage_bodies = bodies
        return json.loads(self.claim("--resolve-canonical-generation", CONTROLLER).stdout)

    def test_real_generation_read_binds_exact_pair_and_never_changes_root(self):
        resolved = self.make_real_generation()
        original = {role: (self.run / (role + ".md")).read_bytes() for role in ("STATE", "ROADMAP")}
        result = self.read()
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        for role in ("STATE", "ROADMAP"):
            actual = (self.output / (role + ".md")).read_bytes()
            self.assertEqual(actual, Path(resolved[role.lower() + "_path"]).read_bytes())
            self.assertEqual(hashlib.sha256(actual).hexdigest(), resolved["pointer"][role.lower() + "_sha256"])
            self.assertEqual((self.run / (role + ".md")).read_bytes(), original[role])
        self.assertEqual(json.loads((self.output / "resolution.json").read_bytes()), resolved)

    def test_current_typed_pair_cannot_bypass_unmapped_native_validator_guards(self):
        self.make_real_generation()
        result = self.validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"CANONICAL_NATIVE_GUARD_PROFILE_UNSUPPORTED", result.stderr)

    def load_reader(self):
        spec = importlib.util.spec_from_file_location("reader_under_test", self.scripts / "read-canonical-pair.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_native_profile_runs_original_run_root_and_phase_guards(self):
        resolved = self.make_real_generation(native=True)
        result = self.validate()
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        phase = self.phase_authority()
        self.assertEqual(phase.returncode, 0, phase.stderr.decode())
        self.assertEqual(json.loads(phase.stdout)["operation"], "replace")
        self.assertEqual(self.read("--native-guards").returncode, 0)
        native_state = (self.output / "native-STATE.md").read_text()
        self.assertTrue(native_state.endswith(self.native_source["STATE"]))
        self.assertEqual((self.output / "native-ROADMAP.md").read_text(), self.native_source["ROADMAP"])
        self.assertEqual(native_state.count("Current epoch:"), 1)
        self.assertIn("Current epoch: " + resolved["pointer"]["continuity_epoch"], native_state)

    def test_native_resumed_current_pair_runs_the_original_native_guards(self):
        original = self.make_real_generation(native=True)
        boundary = "host-reported-compaction"
        invalidation = self.claim("--invalidate-continuity", CONTROLLER, "--boundary", boundary,
                                  "--event", "constructed-shared-native-resume")
        self.assertEqual(invalidation.returncode, 0, invalidation.stderr.decode())
        result = self.claim("--resolve-resume-generation", CONTROLLER)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        evidence = json.loads(result.stdout)
        self.assertEqual(evidence["status"], "PRE_RESUME_EVIDENCE")
        self.assertEqual(evidence["pointer_token"], original["pointer_token"])
        self.assertEqual(evidence["invalidation_token"], invalidation.stdout.decode().strip())
        self.assertNotEqual(self.read("--native-guards").returncode, 0)
        tokens = ("--expected-pointer", evidence["pointer_token"], "--expected-invalidation", evidence["invalidation_token"])
        before = {}
        for role in ("STATE", "ROADMAP"):
            # Two separately completed native commands in this constructed
            # control; no assertion about a real host boundary occurrence.
            result = self.claim("--read-resume-state", CONTROLLER, "--role", role, *tokens)
            self.assertEqual(result.returncode, 0, result.stderr.decode())
            before[role] = json.loads(result.stdout.splitlines()[16])
            self.assertEqual(result.stdout, Path(original[role.lower() + "_path"]).read_bytes())
        receipt = self.claim("--resume-controller", CONTROLLER, "--boundary", boundary,
                             "--epoch", evidence["next_continuity_epoch"], *tokens)
        self.assertEqual(receipt.returncode, 0, receipt.stderr.decode())
        receipt_token = receipt.stdout.decode().strip()
        self.assertEqual(self.claim("--verify-resume-receipt", receipt_token).returncode, 0)
        self.assertEqual(self.claim("--require-current-continuity", CONTROLLER).returncode, 0)
        result = self.validate()
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        result = self.phase_authority()
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        result = self.read("--native-guards")
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        for role in ("STATE", "ROADMAP"):
            after = json.loads((self.output / (role + ".md")).read_bytes().splitlines()[16])
            self.assertEqual(after["payload"], before[role]["payload"])
            self.assertEqual(after["transition"]["boundary"], boundary)
            self.assertEqual(after["transition"]["schema_version"], "implementaudit.native-resume-transition.v1")
        self.assertIn("Current epoch: " + evidence["next_continuity_epoch"], (self.output / "native-STATE.md").read_text())

    def native_failure(self, change, diagnostic, *, roadmap=False, extra_artifacts=None):
        self.make_real_generation(native=True, **{"roadmap_edit" if roadmap else "state_edit": change},
                                  extra_artifacts=extra_artifacts)
        # Construct a valid-looking retired compatibility pair. Its contents
        # cannot rescue a failing pointer-bound native profile; archived exact
        # preimages remain retained in the genuine owner's object database.
        for role in ("STATE", "ROADMAP"):
            shutil.copyfile(self.scripts.parent / "templates" / (role + ".md"), self.run / (role + ".md"))
        result = self.validate()
        self.assertNotEqual(result.returncode, 0, "current native guard failure was hidden by stale root files")
        self.assertIn(diagnostic, result.stderr)

    @staticmethod
    def andon_rows(text, rows):
        return text.replace("|---|---|---|---|---|---|---|---|\n\nOutcome values:",
                            "|---|---|---|---|---|---|---|---|\n" + rows + "\nOutcome values:")

    def test_native_andon_occurrence_guard_is_not_skipped(self):
        self.native_failure(lambda s: self.andon_rows(s, "| 1 |  | 1 | regression | bad | fix | evidence | open |\n"), b"missing an Occ")

    def test_native_andon_class_guard_is_not_skipped(self):
        self.native_failure(lambda s: self.andon_rows(s, "| 1 | o1 | 1 | regression, transport-infrastructure | bad | fix | evidence | open |\n"), b"non-single-token Class")

    def test_native_recurrence_decision_guard_is_not_skipped(self):
        rows = "".join(f"| {i} | o{i} | 1 | regression | bad | owner/source=app.txt | evidence | open |\n" for i in range(1, 4))
        self.native_failure(lambda s: self.andon_rows(s, rows), b"Mechanism-replacement decision")

    def test_native_residual_owner_guard_is_not_skipped(self):
        def change(text):
            return text.replace("| Residual | Consequential | Disposition | Owner / policy ref | Evidence |\n|---|---|---|---|---|",
                "| Residual | Consequential | Disposition | Owner / policy ref | Evidence |\n|---|---|---|---|---|\n| r1 | yes | transferred |  | evidence |")
        self.native_failure(change, b"no owner/policy ref")

    def test_native_model_identity_guard_is_not_skipped(self):
        self.native_failure(lambda s: s + "\nmodel-identity: requested_model: requested | actual_model: substituted | evidence: host-event:constructed | claims: bound\n", b"model substitution must mark claims IDENTITY_UNBOUND")

    def test_native_model_transport_evidence_cell_is_not_skipped(self):
        def change(text):
            text = self.andon_rows(text, "| 1 | o1 | 1 | transport-infrastructure | substituted model | repair | host-event:wrong | open |\n")
            return text + "\nmodel-identity: requested_model: requested | actual_model: substituted | evidence: host-event:constructed | claims: IDENTITY_UNBOUND\n"
        self.native_failure(change, b"bind the transport-infrastructure Andon evidence cell")

    def cold_review_case(self, *, reused=False):
        base = self.git("rev-parse", "HEAD")
        (self.repo / "fixture.txt").write_text("Constructed native cold-review source successor.\n")
        self.git("add", "fixture.txt")
        self.git("-c", "commit.gpgsign=false", "commit", "-qm", "constructed review successor")
        head = self.git("rev-parse", "HEAD")
        report = ("Constructed guard-control attestation; not an independent approval.\n\nReviewer attestation:\n"
                  "- reviewer_identity: constructed-validator-control\n- requested_model: fixture-model\n"
                  "- actual_model: fixture-model\n- authoring_context_reuse: " + ("yes" if reused else "no")
                  + "\n- other_reviewer_output_seen: no\n- base_sha: " + base + "\n- head_sha: " + head
                  + "\n\nReport state: FINAL\nPASS\n").encode()
        def change(text):
            return (text + "\nmodel-identity: requested_model: fixture-model | actual_model: fixture-model | evidence: self-report | claims: bound\n"
                    + "cold-review: disposition: PASS | attestation: native-review.md | base_sha: " + base + " | head_sha: " + head + "\n")
        return change, {"native-review.md": report}

    def test_native_cold_review_consumes_exact_bound_attestation(self):
        change, artifacts = self.cold_review_case()
        self.make_real_generation(native=True, state_edit=change, extra_artifacts=artifacts)
        result = self.validate()
        self.assertEqual(result.returncode, 0, result.stderr.decode())

    def test_native_self_review_cannot_discharge_cold_review(self):
        change, artifacts = self.cold_review_case(reused=True)
        self.native_failure(change, b"authoring-context reuse", extra_artifacts=artifacts)

    def install_actual_cold_record_checker(self):
        destination = self.repo / "scripts/check-cold-review-contract.sh"
        destination.parent.mkdir(exist_ok=True)
        shutil.copyfile(ROOT / "scripts/check-cold-review-contract.sh", destination)

    def successor_case(self, *, malformed=False):
        self.install_actual_cold_record_checker()
        template = (ROOT / "fixtures/cold-review/issue-86-runtime-non-verdict-replacement.md").read_text()
        carried = template[template.index("reviewer-attestation:"):].replace("issue-86-runtime-non-verdict-replacement.md#finding-a", "STATE.md#finding-a")
        if malformed:
            carried = carried.replace("substantive_verdict_consumed: no", "substantive_verdict_consumed: yes")
        def change(text):
            text = self.andon_rows(text, "| 1 | o1 | 6 | transport-infrastructure | reviewer interrupted | exact retry | constructed observation | open |\n")
            return text + "\n## Native successor review control\n\n" + carried
        return change, {"independent-review-confirms-handoff.md": (ROOT / "fixtures/cold-review/independent-review-confirms-handoff.md").read_bytes()}

    def test_native_successor_records_reach_original_direct_record_consumer(self):
        change, artifacts = self.successor_case()
        self.make_real_generation(native=True, state_edit=change, extra_artifacts=artifacts)
        result = self.validate()
        self.assertEqual(result.returncode, 0, result.stderr.decode())

    def test_native_nonverdict_cannot_be_consumed_through_a_stale_root(self):
        change, artifacts = self.successor_case(malformed=True)
        self.native_failure(change, b"runtime non-verdict cannot consume", extra_artifacts=artifacts)

    def test_native_instruction_terminal_evidence_guard_is_not_skipped(self):
        def change(text):
            return text.replace("| Instr | Reference | Kind | Authority | Subject | Issued epoch | Status | Status evidence | Supersedes/by | Scope end |\n|---|---|---|---|---|---|---|---|---|---|",
                "| Instr | Reference | Kind | Authority | Subject | Issued epoch | Status | Status evidence | Supersedes/by | Scope end |\n|---|---|---|---|---|---|---|---|---|---|\n| i1 | exact-original | one-shot-action | user | bounded | G0001 | satisfied |  |  |  |")
        self.native_failure(change, b"terminal status but no status evidence")

    def test_native_false_boundary_provenance_is_not_rotation(self):
        self.native_failure(lambda s: s.replace("| Epoch | Boundary provenance | Established at | Repo identity | Reconciled | Notes |\n|---|---|---|---|---|---|",
            "| Epoch | Boundary provenance | Established at | Repo identity | Reconciled | Notes |\n|---|---|---|---|---|---|\n| G0001 | invented-compaction | absent | original | no | false |"), b"invalid boundary provenance")

    def test_native_historical_rotation_epoch_is_preserved_without_current_authority(self):
        historical = "| G0001 | canonical-state-rotation | historical observation | original scope | yes | archived occurrence only |"
        self.make_real_generation(native=True, state_edit=lambda s: s.replace(
            "| Epoch | Boundary provenance | Established at | Repo identity | Reconciled | Notes |\n|---|---|---|---|---|---|",
            "| Epoch | Boundary provenance | Established at | Repo identity | Reconciled | Notes |\n|---|---|---|---|---|---|\n" + historical))
        result = self.validate()
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        result = self.read("--native-guards")
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        state = (self.output / "native-STATE.md").read_text()
        self.assertIn(historical + "\n", state)
        self.assertEqual(state.count("Current epoch:"), 1)
        self.assertIn("Current epoch: G0002\n", state)

    def test_native_profile_cannot_occupy_effective_current_epoch(self):
        self.native_failure(lambda s: s.replace(
            "| Epoch | Boundary provenance | Established at | Repo identity | Reconciled | Notes |\n|---|---|---|---|---|---|",
            "| Epoch | Boundary provenance | Established at | Repo identity | Reconciled | Notes |\n|---|---|---|---|---|---|\n| G0002 | canonical-state-rotation | alleged | original | yes | native pointer JOIN |"),
            b"profile epoch row collides with the derived live epoch")

    def test_native_phase_table_cannot_be_hidden_by_stale_roadmap(self):
        self.make_real_generation(native=True, roadmap_edit=lambda s: s.replace("| 1 |  |  | - |  |  |  | open |", ""))
        shutil.copyfile(self.scripts.parent / "templates/ROADMAP.md", self.run / "ROADMAP.md")
        result = self.phase_authority()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"exactly one matching phase row", result.stderr)

    def test_native_phase_scope_guard_is_preserved(self):
        self.make_real_generation(native=True)
        # A changed phase cannot reuse its preserved source/evidence binding.
        path = self.run / "phases/phase-1.md"
        path.write_text(path.read_text().replace('"source":"app.txt"', '"source":"outside.txt"'))
        result = command(["bash", self.scripts / "validate-phase.sh", "--mutation-authority", path,
                          "--phase", "1", "--step", "1", "--repo-root", self.repo, "--run-root", self.run], self.repo)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"native record dependency differs", result.stderr)

    def test_native_direct_markdown_denominator_is_closed(self):
        self.make_real_generation(native=True)
        (self.run / "unmapped-current-record.md").write_text("successor-review: unbound live record\n")
        result = self.read("--native-guards")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"population is not completely owner-bound", result.stderr)
        self.assertEqual(list(self.output.iterdir()), [])

    def test_native_authorization_consumer_preserves_default_deny(self):
        self.make_real_generation(native=True)
        result = self.read("--native-guards")
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        result = command(["bash", self.scripts / "check-authorization-binding.sh", "--state",
                          self.output / "native-records/STATE.md"], self.repo)
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assertIn(b"durable STATE is default deny", result.stdout)
        self.assertEqual(self.read("--native-guards", "--verify-current").returncode, 0)

    def test_native_authorization_consumer_cannot_use_a_stale_default_deny_state(self):
        self.make_real_generation(native=True, state_edit=lambda text: text.replace("Commit authorized: no", "Commit authorized: yes"))
        shutil.copyfile(self.scripts.parent / "templates/STATE.md", self.run / "STATE.md")
        stale = command(["bash", self.scripts / "check-authorization-binding.sh", "--state", self.run / "STATE.md"], self.repo)
        self.assertEqual(stale.returncode, 0, stale.stderr.decode())
        result = self.read("--native-guards")
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        result = command(["bash", self.scripts / "check-authorization-binding.sh", "--state",
                          self.output / "native-records/STATE.md"], self.repo)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"missing grant source for authorized STATE action", result.stderr)

    def closure_dependency_case(self, disposition):
        record = b"Constructed portable closure-consumer control; no run closure claim.\nclaim: fixture | surface: source | status: verified | evidence-surface: source\n"
        row = {"ts": "2026-06-01T00:00:00Z", "phase": "1", "what": "constructed guard control",
               "why": "exercise actual dependent ledger reader", "owner": "this-run",
               "unblock": "recorded fixture evidence", "disposition": disposition}
        self.make_real_generation(native=True, extra_artifacts={"closure-record.md": record,
                                  "deferrals.jsonl": (json.dumps(row, separators=(",", ":")) + "\n").encode()})
        result = self.read("--native-guards")
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        return command(["bash", self.scripts / "check-closure-surface.sh",
                        self.output / "native-records/closure-record.md"], self.repo)

    def test_native_closure_consumer_receives_bound_sibling_ledger(self):
        result = self.closure_dependency_case("validated-resolved")
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assertEqual((self.output / "native-records/deferrals.jsonl").read_bytes(), (self.run / "deferrals.jsonl").read_bytes())
        self.assertEqual(self.read("--native-guards", "--verify-current").returncode, 0)

    def test_native_closure_consumer_cannot_lose_a_pending_sibling_ledger(self):
        result = self.closure_dependency_case("pending")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"nonterminal disposition 'pending' blocks closure", result.stderr)

    def test_actual_native_owner_pair_reads_are_ordered_and_token_bound(self):
        resolved = self.make_real_generation()
        module = self.load_reader()
        calls = []
        native = module.owner
        def observe(repo, *args):
            calls.append(args)
            return native(repo, *args)
        with mock.patch.object(module, "owner", side_effect=observe):
            self.assertEqual(module.materialize_pair(self.run, self.output), 0)
        self.assertEqual([args[0] for args in calls], ["--current-controller", "--resolve-canonical-generation",
            "--read-canonical-state", "--read-canonical-state", "--resolve-canonical-generation"])
        self.assertEqual([args[3] for args in calls[2:4]], ["STATE", "ROADMAP"])
        self.assertEqual([args[5] for args in calls[2:4]], [resolved["pointer_token"]] * 2)

    def test_actual_pointer_drift_between_separate_reads_refuses(self):
        self.make_real_generation()
        module = self.load_reader()
        native = module.owner
        def drift(repo, *args):
            result = native(repo, *args)
            if args[:4] == ("--read-canonical-state", CONTROLLER, "--role", "STATE"):
                self.put_ref("current-generations")
            return result
        with mock.patch.object(module, "owner", side_effect=drift), self.assertRaises(module.ReaderError):
            module.materialize_pair(self.run, self.output)
        self.assertEqual(list(self.output.iterdir()), [])

    def test_actual_roadmap_absence_between_separate_reads_refuses(self):
        resolved = self.make_real_generation()
        module = self.load_reader()
        native = module.owner
        def disappear(repo, *args):
            result = native(repo, *args)
            if args[:4] == ("--read-canonical-state", CONTROLLER, "--role", "STATE"):
                Path(resolved["roadmap_path"]).unlink()
            return result
        with mock.patch.object(module, "owner", side_effect=disappear), self.assertRaisesRegex(module.ReaderError, "ROADMAP read refused"):
            module.materialize_pair(self.run, self.output)
        self.assertEqual(list(self.output.iterdir()), [])

    def test_actual_missing_pointer_after_migration_cannot_restore_root_authority(self):
        self.make_real_generation(native=True)
        self.git("update-ref", "-d", f"refs/implementaudit/current-generations/{CONTROLLER}")
        for role in ("STATE", "ROADMAP"):
            shutil.copyfile(self.scripts.parent / "templates" / (role + ".md"), self.run / (role + ".md"))
        result = self.read("--native-guards")
        self.assertEqual(result.returncode, 1)
        self.assertIn(b"JOIN refused; root fallback is forbidden", result.stderr)
        self.assertEqual(list(self.output.iterdir()), [])

    def test_actual_missing_marker_after_migration_cannot_restore_root_authority(self):
        self.make_real_generation(native=True)
        self.git("update-ref", "-d", f"refs/implementaudit/current-generation-migrations/{CONTROLLER}")
        result = self.validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"JOIN refused; root fallback is forbidden", result.stderr)

    def test_transport_changed_pair_bytes_refuse_even_after_native_success(self):
        self.make_real_generation()
        module = self.load_reader()
        native = module.owner
        def corrupt(repo, *args):
            result = native(repo, *args)
            if args[:4] == ("--read-canonical-state", CONTROLLER, "--role", "ROADMAP"):
                result.stdout += b"constructed transport mismatch\n"
            return result
        with mock.patch.object(module, "owner", side_effect=corrupt), self.assertRaisesRegex(module.ReaderError, "bytes differ"):
            module.materialize_pair(self.run, self.output)
        self.assertEqual(list(self.output.iterdir()), [])

    def test_native_snapshot_is_rechecked_after_consumption(self):
        self.make_real_generation(native=True)
        result = self.read("--native-guards")
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assertEqual(self.read("--native-guards", "--verify-current").returncode, 0)
        (self.output / "native-STATE.md").write_text("tampered derivative guard snapshot\n")
        result = self.read("--native-guards", "--verify-current")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"snapshot or current native authority changed", result.stderr)

    def test_pending_boundary_obligations_survive_actual_native_reader(self):
        self.make_real_generation(native=True)
        result = self.read("--native-guards")
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        body = json.loads((self.output / "STATE.md").read_bytes().splitlines()[16])
        pending = body["payload"]["pending_boundaries"]["value"]
        self.assertEqual(pending, self.preimage_bodies["STATE"]["payload"]["pending_boundaries"]["value"])
        self.assertEqual([row["boundary_id"] for row in pending], ["boundary-1", "boundary-2"])
        self.assertTrue(all(row["audit_state_required"] and row["currentness"]["epoch"] is None for row in pending))
        self.assertTrue(all(row["consumption"]["state"] == "PENDING" and row["consumption"]["witness"] is None for row in pending))
        self.assertEqual(pending[0]["uncovered_successors"], ["boundary-2"])
        self.assertNotEqual(pending[0]["physical_source"]["offset"], pending[1]["physical_source"]["offset"])

    def test_TC06_retired_rotation_policy_keeps_old_readers_and_archives(self):
        self.make_real_generation(native=True)
        module = self.load_reader()
        native = module.owner
        refs_before = self.git("for-each-ref", "--format=%(refname) %(objectname)", "refs/implementaudit/")
        def retired(repo, *args):
            self.assertIn(args[0], {"--current-controller", "--resolve-canonical-generation", "--read-canonical-state"},
                          "constructed retirement policy forbids new rotations and other owner effects")
            return native(repo, *args)
        with mock.patch.object(module, "owner", side_effect=retired):
            self.assertEqual(module.materialize_pair(self.run, self.output, native_guards=True), 0)
        self.assertEqual(self.git("for-each-ref", "--format=%(refname) %(objectname)", "refs/implementaudit/"), refs_before)
        body = json.loads((self.output / "STATE.md").read_bytes().splitlines()[16])
        pointers = [row for row in body["archive_pointers"] if row["role"] == "HISTORY_RECORD"]
        spec = importlib.util.spec_from_file_location("reader_retained_archive", self.scripts / "rotate-canonical-state.py")
        helper = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = helper
        spec.loader.exec_module(helper)
        for pointer in pointers:
            result = helper.resolve_typed_archive_pointer_v2(self.repo, pointer)
            history = json.loads(result["bytes"])
            self.assertEqual(result["authority_ceiling"], "ARCHIVED_ONLY_HISTORY")
            self.assertEqual(history["payload"]["current_applicability"], "INVALIDATED_CURRENT_USE")
            self.assertEqual(history["payload"]["original_scope"], "Original admission prefix before later invalidation")
            self.assertIn("TC11 original scope remains", history["payload"]["historical_refusal"])
        self.assertTrue(pointers, "TC11 history must be actually retrieved, not only declared")

    def alter_discovery_claim(self, original, variant, *, retain_schema=False):
        (self.run / ".controller").unlink(missing_ok=True)
        path = self.run / ".claimed"
        raw = original if retain_schema else original.replace(b"schema=implementaudit.run-claim.v2\n", b"")
        if variant == "schema-malformed":
            raw = b"schema=malformed-discovery-hint\n" + raw
        elif variant == "claim-absent":
            path.unlink(missing_ok=True)
            return
        elif variant == "claim-empty":
            raw = b""
        elif variant == "id-absent":
            raw = re.sub(rb"(?m)^claim_id=.*\n", b"", raw)
        elif variant == "id-malformed":
            raw = re.sub(rb"(?m)^claim_id=.*$", b"claim_id=malformed", raw)
        elif variant == "id-replaced":
            self.assertNotEqual(re.findall(rb"(?m)^claim_id=([0-9a-f]{32})$", raw), [b"0" * 32])
            raw = re.sub(rb"(?m)^claim_id=.*$", b"claim_id=" + b"0" * 32, raw)
        elif variant == "id-duplicate":
            raw += b"claim_id=" + b"0" * 32 + b"\n"
        else:
            self.assertEqual(variant, "schema-absent")
        if retain_schema:
            self.assertIn(b"schema=implementaudit.run-claim.v2\n", raw)
            self.assertIn(b"mode=full\n", raw)
        path.write_bytes(raw)

    def discovery_custody(self):
        hints = {}
        for name in (".controller", ".claimed"):
            path = self.run / name
            hints[name] = (path.lstat().st_mode, path.readlink() if path.is_symlink() else path.read_bytes()) if path.exists() or path.is_symlink() else None
        return hints, self.git("for-each-ref", "--format=%(refname) %(objectname)", "refs/implementaudit/")

    def absent_discovery_hints(self):
        hints = self.discovery_custody()[0]
        self.assertIsNone(hints[".controller"], "locator discovery requires an absent controller hint")
        return hints

    def assert_discovery_refuses(self, *, expected_hints=None):
        custody = self.discovery_custody()
        if expected_hints is not None:
            self.assertEqual(custody[0], expected_hints, "discovery claim hints changed between locator rows")
        observed = {}
        for name, consumer in (("reader", self.read), ("run-root", self.validate), ("phase-authority", self.phase_authority)):
            self.assertEqual(self.discovery_custody(), custody, "discovery stimulus changed before the public call")
            observed[name] = consumer()
            self.assertEqual(self.discovery_custody(), custody, "public reader changed its discovery inputs")
        for name, result in observed.items():
            with self.subTest(consumer=name):
                self.assertEqual(result.returncode, 1, name + " admitted legacy input: " + repr({
                    key: (value.returncode, value.stdout, value.stderr) for key, value in observed.items()}))
                self.assertEqual(result.stdout, b"", "refusal emitted a derivative authority")
                if name != "reader":
                    self.assertIn(b"canonical pair selection refused", result.stderr)
        self.assertEqual(list(self.output.iterdir()), [], "failed discovery wrote a pair snapshot")
        self.assertEqual(self.discovery_custody(), custody)

    def discovery_claim_variants(self):
        original = (self.run / ".claimed").read_bytes()
        for variant in ("schema-absent", "schema-malformed", "claim-absent", "claim-empty",
                        "id-absent", "id-malformed", "id-replaced", "id-duplicate"):
            with self.subTest(discovery_hint=variant):
                self.alter_discovery_claim(original, variant)
                self.assert_discovery_refuses()

    def test_discovery_malformed_marker_cannot_hide_behind_mutated_claim_hints(self):
        self.put_ref("current-generation-migrations")
        self.git("update-ref", "-d", f"refs/implementaudit/controllers/{CONTROLLER}")
        self.discovery_claim_variants()

    def test_discovery_malformed_pointer_cannot_hide_behind_mutated_claim_hints(self):
        self.put_ref("current-generations")
        self.git("update-ref", "-d", f"refs/implementaudit/controllers/{CONTROLLER}")
        self.discovery_claim_variants()

    def test_discovery_controller_still_binds_run_without_claim_hints(self):
        self.discovery_claim_variants()

    def retained_discovery_case(self, retained):
        resolved = self.make_real_generation(native=True)
        self.assertEqual(self.validate().returncode, 0)
        # Retain actual CLI-minted authority, then remove the other discovery
        # records and restore a valid-looking retired compatibility pair.
        ref = f"refs/implementaudit/{retained}/{CONTROLLER}"
        oid = self.git("rev-parse", ref)
        expected = resolved["marker_oid"] if retained == "current-generation-migrations" else resolved["pointer_token"].split("@")[1]
        self.assertEqual(oid, expected)
        for role in ("controllers", "current-generations", "current-generation-migrations"):
            if role != retained:
                self.git("update-ref", "-d", f"refs/implementaudit/{role}/{CONTROLLER}")
        for role in ("STATE", "ROADMAP"):
            shutil.copyfile(self.scripts.parent / "templates" / (role + ".md"), self.run / (role + ".md"))
        self.discovery_claim_variants()
        self.assertEqual(self.git("rev-parse", ref), oid)

    def test_discovery_real_permanent_marker_survives_all_other_hint_loss(self):
        self.retained_discovery_case("current-generation-migrations")

    def test_discovery_real_current_pointer_survives_all_other_hint_loss(self):
        self.retained_discovery_case("current-generations")

    def test_discovery_unsafe_claim_reaches_reader_without_shell_prefilter(self):
        original = (self.run / ".claimed").read_bytes()
        self.alter_discovery_claim(original, "schema-absent")
        outside = self.repo / "linked-claim-target"
        (self.run / ".claimed").rename(outside)
        (self.run / ".claimed").symlink_to(outside)
        self.assert_discovery_refuses()

    def test_discovery_malformed_controller_and_claim_hints_still_refuse(self):
        (self.run / ".claimed").write_bytes(b"schema=malformed\nmode=full\n")
        for hint in (b"", b"controller_id=malformed/name\n", b"controller_id=" + CONTROLLER.encode() + b"\nextra=value\n"):
            with self.subTest(controller_hint=hint):
                (self.run / ".controller").write_bytes(hint)
                self.assert_discovery_refuses()

    def test_discovery_linked_marker_custody_refuses_without_claim_schema(self):
        self.put_ref("current-generation-migrations")
        self.git("update-ref", "-d", f"refs/implementaudit/controllers/{CONTROLLER}")
        self.alter_discovery_claim((self.run / ".claimed").read_bytes(), "schema-absent")
        ref = f"refs/implementaudit/current-generation-migrations/{CONTROLLER}"
        path = self.repo / self.git("rev-parse", "--git-path", ref)
        outside = self.repo / "linked-marker-target"
        path.rename(outside)
        path.symlink_to(outside)
        self.assert_discovery_refuses()

    def test_discovery_unbound_legacy_claim_variants_keep_structural_guards(self):
        self.git("update-ref", "-d", f"refs/implementaudit/controllers/{CONTROLLER}")
        original = (self.run / ".claimed").read_bytes()
        for variant in ("schema-absent", "schema-malformed", "claim-absent", "claim-empty",
                        "id-absent", "id-malformed", "id-replaced", "id-duplicate"):
            with self.subTest(discovery_hint=variant):
                self.alter_discovery_claim(original, variant)
                result = self.read()
                self.assertEqual(result.returncode, 3, result.stderr.decode())
                result = self.validate()
                self.assertEqual(result.returncode, 1 if variant == "claim-empty" else 0, result.stderr.decode())
                if variant == "claim-empty":
                    self.assertIn(b".claimed has invalid mode", result.stderr)
        self.alter_discovery_claim(original, "schema-absent")
        result = self.phase_authority()
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        state = self.run / "STATE.md"
        state.write_text(state.read_text().replace("## Andon log", "## Removed native Andon log"))
        result = self.validate()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn(b"Andon log", result.stderr)
        self.assertEqual(list(self.output.iterdir()), [])

    def test_discovery_other_run_authorities_do_not_bind_unbound_legacy_run(self):
        self.make_real_generation(native=True, state_edit=lambda text:
                                  text + "\nPARALLEL: constructed independent legacy reader control\n")
        claimed = self.claim("unbound legacy reader")
        self.assertEqual(claimed.returncode, 0, claimed.stderr.decode())
        self.run = self.repo / claimed.stdout.decode().strip()
        for name in ("STATE.md", "ROADMAP.md", "PROTOCOL.md", "THINKING.md", "sidecars.md", "tools.md", "context.md"):
            shutil.copyfile(self.scripts.parent / "templates" / name, self.run / name)
        (self.run / "phases").mkdir()
        self.write_phase()
        self.alter_discovery_claim((self.run / ".claimed").read_bytes(), "schema-absent")
        result = self.read()
        self.assertEqual(result.returncode, 3, result.stderr.decode())
        result = self.validate()
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        result = self.phase_authority()
        self.assertEqual(result.returncode, 0, result.stderr.decode())
        self.assertEqual(list(self.output.iterdir()), [])

    def test_discovery_unbound_legacy_outside_git_keeps_structural_validation(self):
        with tempfile.TemporaryDirectory(prefix="reader-unbound-", dir="/tmp") as temporary:
            self.run = Path(temporary) / "run"
            shutil.copytree(ROOT / "fixtures/run-root/no-sentinel-legacy/root", self.run)
            self.assertNotEqual(command(["git", "rev-parse", "--show-toplevel"], self.run).returncode, 0)
            result = self.read()
            self.assertEqual(result.returncode, 3, result.stderr.decode())
            result = self.validate()
            self.assertEqual(result.returncode, 0, result.stderr.decode())
            state = self.run / "STATE.md"
            state.write_text(state.read_text().replace("## Andon log", "## Removed native Andon log"))
            result = self.validate()
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(b"Andon log", result.stderr)
            self.assertEqual(list(self.output.iterdir()), [])

    def test_discovery_broken_git_custody_is_not_unbound_legacy(self):
        with tempfile.TemporaryDirectory(prefix="reader-broken-git-", dir="/tmp") as temporary:
            self.run = Path(temporary) / "run"
            shutil.copytree(ROOT / "fixtures/run-root/no-sentinel-legacy/root", self.run)
            (Path(temporary) / ".git").write_text("malformed Git discovery custody\n")
            self.assertEqual(self.read().returncode, 1)
            result = self.validate()
            self.assertEqual(result.returncode, 1, result.stderr.decode())
            self.assertIn(b"canonical pair selection refused", result.stderr)
            self.assertEqual(list(self.output.iterdir()), [])

    def test_discovery_v2_claim_outside_git_still_refuses(self):
        original = (self.run / ".claimed").read_bytes()
        with tempfile.TemporaryDirectory(prefix="reader-v2-outside-git-", dir="/tmp") as temporary:
            self.run = Path(temporary) / "run"
            shutil.copytree(ROOT / "fixtures/run-root/no-sentinel-legacy/root", self.run)
            (self.run / ".claimed").write_bytes(original)
            self.assertEqual(self.read().returncode, 1)
            result = self.validate()
            self.assertEqual(result.returncode, 1, result.stderr.decode())
            self.assertIn(b"canonical pair selection refused", result.stderr)
            self.assertEqual(list(self.output.iterdir()), [])

    def test_discovery_rechecks_authorities_before_owner_legacy_exit(self):
        module = self.load_reader()
        native = module.owner
        def arrive(repo, *args):
            result = native(repo, *args)
            if args[0] == "--resolve-canonical-generation":
                self.assertEqual(result.returncode, 3, result.stderr.decode())
                self.put_ref("current-generation-migrations")
            return result
        with mock.patch.object(module, "owner", side_effect=arrive), self.assertRaises(module.ReaderError):
            module.materialize_pair(self.run, self.output)
        self.assertEqual(list(self.output.iterdir()), [])

    def assert_discovery_baseline_rejects_before_dispatch(self, expected_hints):
        with mock.patch.object(self, "read", wraps=self.read) as reader, \
             mock.patch.object(self, "validate", wraps=self.validate) as run_root, \
             mock.patch.object(self, "phase_authority", wraps=self.phase_authority) as phase:
            with self.assertRaises(AssertionError):
                self.assert_discovery_refuses(expected_hints=expected_hints)
            for consumer in (reader, run_root, phase):
                consumer.assert_not_called()

    def test_discovery_locator_baseline_requires_absent_hint_at_capture(self):
        with self.assertRaises(AssertionError):
            self.absent_discovery_hints()

    def test_discovery_locator_baseline_rejects_restored_hint(self):
        self.alter_discovery_claim((self.run / ".claimed").read_bytes(), "id-replaced", retain_schema=True)
        expected_hints = self.absent_discovery_hints()
        (self.run / ".controller").write_bytes(b"controller_id=canonical-reader-test\n")
        self.assert_discovery_baseline_rejects_before_dispatch(expected_hints)
        self.assertEqual((self.run / ".controller").read_bytes(), b"controller_id=canonical-reader-test\n")

    def test_discovery_locator_baseline_rejects_changed_claim_bytes(self):
        self.alter_discovery_claim((self.run / ".claimed").read_bytes(), "id-replaced", retain_schema=True)
        expected_hints = self.absent_discovery_hints()
        path = self.run / ".claimed"
        path.write_bytes(path.read_bytes() + b"held_out_fixture_hint=changed\n")
        self.assert_discovery_baseline_rejects_before_dispatch(expected_hints)

    def test_discovery_locator_baseline_rejects_changed_claim_mode(self):
        self.alter_discovery_claim((self.run / ".claimed").read_bytes(), "id-replaced", retain_schema=True)
        expected_hints = self.absent_discovery_hints()
        path = self.run / ".claimed"
        original_mode = path.lstat().st_mode
        try:
            path.chmod(original_mode & ~0o222)
            self.assertNotEqual(path.lstat().st_mode, original_mode)
            self.assert_discovery_baseline_rejects_before_dispatch(expected_hints)
        finally:
            path.chmod(original_mode)

    def test_discovery_locator_baseline_permits_intentional_ref_changes(self):
        self.alter_discovery_claim((self.run / ".claimed").read_bytes(), "id-replaced", retain_schema=True)
        expected_hints = self.absent_discovery_hints()
        for role in ("current-generations", "current-generation-migrations"):
            self.put_ref(role)
            self.assert_discovery_refuses(expected_hints=expected_hints)

    def test_discovery_malformed_retained_run_locators_never_select_legacy(self):
        self.make_real_generation(native=True)
        original = {}
        for role in ("current-generations", "current-generation-migrations"):
            ref = f"refs/implementaudit/{role}/{CONTROLLER}"
            original[role] = command(["git", "cat-file", "blob", ref], self.repo).stdout
            self.git("update-ref", "-d", ref)
        self.git("update-ref", "-d", f"refs/implementaudit/controllers/{CONTROLLER}")
        self.alter_discovery_claim((self.run / ".claimed").read_bytes(), "id-replaced", retain_schema=True)
        expected_hints = self.absent_discovery_hints()
        for role in ("STATE", "ROADMAP"):
            shutil.copyfile(self.scripts.parent / "templates" / (role + ".md"), self.run / (role + ".md"))
        identity = self.run.relative_to(self.repo).as_posix()
        locators = ("unresolved-component/../" + identity, "../" + self.repo.name + "/" + identity,
                    "./" + identity, identity + "/", identity.replace("/runs/", "//runs/"),
                    str(self.run), ".IMPLEMENTAUDIT/runs/non-native-name", "unresolved/run")
        for role, raw in original.items():
            for locator in locators:
                with self.subTest(authority=role, run_locator=locator):
                    if role == "current-generations":
                        body = json.loads(raw)
                        body["run_root_identity"] = locator
                        changed = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
                    else:
                        row = raw.decode().split("\t")
                        self.assertEqual(len(row), 10)
                        row[3] = locator
                        changed = "\t".join(row).encode()
                    self.put_ref(role, changed)
                    self.assert_discovery_refuses(expected_hints=expected_hints)
            self.git("update-ref", "-d", f"refs/implementaudit/{role}/{CONTROLLER}")

    def test_discovery_malformed_controller_run_paths_never_select_legacy(self):
        ref = f"refs/implementaudit/controllers/{CONTROLLER}"
        raw = command(["git", "cat-file", "blob", ref], self.repo).stdout
        original = raw.decode().rstrip("\n").split("\t")
        self.assertEqual(len(original), 4)
        self.alter_discovery_claim((self.run / ".claimed").read_bytes(), "id-replaced", retain_schema=True)
        expected_hints = self.absent_discovery_hints()
        identity = self.run.relative_to(self.repo).as_posix()
        alias = self.repo / "linked-repository-alias"
        alias.symlink_to(self.repo, target_is_directory=True)
        paths = (str(self.repo) + "/unresolved-component/../" + identity,
                 identity, str(self.run) + "/", str(self.run).replace("/.IMPLEMENTAUDIT/", "//.IMPLEMENTAUDIT/"),
                 str(self.repo) + "/.IMPLEMENTAUDIT/runs/non-native-name", str(alias / identity))
        for path in paths:
            with self.subTest(controller_run=path):
                row = original.copy()
                row[3] = path
                self.put_ref("controllers", ("\t".join(row) + "\n").encode())
                self.assert_discovery_refuses(expected_hints=expected_hints)


class SharedContractTests(unittest.TestCase):
    def setUp(self):
        path = ROOT / "scripts/check-helper-reachability.sh"
        text = path.read_text().split("<<'PY'\n", 1)[1].rsplit("\nPY", 1)[0]
        tree = ast.parse(text)
        names = {"shell_code", "python_array_invokes", "captured_python_library", "caller_invokes", "claim_public_modes"}
        functions = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
        self.assertEqual({node.name for node in functions}, names)
        self.scope = {"ast": ast, "hashlib": hashlib, "re": re,
                      "projection_payloads": {"standalone_compatibility": {
                          "scripts/canonical_hot_projection.py": (SCRIPTS / "canonical_hot_projection.py").read_bytes()}}}
        exec(compile(ast.Module(body=functions, type_ignores=[]), str(path), "exec"), self.scope)

    def test_complete_new_helper_population_has_actual_callers(self):
        shell = self.scope["caller_invokes"]
        library = self.scope["captured_python_library"]
        self.assertTrue(shell("claim-run-rotation.py", (SCRIPTS / "claim-run.sh").read_text()))
        self.assertTrue(shell("read-canonical-pair.py", (SCRIPTS / "validate-run-root.sh").read_text()))
        self.assertTrue(shell("read-canonical-pair.py", (SCRIPTS / "validate-phase.sh").read_text()))
        self.assertTrue(library("rotate-canonical-state.py", (SCRIPTS / "claim-run-rotation.py").read_text()))
        self.assertTrue(library("canonical_hot_projection.py", (SCRIPTS / "rotate-canonical-state.py").read_text()))

    def test_filename_mentions_or_unexecuted_buffers_do_not_count_as_library_routes(self):
        library = self.scope["captured_python_library"]
        for helper, caller in (("rotate-canonical-state.py", "claim-run-rotation.py"),
                               ("canonical_hot_projection.py", "rotate-canonical-state.py")):
            source = (SCRIPTS / caller).read_text()
            self.assertFalse(library(helper, source.replace("exec(compile(", "print(compile(")))
            self.assertFalse(library(helper, '# "' + helper + '"\n'))
        primary = (SCRIPTS / "rotate-canonical-state.py").read_text()
        primary = re.sub(r"(_HOT_PROJECTION_MODULE_SHA256 = ')[0-9a-f]{64}(')", r"\g<1>" + "0" * 64 + r"\2", primary)
        self.assertFalse(library("canonical_hot_projection.py", primary))

    def test_python_echo_or_c_string_is_not_an_automatic_caller(self):
        invokes = self.scope["caller_invokes"]
        body = 'py=(python3)\nreader="/safe/read-canonical-pair.py"\n'
        self.assertFalse(invokes("read-canonical-pair.py", body + 'echo "${py[@]}" "$reader"\n'))
        self.assertFalse(invokes("read-canonical-pair.py", body + '"${py[@]}" -c "$reader"\n'))

    def test_ref_roles_are_disjoint_and_archive_denominator_excludes_retention_subpaths(self):
        registry = json.loads((ROOT / "skills/implementaudit/references/canonical-state-ref-namespaces.json").read_text())
        rows = registry["role_patterns"]
        self.assertEqual(len({row["role"] for row in rows}), len(rows))
        prefix = "refs/implementaudit/state-archives/reader-controller/"
        for suffix, role in (("G0002", "prepared-state-archive"), ("epochs/G0002", "retained-transition"),
                             ("epochs/G0002-publication", "retained-publication-intent"),
                             ("objects/" + "a" * 40, "retained-object")):
            matched = [row for row in rows if re.fullmatch(row["fullmatch"], prefix + suffix)]
            self.assertEqual([row["role"] for row in matched], [role])
            self.assertEqual(matched[0]["archive_anchor"], role == "prepared-state-archive")
        for suffix in ("G0000", "G00ff", "G0002/extra", "epochs/G0000", "objects/" + "a" * 64):
            self.assertFalse(any(re.fullmatch(row["fullmatch"], prefix + suffix) for row in rows))

    def test_required_boundary_contract_retains_unresolved_execution_without_authority(self):
        child = (ROOT / "skills/audit-state/SKILL.md").read_text()
        continuity = (ROOT / "skills/implementaudit/references/continuity.md").read_text()
        for token in ("CURRENTNESS_DISPOSITION=UNRESOLVED", "mandatory bounded execution",
                      "accepted consumption", "AUTHORITY_OWNERSHIP=NONE", "CURRENTNESS_OWNERSHIP=NONE"):
            self.assertIn(token, child)
        for token in ("Two actual compactions", "accepted JOIN", "original-prefix", "zero-model",
                      "MIGRATED_RESUME_REQUIRES_CANONICAL_SUCCESSOR", "CANONICAL_NATIVE_GUARD_PROFILE_UNSUPPORTED"):
            self.assertIn(token, continuity)

    def test_public_native_modes_are_complete_and_resume_tokens_are_explicit(self):
        source = (SCRIPTS / "claim-run.sh").read_text()
        actual = self.scope["claim_public_modes"](source)
        contract = (ROOT / "skills/implementaudit/references/repo-state-comparison.md").read_text()
        declared = [line.split("|")[1] for line in contract.splitlines() if line.startswith("helper-mode: claim-run.sh|")]
        self.assertEqual(sorted(declared), actual)
        self.assertIn("--resolve-resume-generation", actual)
        self.assertIn("--read-resume-state", actual)
        for name in ("--read-resume-state", "--resume-controller"):
            row = next(line for line in contract.splitlines() if line.startswith("helper-mode: claim-run.sh|" + name + "|"))
            self.assertIn("--expected-pointer <pointer-token>", row)
            self.assertIn("--expected-invalidation <invalidation-token>", row)
        changed = source.replace('case "${1:-}" in\n', 'case "${1:-}" in\n  --unmapped-native-reader) exit 1 ;;\n', 1)
        self.assertNotEqual(sorted(declared), self.scope["claim_public_modes"](changed), "new public mode disappeared from the census")
        with self.assertRaises(SystemExit):
            self.scope["claim_public_modes"](source.replace('case "${1:-}" in\n', 'case "$unbound" in\n', 1))


if __name__ == "__main__":
    unittest.main(verbosity=2)
