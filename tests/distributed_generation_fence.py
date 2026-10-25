#!/usr/bin/env python3
"""Actual protected-sink controls; derived instrumentation is never shipped."""

import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import time


sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "skills/implementaudit/scripts/apply-observed-mutation.sh"
CLAIM = ROOT / "skills/implementaudit/scripts/claim-run.sh"
TEMPLATES = ROOT / "skills/implementaudit/templates"
CONTROLLER = "d48-fence"
PREIMAGE = b"ORIGINAL\n"
CANDIDATE = b"CURRENT\n"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


class Fixture:
    def __init__(self, base):
        self.base = base
        self.repo = base / "repo"
        self.repo.mkdir(parents=True)
        self.env = {key: value for key, value in os.environ.items()
                    if not key.startswith(("GIT_", "IMPLEMENTAUDIT_"))}
        self.env["IMPLEMENTAUDIT_BASE"] = ".IMPLEMENTAUDIT/runs"
        self.env["PYTHONDONTWRITEBYTECODE"] = "1"
        self.run_command(["git", "init", "-q"])
        self.run_command(["git", "config", "user.email", "d48-fixture@example.invalid"])
        self.run_command(["git", "config", "user.name", "d48-fixture"])
        (self.repo / "fixture-seed").write_text("D48-C02 protected sink fixture\n")
        self.run_command(["git", "add", "fixture-seed"])
        self.run_command(["git", "commit", "-q", "-m", "fixture"])
        self.run_rel = self.run_command(
            ["bash", str(CLAIM), "--controller", CONTROLLER, "d48-fence"]
        ).stdout.strip()
        self.run = self.repo / self.run_rel
        for name in ("STATE.md", "PROTOCOL.md", "ROADMAP.md", "THINKING.md",
                     "sidecars.md", "tools.md", "context.md"):
            shutil.copyfile(TEMPLATES / name, self.run / name)
        roadmap = self.run / "ROADMAP.md"
        roadmap.write_text(roadmap.read_text().replace(
            "| 1 |  |  | - |  |  |  | open |\n", ""
        ) + "| 1 | D48-C02 cooperating protected mutation |\n")
        (self.repo / "target").write_bytes(PREIMAGE)
        (self.repo / "artifacts").mkdir()
        self.candidate = self.repo / "artifacts/candidate.bin"
        self.candidate.write_bytes(CANDIDATE)
        (self.run / "phases").mkdir()
        phase = (ROOT / "fixtures/phase-validation/valid-full-spec.md").read_text()
        phase = phase.replace("Phase: 1 of 3", "Phase: 1 of 1")
        phase = phase.replace("Run root: .IMPLEMENTAUDIT/runs/add-settings-Xy9Zq1",
                              "Run root: " + self.run_rel)
        phase = phase.replace("Baseline ref: abc123def456", "Baseline ref: HEAD")
        phase = phase.replace("Owner/source: src/routes/settings.ts",
                              "Owner/source: issue:#200 D48-C02")
        needle = "- Step 1: Create the settings route — target: src/routes/settings.ts (registerSettingsRoutes); change: add GET /api/settings handler behind requireAuth from src/middleware/auth.ts; verify: npm run build; expected: exit 0 with no errors"
        require(phase.count(needle) == 1, "phase authority anchor is not unique")
        phase = phase.replace(needle, needle + '\n  mutation-authority: {"operation":"replace","source":"target","destination":null}')
        phase = phase.replace(
            "In scope: src/routes/settings.ts, tests/settings.test.ts, src/app.ts",
            'In scope: D48-C02 protected mutation fixture\nMutation scope: {"in":["target"],"out":["README.md"]}',
        )
        (self.run / "phases/phase-1.md").write_text(phase)
        head = self.run_command(["git", "rev-parse", "HEAD"]).stdout.strip()
        tree = self.run_command(["git", "rev-parse", "HEAD^{tree}"]).stdout.strip()
        state_path = self.run / "STATE.md"
        state = state_path.read_text().replace("| Run root |  |", f"| Run root | `{self.run_rel}` |")
        state = state.replace("| Next action |  |", "| Next action | exercise protected mutation fence |")
        state = re.sub(r"^Current epoch: .+$", "Current epoch: G0002", state, flags=re.M)
        anchor = "| Epoch | Boundary provenance | Established at | Repo identity | Reconciled | Notes |\n|---|---|---|---|---|---|"
        require(state.count(anchor) == 1, "state epoch anchor is not unique")
        state = state.replace(anchor, anchor + f"\n| G0002 | new-session | 2026-08-20T00:00:00Z | repo at `{head}` / `{tree}` | yes | D48-C02 fixture reconciliation complete |")
        state_path.write_text(state)
        self.receipt = self.run_command([
            "bash", str(CLAIM), "--resume-controller", CONTROLLER,
            "--boundary", "new-session", "--epoch", "G0002",
        ]).stdout.strip()
        self.run_command(["bash", str(CLAIM), "--verify-resume-receipt", self.receipt])
        self.fence_path = self.run / "mutation-fences/phase-1-step-1.json"
        self.fence_path.parent.mkdir()
        self.fence = {
            "schema": "implementaudit.protected-mutation-fence.v1",
            "phase": 1, "step": 1, "source_path": "target",
            "protected_target": {"sha256": hashlib.sha256(PREIMAGE).hexdigest(),
                                 "byte_length": len(PREIMAGE)},
            "controller_generation": "G0002", "authority_generation": "G0002",
            "protected_generation": "G0002", "verified_resume_receipt": self.receipt,
        }
        self.write_fence()

    def run_command(self, command, cwd=None, check=True, timeout=15):
        result = subprocess.run(command, cwd=cwd or self.repo, env=self.env,
                                text=True, capture_output=True, timeout=timeout)
        if check:
            require(result.returncode == 0,
                    f"setup command failed ({result.returncode}): {command!r}: {result.stderr}")
        return result

    def write_fence(self):
        self.fence_path.write_text(json.dumps(self.fence, sort_keys=True, separators=(",", ":")) + "\n")

    def command(self, helper=HELPER, required=False):
        command = ["bash", str(helper), "--repo-root", str(self.repo),
                   "--run-root", str(self.run), "--phase", "1", "--step", "1",
                   "--preimage", str(self.repo / "target"), "--candidate", str(self.candidate)]
        if required:
            command.append("--require-generation-fence")
        return command

    def invoke(self, helper=HELPER, required=False, timeout=15):
        result = self.run_command(self.command(helper, required), check=False, timeout=timeout)
        (self.base / "sink.out").write_text(result.stdout)
        (self.base / "sink.err").write_text(result.stderr)
        try:
            payload = json.loads(result.stdout)
        except ValueError as error:
            raise AssertionError(f"sink returned non-JSON rc={result.returncode}: {result.stderr}") from error
        return result, payload

    def ref(self, name):
        return self.run_command(["git", "rev-parse", "--verify", name]).stdout.strip()

    def instrument(self, phase, insertion):
        """Use the existing strip-byte-equal copy pattern, no product env hook."""
        original = HELPER.read_text()
        locator = 'script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"'
        derived_locator = "script_dir=" + shlex.quote(str(HELPER.parent))
        marker = "    # R36_INSTRUMENT_INSERT\n"
        require(original.count(locator) == 1 and original.count(marker) == 1,
                "helper instrumentation anchors are not unique")
        injected = f"    if phase == {phase!r}:\n" + "".join(
            "        " + line + "\n" for line in insertion.splitlines())
        derived = original.replace(locator, derived_locator).replace(marker, marker + injected)
        require(derived.replace(injected, "").replace(derived_locator, locator) == original,
                "derived helper does not strip byte-equal")
        helper = self.base / "instrumented-apply-observed-mutation.sh"
        helper.write_text(derived)
        return helper


def concurrent_controller(fixture):
    linked = fixture.base / "linked"
    fixture.run_command(["git", "worktree", "add", "-q", "--detach", str(linked), "HEAD"])
    claim_id = dict(line.split("=", 1) for line in
                    (fixture.run / ".claimed").read_text().splitlines())["claim_id"]
    ref = f"refs/implementaudit/controllers/{CONTROLLER}"
    before = fixture.ref(ref)
    barrier = fixture.base / "barrier"
    barrier.mkdir()
    helper = fixture.instrument("first-protected-effect-boundary", f"""gate = Path({str(barrier)!r})
(gate / 'paused').touch()
for _ in range(1500):
    if (gate / 'release').exists():
        break
    time.sleep(0.02)
else:
    raise RuntimeError('D48 test barrier timed out')""")
    writer_command = ["bash", str(CLAIM), "--controller", CONTROLLER,
                      "--supersede-claim", claim_id, "d48-linked-successor"]
    writer = None
    with (barrier / "sink.out").open("w") as sink_out, (barrier / "sink.err").open("w") as sink_err:
        sink = subprocess.Popen(fixture.command(helper), cwd=fixture.repo, env=fixture.env,
                                text=True, stdout=sink_out, stderr=sink_err)
        try:
            deadline = time.monotonic() + 15
            while not (barrier / "paused").exists() and sink.poll() is None and time.monotonic() < deadline:
                time.sleep(0.01)
            require((barrier / "paused").exists(),
                    "sink did not reach protected boundary: " + (barrier / "sink.err").read_text())
            require((fixture.repo / "target").read_bytes() == PREIMAGE,
                    "protected target changed before barrier")
            writer = subprocess.Popen(writer_command, cwd=linked, env=fixture.env,
                                      text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            deadline = time.monotonic() + 2
            while writer.poll() is None and time.monotonic() < deadline:
                time.sleep(0.01)
            published_during_effect_window = fixture.ref(ref) != before
            (barrier / "release").touch()
            sink_rc = sink.wait(timeout=15)
            writer_out, writer_err = writer.communicate(timeout=15)
            (barrier / "writer.out").write_text(writer_out)
            (barrier / "writer.err").write_text(writer_err)
            sink_result = json.loads((barrier / "sink.out").read_text())
            evidence = {
                "controller_published_while_sink_paused": published_during_effect_window,
                "sink_exit": sink_rc, "sink_status": sink_result.get("status"),
                "writer_exit": writer.returncode,
                "protected_target_hex": (fixture.repo / "target").read_bytes().hex(),
            }
            (barrier / "evidence.json").write_text(json.dumps(evidence, indent=2) + "\n")
            require(not published_during_effect_window,
                    "D48-C02 concurrent-controller RED: linked-worktree controller publication crossed the protected effect boundary; " + json.dumps(evidence, sort_keys=True))
            require(sink_rc == 0 and sink_result.get("status") == "COMMITTED"
                    and (fixture.repo / "target").read_bytes() == CANDIDATE,
                    "current sink failed while cooperating publication was excluded: " + json.dumps(evidence))
            if writer.returncode != 0:
                require("cannot lock ref" in writer_err and ".lock" in writer_err,
                        "competing publication failed for a setup reason: " + writer_err)
                retry = fixture.run_command(writer_command, cwd=linked)
                require(bool(retry.stdout.strip()), "publication retry returned no claim")
            require(fixture.ref(ref) != before, "controller publication did not succeed after guard release")
        finally:
            (barrier / "release").touch()
            for child in (sink, writer):
                if child is not None and child.poll() is None:
                    child.terminate()
                    try:
                        child.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        child.kill()
                        child.wait(timeout=5)


V2_RESULT_FIELDS = {
    "schema", "transaction_id", "claim_id", "phase", "step", "authority_binding_sha256",
    "coordination_scope", "operation", "status", "reason_code", "source_path",
    "destination_path", "pre_identities", "candidate_identities", "post_identities",
    "planned_effect_set", "planned_effect_set_sha256", "actual_effect_set", "residue",
}
FENCE_EVIDENCE_FIELDS = {
    "identity_bindings", "authority_publication_guard", "generation_fence_disposition",
}


def assert_stored_schemas(fixture, payload, protected):
    transaction = fixture.run / "mutation-transactions" / payload["transaction_id"]
    expected = {
        "authority.json": ("authority", {
            "schema", "transaction_id", "created_at_utc", "claim", "phase", "operation",
            "source", "destination", "observations", "planned_effect_set",
            "planned_effect_set_sha256",
        }),
        "journal.json": ("journal", {
            "schema", "transaction_id", "authority_sha256", "status", "pre_identities",
            "candidate_identities", "current_identities", "planned_effect_set_sha256",
            "actual_effect_set", "residue", "updated_at_utc",
        }),
    }
    for name, (kind, fields) in expected.items():
        path = transaction / name
        if not path.exists() and name == "journal.json":
            continue
        record = json.loads(path.read_bytes())
        version = 3 if protected else 2
        require(record["schema"] == f"implementaudit.observation-bound-mutation.{kind}.v{version}",
                f"{kind} schema does not distinguish protected and ordinary records")
        require(set(record) == fields | (FENCE_EVIDENCE_FIELDS if protected else set()),
                f"{kind} record changed its versioned keyset")
    saved_result = json.loads((transaction / "result.json").read_bytes())
    require(saved_result["schema"] == payload["schema"] and set(saved_result) == set(payload),
            "persisted result and stdout disagree on their versioned contract")


def assert_observed_result_prefix(fixture, payload, promoted=True):
    transaction = fixture.run / "mutation-transactions" / payload["transaction_id"]
    saved = json.loads((transaction / "result.json").read_bytes())
    relative = transaction.relative_to(fixture.repo).as_posix()
    path = relative + ("/result.tmp" if promoted else "/result.json")
    expected = [("repo", path, effect) for effect in ("create", "write", "fsync")]
    if promoted:
        expected += [("repo", path, "replace"), ("repo", relative + "/result.json", "replace")]
    expected.append(("repo", relative, "fsync"))
    actual = payload["actual_effect_set"]
    suffix = actual[-len(expected):]
    require([(row["scope"], row["path"], row["effect"]) for row in suffix] == expected
            and all(row["outcome"] == "applied" for row in suffix),
            "live result lost its completed publication suffix")
    require(saved["actual_effect_set"] == actual[:-len(expected)],
            "persisted result is not the exact completed prefix before publication")
    require({key: value for key, value in saved.items() if key != "actual_effect_set"} ==
            {key: value for key, value in payload.items() if key != "actual_effect_set"},
            "persisted result changed non-effect semantics")


def assert_result(fixture, result, payload, status, reason, target=PREIMAGE, protected=True):
    require(payload.get("status") == status and payload.get("reason_code") == reason,
            f"expected {status}/{reason}, got {payload.get('status')}/{payload.get('reason_code')}; {result.stderr}")
    expected_exit = {"COMMITTED": 0, "NO_CHANGE": 0, "REJECTED_NO_MUTATION": 64,
                     "CONFLICT_REBASE": 65, "MUTATION_FAILED_ROLLED_BACK": 71,
                     "UNSUPPORTED_OWNER_DECISION": 77, "UNKNOWN": 78}[status]
    require(result.returncode == expected_exit, f"status/exit mismatch: {result.returncode}")
    require((fixture.repo / "target").read_bytes() == target, "protected target bytes differ")
    version = 3 if protected else 2
    require(payload.get("schema") == f"implementaudit.observation_bound_mutation.v{version}",
            "result schema does not distinguish protected and ordinary records")
    fields = V2_RESULT_FIELDS | (FENCE_EVIDENCE_FIELDS | {
        "retry_permitted", "terminal_closure_claim"} if protected else set())
    require(set(payload) == fields, "result changed its versioned keyset")
    if protected:
        require(payload.get("retry_permitted") is False, "sink granted retry authority")
    if status == "UNKNOWN":
        require(payload.get("terminal_closure_claim") == "PROHIBITED",
                "unknown fence allowed terminal closure")
    if status in {"UNKNOWN", "REJECTED_NO_MUTATION", "CONFLICT_REBASE", "UNSUPPORTED_OWNER_DECISION"}:
        require(not any(row.get("scope") == "repo" and row.get("path") == "target"
                        for row in payload["actual_effect_set"]),
                "refusal performed a protected target effect")


def persisted_result_prefix(fixture):
    # The saved evidence must contain exactly the completed observations at
    # serialization, not its own not-yet-executed publication effects.
    captured_path = fixture.base / "result-prefix-capture.json"
    refs_before = fixture.run_command(["git", "show-ref"]).stdout
    helper = fixture.instrument("init", f"""capture_path = Path({str(captured_path)!r})
original_write_new = write_new
captures = []
def capture_result_write(path, data, *pos, **kw):
    if path in {{RESULT, RESULT_TMP}}:
        captures.append({{"path": repo_relative(path), "completed": list(actual),
                         "serialized": json.loads(data)}})
        capture_path.write_text(json.dumps(captures, sort_keys=True))
    return original_write_new(path, data, *pos, **kw)
globals()["write_new"] = capture_result_write""")
    result, payload = fixture.invoke(helper, required=True)
    assert_result(fixture, result, payload, "COMMITTED", "NONE", CANDIDATE)
    assert_guard_effects(fixture, payload)
    assert_stored_schemas(fixture, payload, protected=True)
    require(fixture.run_command(["git", "show-ref"]).stdout == refs_before,
            "result capture changed authority refs")
    captures = json.loads(captured_path.read_bytes())
    transaction = fixture.run / "mutation-transactions" / payload["transaction_id"]
    relative = transaction.relative_to(fixture.repo).as_posix()
    require([row["path"] for row in captures] ==
            [relative + "/result.json", relative + "/result.tmp"],
            "capture missed checkpoint or final result publication")
    require([row["serialized"]["status"] for row in captures] ==
            ["RECOVERY_REQUIRED", "COMMITTED"],
            "captured results changed target-operation dispositions")
    saved = json.loads((transaction / "result.json").read_bytes())
    require(saved == captures[-1]["serialized"],
            "actual saved result differs from the captured serialization")
    print("D48_RESULT_PREFIX_CAPTURE=" + json.dumps([
        {"path": row["path"], "completed_count": len(row["completed"]),
         "serialized_count": len(row["serialized"]["actual_effect_set"])}
        for row in captures], sort_keys=True), flush=True)
    for row in captures:
        snapshot = row["serialized"]
        require(snapshot["actual_effect_set"] == row["completed"],
                "D48-C03 RED: protected persisted result claimed a future effect or lost the completed prefix")
        require(any(effect["scope"] == "repo" and effect["path"] == "target"
                    and effect["effect"] == "link" and effect["outcome"] == "applied"
                    for effect in snapshot["actual_effect_set"]),
                "persisted prefix omitted completed protected target publication")
        require(any(identity["path"] == "target" and
                    identity["identity"].get("sha256") == hashlib.sha256(CANDIDATE).hexdigest()
                    for identity in snapshot["post_identities"]),
                "persisted prefix lost authoritative target readback")
        require(snapshot["authority_publication_guard"]["state"] == "RELEASED"
                and snapshot["retry_permitted"] is False,
                "persisted prefix changed guard or retry disposition")
    completed = captures[-1]["completed"]
    require(payload["actual_effect_set"][:len(completed)] == completed,
            "live result rewrote the completed serialized prefix")
    suffix = payload["actual_effect_set"][len(completed):]
    require([(row["scope"], row["path"], row["effect"]) for row in suffix] == [
        ("repo", relative + "/result.tmp", "create"),
        ("repo", relative + "/result.tmp", "write"),
        ("repo", relative + "/result.tmp", "fsync"),
        ("repo", relative + "/result.tmp", "replace"),
        ("repo", relative + "/result.json", "replace"),
        ("repo", relative, "fsync"),
    ] and all(row["outcome"] == "applied" for row in suffix),
            "live result omitted or invented a completed publication effect")
    require(all(row["sequence"] == index for index, row in
                enumerate(payload["actual_effect_set"], 1)),
            "live result effect sequence is not contiguous")
    require({key: value for key, value in saved.items() if key != "actual_effect_set"} ==
            {key: value for key, value in payload.items() if key != "actual_effect_set"},
            "persisted prefix changed non-effect result semantics")


def persisted_journal_prefix(fixture, ordinary=False, fail_sync=False):
    # A completed checkpoint cannot observe its own later publication. Keep the
    # ordinary v2 convention while rejecting prospective v3 applied rows.
    if ordinary:
        fixture.fence_path.unlink()
        fixture.fence_path.parent.rmdir()
    captured_path = fixture.base / "journal-prefix-capture.json"
    fault_path = fixture.base / "journal-prefix-fault.json"
    refs_before = fixture.run_command(["git", "show-ref"]).stdout
    helper = fixture.instrument("init", f"""capture_path = Path({str(captured_path)!r})
fault_path = Path({str(fault_path)!r})
original_write_new = write_new
original_persist_journal = persist_journal
original_sync = sync_directory_raw
captures = []
journal_probe = {{"status": None, "failed": False}}
def observed_journal(status, *pos, **kw):
    previous = journal_probe["status"]
    journal_probe["status"] = status
    try:
        return original_persist_journal(status, *pos, **kw)
    finally:
        journal_probe["status"] = previous
def observed_write(path, data, *pos, **kw):
    if path == JOURNAL_TMP:
        captures.append({{"completed": list(actual), "serialized": json.loads(data)}})
        capture_path.write_text(json.dumps(captures, sort_keys=True))
    return original_write_new(path, data, *pos, **kw)
def observed_sync(path):
    if {fail_sync!r} and path == TX and journal_probe["status"] == "COMMITTED" and not journal_probe["failed"]:
        journal_probe["failed"] = True
        fault_path.write_text(json.dumps({{"completed": list(actual),
            "journal": json.loads(JOURNAL.read_bytes())}}, sort_keys=True))
        raise OSError(5, "injected terminal journal directory fsync failure")
    return original_sync(path)
globals()["persist_journal"] = observed_journal
globals()["write_new"] = observed_write
globals()["sync_directory_raw"] = observed_sync""")
    result, payload = fixture.invoke(helper, required=not ordinary)
    require(not result.stderr, "journal probe emitted unexpected diagnostics")
    require((fixture.repo / "target").read_bytes() == CANDIDATE,
            "journal probe lost the completed target operation")
    require(fixture.run_command(["git", "show-ref"]).stdout == refs_before,
            "journal probe changed authority refs")
    assert_stored_schemas(fixture, payload, protected=not ordinary)
    if ordinary:
        assert_result(fixture, result, payload, "COMMITTED", "NONE", CANDIDATE, protected=False)
    else:
        assert_guard_effects(fixture, payload)
        assert_observed_result_prefix(fixture, payload, promoted=not fail_sync)
        require(payload["retry_permitted"] is False, "journal probe granted retry authority")
        if fail_sync:
            require(result.returncode == 78 and payload["status"] == "UNKNOWN"
                    and payload["reason_code"] == "MANUAL_RECONCILIATION"
                    and payload["terminal_closure_claim"] == "PROHIBITED",
                    "journal persistence uncertainty permitted completion")
        else:
            assert_result(fixture, result, payload, "COMMITTED", "NONE", CANDIDATE)
    transaction = fixture.run / "mutation-transactions" / payload["transaction_id"]
    relative = transaction.relative_to(fixture.repo).as_posix()
    authority = transaction / "authority.json"
    saved = json.loads((transaction / "result.json").read_bytes())
    if ordinary:
        require(saved == payload, "ordinary v2 saved/live result compatibility changed")
    captures = json.loads(captured_path.read_bytes())
    statuses = ["PLANNED", "DISPLACEMENT_DURABLE", "PUBLICATION_DURABLE"]
    if not ordinary:
        statuses.append("COMMITTED")
    require([row["serialized"]["status"] for row in captures] == statuses,
            "journal probe missed an execution checkpoint")
    print("D48_JOURNAL_PREFIX_CAPTURE=" + json.dumps([
        {"status": row["serialized"]["status"], "completed_count": len(row["completed"]),
         "serialized_count": len(row["serialized"]["actual_effect_set"])}
        for row in captures], sort_keys=True), flush=True)
    actual = payload["actual_effect_set"]
    planned = {(row["scope"], row["path"]): row["allowed_effects"]
               for row in payload["planned_effect_set"]}
    require(payload["planned_effect_set_sha256"] == hashlib.sha256(json.dumps(
        payload["planned_effect_set"], sort_keys=True, separators=(",", ":"),
        ensure_ascii=False).encode()).hexdigest(), "journal probe lost the effect-plan digest")
    for index, row in enumerate(actual, 1):
        require(row["sequence"] == index and
                row["effect"] in planned[(row["scope"], row["path"])],
                "journal probe lost sequence or planned-effect membership")
    expected_suffix = [("repo", relative + "/journal.tmp", effect)
                       for effect in ("create", "write", "fsync", "replace")]
    expected_suffix += [("repo", relative + "/journal.json", "replace"),
                        ("repo", relative, "fsync")]
    if fail_sync:
        require(fault_path.is_file(), "journal sync fault was not reached")
        fault = json.loads(fault_path.read_bytes())
        journal = json.loads((transaction / "journal.json").read_bytes())
        require(journal == fault["journal"] == captures[-1]["serialized"],
                "retained journal differs from its captured serialization")
        require(fault["completed"] == actual[:len(fault["completed"])]
                and len(fault["completed"]) == len(captures[-1]["completed"]) + 5,
                "journal fault lost the five completed publication operations")
        residues = {row["path"] for row in payload["residue"]}
        require(relative in residues and relative + "/journal.json" in residues,
                "journal persistence uncertainty lost transaction/journal custody")
    else:
        require(not fault_path.exists() and not (transaction / "journal.json").exists()
                and not payload["residue"], "successful journal publication retained uncertainty")
    for index, captured in enumerate(captures):
        snapshot = captured["serialized"]
        completed = captured["completed"]
        count = 5 if fail_sync and index == len(captures) - 1 else 6
        suffix = actual[len(completed):len(completed) + count]
        require(actual[:len(completed)] == completed and
                [(row["scope"], row["path"], row["effect"]) for row in suffix] == expected_suffix[:count]
                and all(row["outcome"] == "applied" for row in suffix),
                "live result lost a completed journal publication suffix")
        require(snapshot["transaction_id"] == payload["transaction_id"]
                and snapshot["authority_sha256"] == hashlib.sha256(authority.read_bytes()).hexdigest()
                and snapshot["planned_effect_set_sha256"] == payload["planned_effect_set_sha256"],
                "journal checkpoint lost its transaction/authority/plan identity")
        target = next(row["identity"] for row in snapshot["current_identities"] if row["path"] == "target")
        if snapshot["status"] == "DISPLACEMENT_DURABLE":
            require(target["kind"] == "absent", "journal lost observed displacement")
        else:
            expected = PREIMAGE if snapshot["status"] == "PLANNED" else CANDIDATE
            require(target.get("sha256") == hashlib.sha256(expected).hexdigest(),
                    "journal lost authoritative target readback")
        if ordinary:
            require(snapshot["schema"] == "implementaudit.observation-bound-mutation.journal.v2"
                    and snapshot["actual_effect_set"] == completed + suffix,
                    "ordinary v2 journal prospective compatibility changed")
        else:
            require(snapshot["schema"] == "implementaudit.observation-bound-mutation.journal.v3"
                    and snapshot["identity_bindings"]["effect"] == payload["identity_bindings"]["effect"],
                    "protected journal lost its versioned effect identity")
            require(snapshot["actual_effect_set"] == completed,
                    "D48-C03 RED: protected journal claimed a future effect or lost the completed serialization prefix")


def current_generation(fixture, timeout=15):
    result, payload = fixture.invoke(required=True, timeout=timeout)
    assert_result(fixture, result, payload, "COMMITTED", "NONE", CANDIDATE)
    require(payload.get("generation_fence_disposition") == "VERIFIED", "fence was not verified")
    require(payload["identity_bindings"]["generation"]["receipt_ref"] + "@" +
            payload["identity_bindings"]["generation"]["receipt_oid"] == fixture.receipt,
            "result lost the exact verified receipt identity")
    assert_guard_effects(fixture, payload)
    assert_stored_schemas(fixture, payload, protected=True)


def cheap_local(fixture):
    fixture.fence_path.unlink()
    fixture.fence_path.parent.rmdir()
    result, payload = fixture.invoke()
    assert_result(fixture, result, payload, "COMMITTED", "NONE", CANDIDATE, protected=False)
    assert_stored_schemas(fixture, payload, protected=False)
    require(not fixture.fence_path.parent.exists(), "ordinary local mutation created fence custody")
    require(not any(row["scope"] == "git-common" for row in payload["planned_effect_set"]),
            "ordinary local mutation planned distributed authority locks")


def early_result(protected, no_change):
    def control(fixture):
        if not protected:
            fixture.fence_path.unlink()
        if no_change:
            fixture.candidate.write_bytes(PREIMAGE)
            status, reason = "NO_CHANGE", "NONE"
        else:
            fixture.candidate.unlink()
            status, reason = "REJECTED_NO_MUTATION", "PREIMAGE_REQUIRED"
        result, payload = fixture.invoke(required=protected)
        assert_result(fixture, result, payload, status, reason, protected=protected)
        require(not payload["actual_effect_set"], "early result performed an effect")
        if protected:
            require(payload["authority_publication_guard"] is None and
                    payload["generation_fence_disposition"] == "NOT_EVALUATED",
                    "early protected result invented a verified fence or guard")
    return control


def historical_legacy_receipt(fixture):
    # Preserve the historical-v1 fixture accepted by continuity-contract.test.sh;
    # fresh minting canonicalises aliases, so this is verified historical data.
    state = fixture.run / "STATE.md"
    state.write_text(state.read_text().replace("Current epoch: G0002", "Current epoch: e1")
                     .replace("| G0002 | new-session |", "| e1 | new-session |"))
    claim_id = dict(line.split("=", 1) for line in
                    (fixture.run / ".claimed").read_text().splitlines())["claim_id"]
    fields = ["implementaudit.continuity-receipt.v1", CONTROLLER,
        fixture.ref(f"refs/implementaudit/controllers/{CONTROLLER}"), claim_id, fixture.ref("HEAD"),
        fixture.run_command(["git", "rev-parse", "HEAD^{tree}"]).stdout.strip(),
        hashlib.sha256(state.read_bytes()).hexdigest(),
        hashlib.sha256((fixture.run / "ROADMAP.md").read_bytes()).hexdigest(),
        "new-session", "e1", "legacy-currentness"]
    record = fixture.base / "historical-v1-receipt.tsv"
    record.write_bytes("\t".join(fields).encode())
    oid = fixture.run_command(["git", "hash-object", "-w", str(record)]).stdout.strip()
    ref = f"refs/implementaudit/continuity-receipts/{CONTROLLER}/e1"  # legacy spelling compatibility fixture
    fixture.run_command(["git", "update-ref", ref, oid])
    fixture.receipt = ref + "@" + oid
    fixture.run_command(["bash", str(CLAIM), "--verify-resume-receipt", fixture.receipt])
    current = fixture.run_command(["bash", str(CLAIM), "--require-current-continuity", CONTROLLER])
    require(current.stdout.strip() == fixture.receipt,
            "real continuity owner did not accept the exact historical token")


def ordinary_legacy_receipt(fixture):
    historical_legacy_receipt(fixture)
    cheap_local(fixture)


def protected_legacy_receipt(fixture):
    historical_legacy_receipt(fixture)
    fixture.fence["verified_resume_receipt"] = fixture.receipt
    fixture.write_fence()
    result, payload = fixture.invoke(required=True)
    assert_result(fixture, result, payload, "UNSUPPORTED_OWNER_DECISION", "STALE_CONTINUITY_RECEIPT")


def assert_guard_effects(fixture, payload, clean=True):
    declared = {(row["scope"], row["path"]): row for row in payload["planned_effect_set"]}
    observed = [row for row in payload["actual_effect_set"] if row["scope"] == "git-common"]
    require(observed, "protected mutation omitted native authority guard effects")
    for row in observed:
        plan = declared.get((row["scope"], row["path"]))
        require(plan is not None and row["effect"] in plan["allowed_effects"],
                "native authority effect was not declared: " + str(row))
    lock_paths = {row["path"] for row in declared.values()
                  if row["scope"] == "git-common" and "authority-ref-lock" in row["roles"]}
    require("HEAD.lock" in lock_paths and
            f"refs/implementaudit/controllers/{CONTROLLER}.lock" in lock_paths,
            "guard omitted HEAD or controller lock custody")
    common = Path(fixture.run_command(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"]).stdout.strip())
    remaining = {path for path in lock_paths if os.path.lexists(common / path)}
    if clean:
        require(not remaining, "normal guard release retained locks: " + str(remaining))
        created = {row["path"] for row in observed if row["effect"] == "create"}
        removed = {row["path"] for row in observed if row["effect"] == "unlink"}
        require(created == lock_paths and removed == created,
                "guard lock creation/removal census is incomplete")
    else:
        require(remaining, "abnormal guard loss did not preserve any physical lock witness")
        guard = payload["authority_publication_guard"]
        require(Path(guard["git_common_dir"]) == common and guard["state"] == "RELEASE_UNCERTAIN",
                "abnormal guard result lost common custody or release uncertainty")
        recorded = set(guard["remaining_lock_paths"])
        require(remaining == recorded, "physical Git lock residue census differs from result")


def disabled_reference_hooks(fixture):
    hooks = fixture.base / "hooks"
    hooks.mkdir()
    sentinel = fixture.base / "reference-transaction-called"
    hook = hooks / "reference-transaction"
    hook.write_text("#!/bin/sh\nprintf '%s\\n' \"$1\" >> " + shlex.quote(str(sentinel)) + "\nexit 1\n")
    hook.chmod(0o700)
    fixture.run_command(["git", "config", "core.hooksPath", str(hooks)])
    ref = f"refs/implementaudit/controllers/{CONTROLLER}"
    probe = subprocess.run(["git", "update-ref", "--stdin"], cwd=fixture.repo, env=fixture.env,
        input=f"start\nverify {ref} {fixture.ref(ref)}\nprepare\nabort\n",
        text=True, capture_output=True, timeout=15)
    require(probe.returncode != 0 and sentinel.exists(),
            "reference-transaction refusing-hook positive control did not execute")
    sentinel.unlink()
    current_generation(fixture)
    require(not sentinel.exists(), "verify-only sink guard executed repository reference-transaction hook")


def native_current_generation(fixture):
    """Real CLI migration, using the existing typed-source fixture factory."""
    factory_path = ROOT / "fixtures/canonical-state-rotation/protected_projection_v2_test.py"
    spec = importlib.util.spec_from_file_location("d48_native_fixture", factory_path)
    factory = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(factory)
    source = json.loads((factory_path.parent / "v2/source.json").read_text())
    bodies = source["bodies"]
    claim_id = dict(line.split("=", 1) for line in
                    (fixture.run / ".claimed").read_text().splitlines())["claim_id"]
    identity = bodies["STATE"]["payload"]["identity"]["value"]
    identity.update(controller_id=CONTROLLER, claim_id=claim_id,
                    run_root_identity=fixture.run_rel,
                    candidate=fixture.ref("HEAD"),
                    tree=fixture.run_command(["git", "rev-parse", "HEAD^{tree}"]).stdout.strip())
    receipt_ref = f"refs/implementaudit/continuity-receipts/{CONTROLLER}/G0003"
    invalidation = fixture.run_command(["bash", str(CLAIM), "--invalidate-continuity", CONTROLLER,
        "--boundary", "new-session", "--event", "d48-native-fixture"]).stdout.strip().split("@")[1]
    for body in bodies.values():
        body["continuity"].update(boundary="new-session", invalidation_oid=invalidation,
                                   continuity_epoch="G0003", projection_generation_id="G0003",
                                   expected_receipt_ref=receipt_ref,
                                   predecessor_receipt_ref_oid=fixture.receipt)
        for item in body["artifact_refs"]:
            if item["role"] == "CONTINUITY_RECEIPT":
                item["locator"] = receipt_ref
    continuation = bodies["STATE"]["payload"]["continuation"]["value"]
    continuation.update(status="IN_PHASE", phase="1", next_action="exercise protected mutation fence")
    native_state = (fixture.run / "STATE.md").read_text().replace("| Status | open |", "| Status | IN_PHASE |")
    native_state = re.sub(r"(?m)^Current epoch:.*\n", "", native_state)
    native_pair = {"STATE": native_state, "ROADMAP": (fixture.run / "ROADMAP.md").read_text()}
    for role, content in native_pair.items():
        bodies[role]["payload"]["native_guards"] = {"owner": role + ".md", "value": {
            "schema_version": "implementaudit.native-guard-profile.v1", "lines": content.splitlines()}}
    artifacts = {key: content.encode() for key, content in source["artifact_texts"].items()}
    native_files = sorted(path for path in fixture.run.rglob("*") if path.is_file()
                          and path.name not in {"STATE.md", "ROADMAP.md", ".claimed", ".controller"}
                          and "mutation-fences" not in path.parts)
    for index, path in enumerate(native_files):
        artifact_id = f"native-{index}"
        bodies["ROADMAP"]["artifact_refs"].append({"artifact_id": artifact_id, "owner": "ROADMAP.md",
            "role": "EVIDENCE", "locator": path.relative_to(fixture.run).as_posix(), "object_format": "sha1"})
        bodies["STATE"]["payload"]["runtime_artifacts"]["value"].append(artifact_id)
        artifacts[artifact_id] = path.read_bytes()
    bodies["STATE"]["history"][0]["payload"]["text"] += " Exact constructed historical observation." * 6500
    pair = factory.render_pair(bodies)
    for role, raw in pair.items():
        (fixture.run / (role + ".md")).write_bytes(raw)
    previous = fixture.run_command(["bash", str(CLAIM), "--resume-controller", CONTROLLER,
        "--boundary", "new-session", "--epoch", "G0003"]).stdout.strip()
    artifacts["receipt"] = fixture.run_command(["git", "cat-file", "blob", previous.split("@")[1]]).stdout.encode()
    for body in bodies.values():
        for item in body["artifact_refs"]:
            if item["role"] != "CONTINUITY_RECEIPT":
                path = fixture.run / item["locator"]
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(artifacts[item["artifact_id"]])
    owner_map = fixture.run / "owner-map.json"
    owner_map.write_text(json.dumps({"schema": "implementaudit.rotation-owner-map.v2",
        "owner_map": factory.build_owner_map(bodies, pair, artifacts)}, sort_keys=True, separators=(",", ":")))
    rotated = fixture.run_command(["bash", str(CLAIM), "--rotate-canonical-state", CONTROLLER,
                                   "--owner-map", str(owner_map)], timeout=30)
    require(json.loads(rotated.stdout)["status"] == "ROTATED", "native fixture did not migrate")
    fixture.receipt = fixture.run_command(["bash", str(CLAIM), "--require-current-continuity", CONTROLLER]).stdout.strip()
    fields = fixture.run_command(["git", "cat-file", "blob", fixture.receipt.split("@")[1]]).stdout.rstrip("\n").split("\t")
    require(fields[0] == "implementaudit.continuity-receipt.v3" and len(fields) == 14,
            "native positive did not use the actual fourteen-field v3 receipt")
    generation = fixture.receipt.split("@")[0].rsplit("/", 1)[1]
    fixture.fence.update(controller_generation=generation, authority_generation=generation,
                         protected_generation=generation, verified_resume_receipt=fixture.receipt)
    fixture.write_fence()
    current_generation(fixture, timeout=60)


def rejected_change(change, reason, status="REJECTED_NO_MUTATION"):
    def control(fixture):
        change(fixture)
        fixture.write_fence()
        result, payload = fixture.invoke()
        assert_result(fixture, result, payload, status, reason)
    return control


def malformed_bytes(data):
    def control(fixture):
        fixture.fence_path.write_bytes(data)
        result, payload = fixture.invoke()
        assert_result(fixture, result, payload, "UNKNOWN", "MANUAL_RECONCILIATION")
    return control


def missing_required(fixture):
    fixture.fence_path.unlink()
    result, payload = fixture.invoke(required=True)
    assert_result(fixture, result, payload, "UNKNOWN", "MANUAL_RECONCILIATION")


def duplicate_member(fixture):
    raw = fixture.fence_path.read_text()
    fixture.fence_path.write_text(raw.replace('{', '{"phase":1,', 1))
    result, payload = fixture.invoke()
    assert_result(fixture, result, payload, "UNKNOWN", "MANUAL_RECONCILIATION")


def duplicate_nested_member(fixture):
    raw = fixture.fence_path.read_text()
    fixture.fence_path.write_text(raw.replace('"protected_target":{', '"protected_target":{"byte_length":9,', 1))
    result, payload = fixture.invoke()
    assert_result(fixture, result, payload, "UNKNOWN", "MANUAL_RECONCILIATION")


def unsafe_fence(kind):
    def control(fixture):
        original = fixture.fence_path.read_bytes()
        if kind == "directory":
            fixture.fence_path.unlink()
            fixture.fence_path.mkdir()
        elif kind == "hardlink":
            os.link(fixture.fence_path, fixture.base / "fence-hardlink")
        elif kind == "symlink":
            referent = fixture.base / "fence-referent.json"
            referent.write_bytes(original)
            fixture.fence_path.unlink()
            fixture.fence_path.symlink_to(referent)
        elif kind == "parent-symlink":
            parent = fixture.fence_path.parent
            referent = fixture.run / "other-fences"
            parent.rename(referent)
            parent.symlink_to(referent, target_is_directory=True)
        elif kind == "fifo":
            fixture.fence_path.unlink()
            os.mkfifo(fixture.fence_path)
        else:
            raise AssertionError("unknown unsafe fence case")
        result, payload = fixture.invoke()
        assert_result(fixture, result, payload, "UNKNOWN", "MANUAL_RECONCILIATION")
    return control


def capture_change(kind):
    def control(fixture):
        if kind == "drift":
            insertion = "FENCE_PATH.write_bytes(FENCE_PATH.read_bytes() + b'\\n')"
            status, reason = "REJECTED_NO_MUTATION", "FENCE_IDENTITY_DRIFT"
        elif kind == "remove":
            insertion = "FENCE_PATH.unlink()"
            status, reason = "UNKNOWN", "MANUAL_RECONCILIATION"
        else:
            raw = fixture.fence_path.read_bytes()
            fixture.fence_path.unlink()
            insertion = f"FENCE_PATH.write_bytes({raw!r})"
            status, reason = "UNKNOWN", "MANUAL_RECONCILIATION"
        helper = fixture.instrument("locks-acquired", insertion)
        result, payload = fixture.invoke(helper)
        assert_result(fixture, result, payload, status, reason)
    return control


def replay(fixture):
    current_generation(fixture)
    fixture.candidate.write_bytes(b"REPLAY\n")
    result, payload = fixture.invoke()
    assert_result(fixture, result, payload, "CONFLICT_REBASE",
                  "PHASE_AUTHORITY_IN_PROGRESS_OR_REPLAY", CANDIDATE)


def rollback(fixture):
    helper = fixture.instrument("init", "globals()['fault'] = 'after-displacement'")
    result, payload = fixture.invoke(helper)
    assert_result(fixture, result, payload, "MUTATION_FAILED_ROLLED_BACK", "NONE")
    require(payload["generation_fence_disposition"] == "VERIFIED", "rollback lost verified fence")
    require(not payload["residue"], "ordinary successful rollback retained residue")
    assert_guard_effects(fixture, payload)


def guard_lost_before_effect(fixture):
    helper = fixture.instrument("first-protected-effect-boundary", "authority_guard.kill()\nauthority_guard.wait(timeout=5)")
    result, payload = fixture.invoke(helper)
    require(result.returncode != 0 and payload["status"] not in {"COMMITTED", "NO_CHANGE"},
            "dead authority guard was reported as success")
    require((fixture.repo / "target").read_bytes() == PREIMAGE,
            "protected target changed after native guard died")
    require(payload.get("retry_permitted") is False and payload.get("terminal_closure_claim") != "ALLOWED",
            "guard loss granted retry or closure")
    assert_guard_effects(fixture, payload, clean=False)


def abort_failure(fixture):
    helper = fixture.instrument("init", """original_release = release_authority_guard
def fail_abort():
    process = globals()['authority_guard']
    if process is not None:
        process.kill()
        process.wait(timeout=5)
    return original_release()
globals()['release_authority_guard'] = fail_abort""")
    result, payload = fixture.invoke(helper)
    require(result.returncode != 0 and payload["status"] not in {
        "COMMITTED", "NO_CHANGE", "REJECTED_NO_MUTATION", "MUTATION_FAILED_NO_STATE_CHANGE", "MUTATION_FAILED_ROLLED_BACK"},
        "abnormal abort concealed target publication or claimed success")
    require((fixture.repo / "target").read_bytes() == CANDIDATE,
            "abort-failure control did not reach terminal target publication")
    require(payload.get("retry_permitted") is False and payload.get("terminal_closure_claim") != "ALLOWED",
            "abnormal abort granted retry or closure")
    assert_guard_effects(fixture, payload, clean=False)


CASES = {
    "concurrent-controller": concurrent_controller,
    "current-generation": current_generation,
    "persisted-result-prefix": persisted_result_prefix,
    "persisted-journal-prefix": persisted_journal_prefix,
    "journal-sync-failure-prefix": lambda fixture: persisted_journal_prefix(fixture, fail_sync=True),
    "ordinary-journal-compatibility": lambda fixture: persisted_journal_prefix(fixture, ordinary=True),
    "native-current-generation": native_current_generation,
    "disabled-reference-hooks": disabled_reference_hooks,
    "cheap-local": cheap_local,
    "ordinary-early-rejection": early_result(False, False),
    "ordinary-early-no-change": early_result(False, True),
    "protected-early-rejection": early_result(True, False),
    "protected-early-no-change": early_result(True, True),
    "ordinary-legacy-receipt": ordinary_legacy_receipt,
    "protected-legacy-receipt": protected_legacy_receipt,
    "wrong-controller": rejected_change(lambda f: f.fence.update(controller_id="foreign"), "WRONG_CONTROLLER"),
    "wrong-receipt": rejected_change(lambda f: f.fence.update(verified_resume_receipt=f.receipt.rsplit("@", 1)[0] + "@" + "0" * 40), "POINTER_RECEIPT_DRIFT"),
    "stale-controller-generation": rejected_change(lambda f: f.fence.update(controller_generation="G0001"), "STALE_CONTROLLER_GENERATION"),
    "stale-authority-generation": rejected_change(lambda f: f.fence.update(authority_generation="G0001"), "STALE_AUTHORITY_GENERATION"),
    "wrong-protected-generation": rejected_change(lambda f: f.fence.update(protected_generation="G0001"), "PROTECTED_GENERATION_MISMATCH"),
    "wrong-target-fingerprint": rejected_change(lambda f: f.fence["protected_target"].update(sha256="0" * 64), "PROTECTED_TARGET_IDENTITY_MISMATCH"),
    "boolean-target-length": rejected_change(lambda f: f.fence["protected_target"].update(byte_length=True), "PROTECTED_TARGET_IDENTITY_MISMATCH"),
    "boolean-phase": rejected_change(lambda f: f.fence.update(phase=True), "PROTECTED_TARGET_IDENTITY_MISMATCH"),
    "wrong-source": rejected_change(lambda f: f.fence.update(source_path="other"), "PROTECTED_TARGET_IDENTITY_MISMATCH"),
    "incapable-sink": rejected_change(lambda f: f.fence.update(sink_capability="UNSUPPORTED"), "MANUAL_RECONCILIATION", "UNKNOWN"),
    "extra-member": rejected_change(lambda f: f.fence.update(unexpected=True), "MANUAL_RECONCILIATION", "UNKNOWN"),
    "missing-member": rejected_change(lambda f: f.fence.pop("protected_target"), "MANUAL_RECONCILIATION", "UNKNOWN"),
    "missing-required": missing_required,
    "malformed-json": malformed_bytes(b"{"),
    "null-root": malformed_bytes(b"null\n"),
    "list-root": malformed_bytes(b"[]\n"),
    "invalid-utf8": malformed_bytes(b"\xff\n"),
    "oversized-fence": malformed_bytes(b" " * 16385),
    "duplicate-member": duplicate_member,
    "duplicate-nested-member": duplicate_nested_member,
    "unsafe-directory": unsafe_fence("directory"),
    "unsafe-hardlink": unsafe_fence("hardlink"),
    "unsafe-symlink": unsafe_fence("symlink"),
    "unsafe-parent-symlink": unsafe_fence("parent-symlink"),
    "after-capture-drift": capture_change("drift"),
    "after-capture-removal": capture_change("remove"),
    "late-fence-on-cheap-route": capture_change("appear"),
    "replay": replay,
    "rollback": rollback,
    "guard-lost-before-effect": guard_lost_before_effect,
    "abort-failure": abort_failure,
}
if hasattr(os, "mkfifo"):
    CASES["unsafe-fifo"] = unsafe_fence("fifo")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=sorted(CASES))
    parser.add_argument("--evidence-dir", type=Path)
    args = parser.parse_args()
    selected = [args.case] if args.case else list(CASES)
    temporary = None
    if args.evidence_dir:
        args.evidence_dir.mkdir(parents=True, exist_ok=True)
        base = Path(tempfile.mkdtemp(prefix="d48-fence-", dir=args.evidence_dir))
    else:
        temporary = tempfile.TemporaryDirectory(prefix="d48-fence-")
        base = Path(temporary.name)
    try:
        for name in selected:
            CASES[name](Fixture(base / name))
            print(f"D48-C02 boundary {name}: PASS", flush=True)
        print(f"D48-C02 boundary controls: {len(selected)}/{len(selected)}", flush=True)
    finally:
        if temporary:
            temporary.cleanup()


if __name__ == "__main__":
    main()
