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


def assert_result(fixture, result, payload, status, reason, target=PREIMAGE):
    require(payload.get("status") == status and payload.get("reason_code") == reason,
            f"expected {status}/{reason}, got {payload.get('status')}/{payload.get('reason_code')}; {result.stderr}")
    expected_exit = {"COMMITTED": 0, "REJECTED_NO_MUTATION": 64,
                     "CONFLICT_REBASE": 65, "MUTATION_FAILED_ROLLED_BACK": 71,
                     "UNSUPPORTED_OWNER_DECISION": 77, "UNKNOWN": 78}[status]
    require(result.returncode == expected_exit, f"status/exit mismatch: {result.returncode}")
    require((fixture.repo / "target").read_bytes() == target, "protected target bytes differ")
    require(payload.get("retry_permitted") is False, "sink granted retry authority")
    if status == "UNKNOWN":
        require(payload.get("terminal_closure_claim") == "PROHIBITED",
                "unknown fence allowed terminal closure")
    if status in {"UNKNOWN", "REJECTED_NO_MUTATION", "CONFLICT_REBASE", "UNSUPPORTED_OWNER_DECISION"}:
        require(not any(row.get("scope") == "repo" and row.get("path") == "target"
                        for row in payload["actual_effect_set"]),
                "refusal performed a protected target effect")


def current_generation(fixture, timeout=15):
    result, payload = fixture.invoke(required=True, timeout=timeout)
    assert_result(fixture, result, payload, "COMMITTED", "NONE", CANDIDATE)
    require(payload.get("generation_fence_disposition") == "VERIFIED", "fence was not verified")
    require(payload["identity_bindings"]["generation"]["receipt_ref"] + "@" +
            payload["identity_bindings"]["generation"]["receipt_oid"] == fixture.receipt,
            "result lost the exact verified receipt identity")
    assert_guard_effects(fixture, payload)


def cheap_local(fixture):
    fixture.fence_path.unlink()
    fixture.fence_path.parent.rmdir()
    result, payload = fixture.invoke()
    assert_result(fixture, result, payload, "COMMITTED", "NONE", CANDIDATE)
    require(payload.get("generation_fence_disposition") == "NOT_APPLICABLE",
            "ordinary local mutation acquired a distributed fence obligation")
    require(not fixture.fence_path.parent.exists(), "ordinary local mutation created fence custody")
    require(not any(row["scope"] == "git-common" for row in payload["planned_effect_set"]),
            "ordinary local mutation planned distributed authority locks")


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
    ref = f"refs/implementaudit/continuity-receipts/{CONTROLLER}/e1"
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
    "native-current-generation": native_current_generation,
    "disabled-reference-hooks": disabled_reference_hooks,
    "cheap-local": cheap_local,
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
