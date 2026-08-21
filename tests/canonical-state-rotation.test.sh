#!/usr/bin/env bash
# R0039 F1 is an immutable, nonmergeable semantic RED checkpoint.
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
checker="$repo_root/scripts/check-canonical-state-rotation.sh"
helper="$repo_root/skills/implementaudit/scripts/rotate-canonical-state.py"
claim_helper="$repo_root/skills/implementaudit/scripts/claim-run.sh"
f2_fixture="$repo_root/fixtures/canonical-state-rotation/f2-draft-archive.json"
f3_fixture="$repo_root/fixtures/canonical-state-rotation/f3-reader-matrix.json"
sequence_cas_fixture="$repo_root/fixtures/canonical-state-rotation/sequence-cas-cases.json"
event_byte_fixture="$repo_root/fixtures/canonical-state-rotation/event-byte-cases.json"
event_schema_fixture="$repo_root/fixtures/canonical-state-rotation/event-schema-cases.json"
evidence_helper="$repo_root/skills/implementaudit/scripts/operational-evidence.py"
tmp="$(mktemp -d)"
trap 'rm -rf -- "$tmp"' EXIT

fail() { printf 'canonical-state-rotation.test: %s\n' "$*" >&2; exit 2; }

case "${1:-}" in
  '') f2_only=false; f3_only=false; clarifications_only=false; event_bytes_only=false; sequence_cas_only=false ;;
  --clarifications-only) f2_only=false; f3_only=false; clarifications_only=true; event_bytes_only=false; sequence_cas_only=false ;;
  --f2-only) f2_only=true; f3_only=false; clarifications_only=false; event_bytes_only=false; sequence_cas_only=false ;;
  --f3-only) f2_only=false; f3_only=true; clarifications_only=false; event_bytes_only=false; sequence_cas_only=false ;;
  --event-bytes-only) f2_only=false; f3_only=false; clarifications_only=false; event_bytes_only=true; sequence_cas_only=false ;;
  --sequence-cas-only) f2_only=false; f3_only=false; clarifications_only=false; event_bytes_only=false; sequence_cas_only=true ;;
  *) fail "usage: canonical-state-rotation.test.sh [--clarifications-only|--f2-only|--f3-only|--event-bytes-only|--sequence-cas-only]" ;;
esac

[ -f "$checker" ] || fail "missing root checker: $checker"
bash -n "$checker" || fail "checker syntax is invalid"
if $clarifications_only; then
  # Catches production that omits event-byte canonicalization, bound cursors,
  # or sequence-CAS isolation despite an apparently valid reader migration.
  bash "$checker" --clarification-fixtures-self-check >/dev/null
  printf '%s\n' \
    'CANONICAL_STATE_ROTATION_CLARIFICATIONS_RED=EVENT_BYTES_CURSOR_SEQUENCE_CAS_NOT_IMPLEMENTED' >&2
  exit 1
fi
if $sequence_cas_only; then
  [ -f "$sequence_cas_fixture" ] || fail "missing sequence-CAS fixture"
  python - "$helper" "$sequence_cas_fixture" "$tmp" <<'PY'
import contextlib
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

spec = importlib.util.spec_from_file_location("rotation_sequence_cas", sys.argv[1])
rotation = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rotation)
native_contract_symbols = {
    "WINDOWS_TRUSTED_GIT_PATHS_V1", "WINDOWS_TRUSTED_OWNER_SIDS_V1",
    "freeze_trusted_executable_v1", "observe_trusted_executable_v1",
}
missing_native_contract = sorted(native_contract_symbols - set(vars(rotation)))
if missing_native_contract:
    raise SystemExit("native Windows trust/fence contract unavailable: "
                     + ",".join(missing_native_contract))
if os.name == "nt":
    if rotation.WINDOWS_TRUSTED_GIT_PATHS_V1 != (
            r"C:\Program Files\Git\cmd\git.exe",
            r"C:\Program Files\Git\bin\git.exe"):
        raise SystemExit("native Windows Git trust roots are not exact")
    if rotation.WINDOWS_TRUSTED_OWNER_SIDS_V1 != frozenset({
            "S-1-5-18", "S-1-5-32-544",
            "S-1-5-80-956008885-3418522649-1831038044-1853292631-2271478464"}):
        raise SystemExit("native Windows owner SID allowlist is not exact")
# This is deliberately the installed helper's physical-owner route, with no
# replacement of either loader.  It must stay independent of both this test's
# cwd and the isolated publication repository built below.
physical_owner = rotation.publication_owner_repo_v1()
physical_context = rotation.load_governed_publication_context_v1()
if (physical_context["repo_path"] != physical_owner
        or set(physical_context) != {"repo_path", "run_root_path", "controller_id", "claim_id", "run_id", "generation_id", "source_epoch", "receipt_oid", "expected_old_pointer_oid", "migration_marker_oid", "publication_guard_refs"}
        or not all(str(physical_context[key]) for key in ("controller_id", "claim_id", "run_id", "generation_id", "source_epoch", "receipt_oid"))):
    raise SystemExit("physical ten-key v2 publication custody loader is incomplete")
physical_cwd = Path.cwd()
os.chdir(Path(sys.argv[3]))
try:
    if rotation.load_governed_publication_context_v1() != physical_context:
        raise SystemExit("physical publication custody changed with caller cwd")
finally:
    os.chdir(physical_cwd)
with open(sys.argv[2], encoding="utf-8") as stream:
    fixture = json.load(stream)
expected = [
    "SC01-single-winner", "SC02-loser-not-queryable", "SC03-loser-not-current",
    "SC04-retry-reallocates", "SC05-winner-data-preserved",
    "SC06-reused-predecessor-sequence", "SC07-noncontiguous-gap",
    "SC08-wrong-predecessor-high-water", "SC09-other-predecessor-manifest",
    "SC10-pointer-manifest-type-confusion",
]
if (fixture.get("schema")
        != "implementaudit.canonical-state-rotation-sequence-cas-cases.v1"
        or [row.get("id") for row in fixture.get("cases", [])] != expected):
    raise SystemExit("sequence-CAS fixture population drift")
sc10_subcases = ["manifest-as-pointer", "noncanonical-pointer-bytes", "noncanonical-manifest-bytes",
                 "manifest-oid", "manifest-digest", "controller-id", "claim-id", "run-id",
                 "generation-id", "source-epoch", "cold-high-water"]
if fixture["cases"][-1].get("subcases") != sc10_subcases:
    raise SystemExit("SC10 fixture subcase population drift")


def error(action, expected=None):
    try:
        action()
    except rotation.RotationError as exc:
        if expected is not None and str(exc) != expected:
            raise SystemExit("expected %r, got %r" % (expected, exc))
        return
    raise SystemExit("expected a fail-closed sequence-CAS refusal")


def git(repo, *args, data=None):
    result = subprocess.run(["git", "-C", str(repo), *args], input=data,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode:
        raise SystemExit(result.stderr.decode("utf-8", "replace"))
    return result.stdout


def blob(repo, data):
    return git(repo, "hash-object", "-w", "--stdin", data=data).decode().strip()


def manifest(before, sequences):
    events = [{"sequence": sequence, "event_id": "iaevt-v1-" + (f"{n:064x}"),
               "segment_digest": "sha256:" + (f"{n:064x}"),
               "record_kind": "finding.closed",
               "source_evidence_id": "iasrc-v1-r0039-archive-case-%d" % n}
              for n, sequence in enumerate(sequences, 1)]
    body = {"schema_version": "implementaudit.state-generation-manifest.v1",
            "query_contract_version": "implementaudit.history-query.v1",
            "controller_id": "controller-1", "claim_id": "a" * 32,
            "run_id": "run-1", "generation_id": "G0001", "source_epoch": "G0001",
            "predecessor_manifest_digest": None, "predecessor_high_water": before,
            "events": events, "record_class_counts": {"finding.closed": len(events)},
            "population_digest": hashlib.sha256(rotation.canonical_json_v1(
                rotation.manifest_population_rows_v1(events))).hexdigest(),
            "high_water": sequences[-1]}
    body["manifest_digest"] = hashlib.sha256(rotation.canonical_json_v1(body)).hexdigest()
    return body


repo = Path(sys.argv[3]) / "sequence-cas-isolated-repo"
subprocess.run(["git", "init", "-q", str(repo)], check=True)
winner = blob(repo, b"winner-candidate")
loser = blob(repo, b"loser-candidate")
ref = "refs/implementaudit/current-generations/cas-controller"
winner_cas = rotation.prepare_trusted_update_ref_transaction_v1(
    repo=repo, ref=ref, new_oid=winner, old_oid=rotation.ZERO_OID, verify_refs=())
loser_cas = rotation.prepare_trusted_update_ref_transaction_v1(
    repo=repo, ref=ref, new_oid=loser, old_oid=rotation.ZERO_OID, verify_refs=())
completed = subprocess.run(winner_cas["argv"], cwd=winner_cas["cwd"], env=winner_cas["env"],
                           input=winner_cas["stdin_bytes"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
if completed.returncode != 0 or rotation.read_back_published_ref_v1(winner_cas) != winner:
    raise SystemExit("SC01 winner publication/readback failed")
completed = subprocess.run(loser_cas["argv"], cwd=loser_cas["cwd"], env=loser_cas["env"],
                           input=loser_cas["stdin_bytes"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
if completed.returncode == 0:
    raise SystemExit("SC02 expected-old loser unexpectedly published")
refs = git(repo, "for-each-ref", "--format=%(objectname)", "refs/implementaudit/").decode().splitlines()
if refs != [winner] or loser in refs:
    raise SystemExit("SC02/SC03 loser is queryable or current")
if rotation.quarantine_unreferenced_cas_loser_v1(repo, loser) != "UNREFERENCED_LOSER_QUARANTINED":
    raise SystemExit("SC02 loser did not produce bounded unreferenced quarantine evidence")
if rotation.allocate_candidate_sequences_v1("00000000000000000001", 1) != ["00000000000000000002"]:
    raise SystemExit("SC04 loser retry did not allocate after winner high-water")
if git(repo, "cat-file", "blob", winner) != b"winner-candidate":
    raise SystemExit("SC05 winner data was not preserved")

base = manifest("00000000000000000000", ["00000000000000000001"])
rotation.verify_generation_manifest_v1(base)
error(lambda: rotation.verify_generation_manifest_v1(manifest(
    "00000000000000000001", ["00000000000000000001"])))
error(lambda: rotation.verify_generation_manifest_v1(manifest(
    "00000000000000000000", ["00000000000000000001", "00000000000000000003"])))
error(lambda: rotation.verify_generation_manifest_v1(manifest(
    "00000000000000000002", ["00000000000000000004"])))

manifest_oid = blob(repo, rotation.canonical_json_v1(base))
previous, previous_bytes = rotation.build_generation_pointer_v1(
    controller_id="controller-1", claim_id="a" * 32, run_id="run-1", generation_id="G0001",
    source_epoch="G0001", predecessor_pointer_oid=None, predecessor_pointer_digest=None,
    generation_manifest_oid=manifest_oid, generation_manifest_digest=base["manifest_digest"],
    cold_high_water=base["high_water"], hot_state_digest="b" * 64, hot_roadmap_digest="c" * 64,
    work_graph_path="WORK_GRAPH.json", work_graph_digest="d" * 64, degraded_state="NONE")
other = dict(base, predecessor_manifest_digest="e" * 64)
other["manifest_digest"] = hashlib.sha256(rotation.canonical_json_v1(
    {key: value for key, value in other.items() if key != "manifest_digest"})).hexdigest()
error(lambda: rotation.verify_generation_successor_tuple_v1(
    pointer=previous, manifest=other, predecessor_oid="f" * 40, predecessor_pointer=previous))
pointer_oid = blob(repo, previous_bytes)
error(lambda: rotation.load_canonical_generation_manifest_oid_v1(repo, pointer_oid))

request = {"schema_version": "implementaudit.history-event.v1", "run_id": "run-1",
           "controller_id": "controller-1", "generation_id": "G0001",
           "sequence": "00000000000000000001", "record_kind": "finding.closed",
           "subject_id": "subject-1", "source_epoch": "G0001", "transition": "APPENDED",
           "status": "CLOSED", "supersedes_event_id": None, "payload": {"case": "segment"}}
segment = dict(request, source_evidence_id="iasrc-v1-r0039-archive-case-1",
               source_locator={"kind": "repo-relative", "root_identity": "sha256:" + "a" * 64,
                               "path": "evidence/file", "host_identity": None},
               source_digest="sha256:" + "b" * 64,
               payload_digest=hashlib.sha256(rotation.canonical_json_v1(request["payload"])).hexdigest())
segment["event_id"] = "iaevt-v1-" + hashlib.sha256(rotation.canonical_json_v1(segment)).hexdigest()
segment_raw = rotation.canonical_json_v1(segment)
segment_event_row = {
    "sequence": segment["sequence"], "event_id": segment["event_id"],
    "segment_digest": "sha256:" + hashlib.sha256(segment_raw).hexdigest(),
    "record_kind": segment["record_kind"],
    "source_evidence_id": segment["source_evidence_id"],
}
segment_manifest = {
    "schema_version": "implementaudit.state-generation-manifest.v1",
    "query_contract_version": "implementaudit.history-query.v1",
    "controller_id": "controller-1", "claim_id": "a" * 32,
    "run_id": "run-1", "generation_id": "G0001", "source_epoch": "G0001",
    "predecessor_manifest_digest": None,
    "predecessor_high_water": "00000000000000000000",
    "events": [segment_event_row], "record_class_counts": {"finding.closed": 1},
    "population_digest": hashlib.sha256(rotation.canonical_json_v1(
        rotation.manifest_population_rows_v1([segment_event_row]))).hexdigest(),
    "high_water": "00000000000000000001",
}
segment_manifest["manifest_digest"] = hashlib.sha256(
    rotation.canonical_json_v1(segment_manifest)).hexdigest()
segment_manifest_raw = rotation.canonical_json_v1(segment_manifest)
segment_oid = blob(repo, segment_raw)
segment_ref = (rotation.EVENT_SEGMENT_PREFIX + "/run-1/G0001/00000000000000000001/" +
               segment["event_id"])
git(repo, "update-ref", segment_ref, segment_oid)
rotation.verify_manifest_segments_core_v1(repo, segment_manifest)
def reidentify(value):
    result = dict(value)
    result.pop("event_id")
    result["event_id"] = "iaevt-v1-" + hashlib.sha256(rotation.canonical_json_v1(result)).hexdigest()
    return result

bad_segment = reidentify(dict(segment, controller_id="controller-2"))
bad_segment_raw = rotation.canonical_json_v1(bad_segment)
bad_oid = blob(repo, bad_segment_raw)
git(repo, "update-ref", segment_ref, bad_oid, segment_oid)
error(lambda: rotation.verify_manifest_segments_core_v1(repo, segment_manifest),
      "manifest row and segment semantics disagree")
git(repo, "update-ref", segment_ref, segment_oid, bad_oid)
bad_epoch = reidentify(dict(segment, source_epoch="G0002"))
bad_epoch_oid = blob(repo, rotation.canonical_json_v1(bad_epoch))
git(repo, "update-ref", segment_ref, bad_epoch_oid, segment_oid)
error(lambda: rotation.verify_manifest_segments_core_v1(repo, segment_manifest),
      "manifest row and segment semantics disagree")
git(repo, "update-ref", segment_ref, segment_oid, bad_epoch_oid)
segment_manifest_oid = blob(repo, rotation.canonical_json_v1(segment_manifest))
segment_pointer, segment_pointer_bytes = rotation.build_generation_pointer_v1(
    controller_id="controller-1", claim_id="a" * 32, run_id="run-1", generation_id="G0001",
    source_epoch="G0001", predecessor_pointer_oid=None, predecessor_pointer_digest=None,
    generation_manifest_oid=segment_manifest_oid, generation_manifest_digest=segment_manifest["manifest_digest"],
    cold_high_water=segment_manifest["high_water"], hot_state_digest="b" * 64,
    hot_roadmap_digest="c" * 64, work_graph_path="WORK_GRAPH.json", work_graph_digest="d" * 64,
    degraded_state="NONE")
segment_pointer_oid = blob(repo, segment_pointer_bytes)

def rehashed_pointer(pointer):
    result = dict(pointer)
    result["pointer_digest"] = hashlib.sha256(rotation.canonical_json_v1(
        {key: value for key, value in result.items() if key != "pointer_digest"})).hexdigest()
    return result

# Every SC10 subcase is executed against the strict tuple boundary, rather than
# being treated as a fixture label.  The actual manifest OID is separately
# supplied so a pointer's self-reported OID cannot make the comparison tautological.
error(lambda: rotation.load_canonical_generation_manifest_oid_v1(repo, segment_pointer_oid),
      "manifest keys are not exact")
noncanonical_pointer_oid = blob(repo, json.dumps(segment_pointer, sort_keys=True).encode())
error(lambda: rotation.load_canonical_generation_pointer_oid_v1(repo, noncanonical_pointer_oid),
      "generation pointer bytes are not canonical")
noncanonical_manifest_oid = blob(repo, json.dumps(segment_manifest, sort_keys=True).encode())
error(lambda: rotation.load_canonical_generation_manifest_oid_v1(repo, noncanonical_manifest_oid),
      "generation manifest bytes are not canonical")
tuple_mutations = {
    "manifest-oid": ("generation_manifest_oid", pointer_oid),
    "manifest-digest": ("generation_manifest_digest", "0" * 64),
    "controller-id": ("controller_id", "controller-2"),
    "claim-id": ("claim_id", "b" * 32),
    "run-id": ("run_id", "run-2"),
    "generation-id": ("generation_id", "G0002"),
    "source-epoch": ("source_epoch", "G0002"),
    "cold-high-water": ("cold_high_water", "00000000000000000002"),
}
for label, (field, value) in tuple_mutations.items():
    changed = rehashed_pointer(dict(segment_pointer, **{field: value}))
    error(lambda changed=changed: rotation.verify_pointer_manifest_tuple_v1(
        pointer=changed, manifest=segment_manifest, manifest_oid=segment_manifest_oid),
        "pointer and manifest tuple disagrees")

# Publisher controls use a genuine temporary source layout.  The copied module
# resolves its own copied claim-run/validator and every counted scenario enters
# publish_generation_pointer_v1 through the unmodified no-input lease/context
# route.  Only low-level native-read and subprocess boundaries are injected.
owner_repo = Path(sys.argv[3]) / "publisher-owner"
subprocess.run(["git", "init", "-q", str(owner_repo)], check=True)
owner_scripts = owner_repo / "skills" / "implementaudit" / "scripts"
owner_scripts.mkdir(parents=True)
source_scripts = Path(sys.argv[1]).parent
for name in ("rotate-canonical-state.py", "claim-run.sh", "validate-run-root.sh"):
    shutil.copy2(source_scripts / name, owner_scripts / name)
run_name = "task4-AbC123"
run_root = owner_repo / ".IMPLEMENTAUDIT" / "runs" / run_name
run_root.mkdir(parents=True)
mutable_content = {
    "STATE.md": b"Current epoch: G0001\n",
    "ROADMAP.md": b"Task 4 publisher fixture\n",
    "WORK_GRAPH.json": b'{"nodes":[]}\n',
}
for name, data in mutable_content.items():
    (run_root / name).write_bytes(data)
for name in ("PROTOCOL.md", "THINKING.md", "sidecars.md", "tools.md", "context.md"):
    (run_root / name).write_text(name + "\n", encoding="utf-8")
owner_repo_text = owner_repo.resolve().as_posix()
owner_common = git(owner_repo, "rev-parse", "--path-format=absolute", "--git-common-dir").decode().strip()
claim_id = "a" * 32
(run_root / ".claimed").write_bytes(("\n".join((
    "schema=implementaudit.run-claim.v2",
    "claim_id=" + claim_id,
    "claimed_at_utc=2026-08-21T00:00:00Z",
    "mode=full",
    "templates=STATE.md PROTOCOL.md ROADMAP.md THINKING.md sidecars.md tools.md context.md",
    "repo_root=" + owner_repo_text,
    "git_common_dir=" + owner_common,
    "run_base=.IMPLEMENTAUDIT/runs",
    "run_root=.IMPLEMENTAUDIT/runs/" + run_name,
    "run_name=" + run_name,
)) + "\n").encode())
git(owner_repo, "config", "user.name", "Task4 Fixture")
git(owner_repo, "config", "user.email", "task4@example.invalid")
git(owner_repo, "add", "skills", ".IMPLEMENTAUDIT")
git(owner_repo, "commit", "-q", "-m", "fixture owner")
owner_head = git(owner_repo, "rev-parse", "HEAD").decode().strip()
owner_tree = git(owner_repo, "rev-parse", "HEAD^{tree}").decode().strip()
controller_id = "controller-1"
controller_ref = "refs/implementaudit/controllers/" + controller_id
controller_raw = ("implementaudit.controller-current.v1\t" + controller_id + "\t"
                  + claim_id + "\t" + run_root.resolve().as_posix() + "\n").encode()
controller_oid = blob(owner_repo, controller_raw)
git(owner_repo, "update-ref", controller_ref, controller_oid)
receipt_ref = "refs/implementaudit/continuity-receipts/controller-1/G0001"
receipt_raw = "\t".join((
    "implementaudit.continuity-receipt.v2", controller_id, controller_oid,
    claim_id, owner_head, owner_tree,
    hashlib.sha256(mutable_content["STATE.md"]).hexdigest(),
    hashlib.sha256(mutable_content["ROADMAP.md"]).hexdigest(),
    "none", "manual-resume", "G0001", "task4-fixture-event",
)).encode() + b"\n"
receipt_oid = blob(owner_repo, receipt_raw)
git(owner_repo, "update-ref", receipt_ref, receipt_oid)
marker_ref = "refs/implementaudit/current-generation-migrations/controller-1"
invalidation_ref = "refs/implementaudit/continuity-invalidations/controller-1"
current_ref = "refs/implementaudit/current-generations/controller-1"

owner_spec = importlib.util.spec_from_file_location(
    "rotation_sequence_cas_owner", owner_scripts / "rotate-canonical-state.py")
owner_rotation = importlib.util.module_from_spec(owner_spec)
owner_spec.loader.exec_module(owner_rotation)
owner_validator_probe = subprocess.run([
    r"C:\Program Files\Git\bin\bash.exe", str(owner_scripts / "validate-run-root.sh"),
    "--claim-only", run_root.resolve().as_posix(), "--repo-root", owner_repo_text,
], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
if owner_validator_probe.returncode != 0:
    raise SystemExit("temporary source-layout owner validator failed: "
                     + owner_validator_probe.stderr.decode("utf-8", "replace"))
owner_custody_probe = subprocess.run([
    r"C:\Program Files\Git\bin\bash.exe", str(owner_scripts / "claim-run.sh"),
    "--publication-custody",
], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
   env=owner_rotation.git_environment(), check=False)
if owner_custody_probe.returncode != 0:
    raise SystemExit("temporary source-layout custody route failed: stdout=%r stderr=%r"
                     % (owner_custody_probe.stdout, owner_custody_probe.stderr))
if (owner_rotation.publication_owner_repo_v1() != owner_repo.resolve()
        or owner_rotation.load_governed_publication_context_v1()["run_root_path"]
        != run_root.resolve()):
    raise SystemExit("temporary source-layout owner did not resolve its physical custody")

def owner_error(action, expected=None):
    try:
        action()
    except owner_rotation.RotationError as exc:
        if expected is not None and str(exc) != expected:
            raise SystemExit("expected %r, got %r" % (expected, exc))
        return exc
    raise SystemExit("expected copied publisher to fail closed")

# Fixed-location/owner/native-observation controls are real where supported and
# otherwise inject only the lowest native wrapper to prove the typed refusal.
fake_pf = Path(sys.argv[3]) / "fake-program-files" / "Git" / "cmd"
fake_pf.mkdir(parents=True)
(fake_pf / "git.exe").write_bytes(b"caller-selected-not-git")
fake_oid = blob(owner_repo, b"fake-selection-probe")
saved_program_files = os.environ.get("ProgramFiles")
os.environ["ProgramFiles"] = str(fake_pf.parents[1])
try:
    fake_probe = owner_rotation.prepare_trusted_update_ref_transaction_v1(
        repo=owner_repo, ref="refs/implementaudit/current-generations/fake-probe",
        new_oid=fake_oid, old_oid=owner_rotation.ZERO_OID, verify_refs=())
finally:
    if saved_program_files is None:
        os.environ.pop("ProgramFiles", None)
    else:
        os.environ["ProgramFiles"] = saved_program_files
selected_executable = Path(fake_probe["argv"][0])
if (not any(os.path.samefile(selected_executable, fixed)
            for fixed in owner_rotation.WINDOWS_TRUSTED_GIT_PATHS_V1)
        or str(fake_pf) in str(selected_executable)):
    raise SystemExit("caller ProgramFiles selected the trusted executable")
wrong_owner = Path(sys.argv[3]) / "wrong-owner-git.exe"
shutil.copy2(owner_rotation.WINDOWS_TRUSTED_GIT_PATHS_V1[0], wrong_owner)
try:
    owner_rotation.freeze_trusted_executable_v1(wrong_owner)
except owner_rotation.RotationError as exc:
    if str(exc) != "trusted Windows file ownership is invalid":
        raise
else:
    original_owner_sid = owner_rotation._windows_owner_sid_v1
    owner_rotation._windows_owner_sid_v1 = lambda _handle: "S-1-5-21-1-2-3-1001"
    try:
        owner_error(lambda: owner_rotation.freeze_trusted_executable_v1(wrong_owner),
                    "trusted Windows file ownership is invalid")
    finally:
        owner_rotation._windows_owner_sid_v1 = original_owner_sid
owner_error(lambda: owner_rotation.freeze_trusted_executable_v1(Path(sys.argv[3])))

expected_digests = {
    "STATE": hashlib.sha256(mutable_content["STATE.md"]).hexdigest(),
    "ROADMAP": hashlib.sha256(mutable_content["ROADMAP.md"]).hexdigest(),
    "WORK_GRAPH": hashlib.sha256(mutable_content["WORK_GRAPH.json"]).hexdigest(),
}
observation_rows = owner_rotation.observe_publication_vector_v1(
    context={"run_root_path": run_root}, expected_digests=expected_digests)
if (owner_rotation.PublicationObservationV1._fields != (
        "semantic_role", "canonical_no_follow_path", "file_identity", "size",
        "ctime_ns", "mtime_ns", "sha256", "expected_digest")
        or [row.semantic_role for row in observation_rows] != ["STATE", "ROADMAP", "WORK_GRAPH"]
        or any(len(row.file_identity) != 2 or row.sha256 != row.expected_digest
               for row in observation_rows)):
    raise SystemExit("native publication observation tuple is not exact")
original_windows_apis = owner_rotation._windows_apis_v1
owner_rotation._windows_apis_v1 = lambda: (_ for _ in ()).throw(
    owner_rotation.RotationError("OE_PUBLICATION_FENCE_UNSUPPORTED"))
try:
    owner_error(lambda: owner_rotation.observe_publication_vector_v1(
        context={"run_root_path": run_root}, expected_digests=expected_digests),
        "OE_PUBLICATION_FENCE_UNSUPPORTED")
finally:
    owner_rotation._windows_apis_v1 = original_windows_apis

owner_segment = reidentify(dict(segment, run_id=run_name))
owner_segment_raw = owner_rotation.canonical_json_v1(owner_segment)
owner_segment_oid = blob(owner_repo, owner_segment_raw)
owner_segment_ref = (owner_rotation.EVENT_SEGMENT_PREFIX
                     + "/" + run_name + "/G0001/00000000000000000001/"
                     + owner_segment["event_id"])
git(owner_repo, "update-ref", owner_segment_ref, owner_segment_oid)
owner_manifest, owner_manifest_raw = owner_rotation.build_generation_manifest_v1(
    None, [owner_segment])
if owner_manifest_raw != owner_rotation.canonical_json_v1(owner_manifest):
    raise SystemExit("copied owner manifest builder did not return canonical product bytes")
owner_manifest_oid = blob(owner_repo, owner_manifest_raw)

def owner_pointer(*, controller="controller-1", degraded="NONE"):
    pointer, raw = owner_rotation.build_generation_pointer_v1(
        controller_id=controller, claim_id=claim_id, run_id=run_name,
        generation_id="G0001", source_epoch="G0001",
        predecessor_pointer_oid=None, predecessor_pointer_digest=None,
        generation_manifest_oid=owner_manifest_oid,
        generation_manifest_digest=owner_manifest["manifest_digest"],
        cold_high_water=owner_manifest["high_water"],
        hot_state_digest=expected_digests["STATE"],
        hot_roadmap_digest=expected_digests["ROADMAP"],
        work_graph_path="WORK_GRAPH.json",
        work_graph_digest=expected_digests["WORK_GRAPH"],
        degraded_state=degraded)
    return pointer, blob(owner_repo, raw)

owner_pointer_value, owner_pointer_oid = owner_pointer()
_, owner_loser_oid = owner_pointer(degraded="ACTIVEGRAPH_DOGFOOD_DEGRADED")
_, owner_wrong_live_oid = owner_pointer(controller="controller-2")
bad_controller_segment = reidentify(dict(owner_segment, controller_id="controller-2"))
bad_controller_oid = blob(owner_repo, owner_rotation.canonical_json_v1(bad_controller_segment))
bad_epoch_segment = reidentify(dict(owner_segment, source_epoch="G0002"))
bad_epoch_oid = blob(owner_repo, owner_rotation.canonical_json_v1(bad_epoch_segment))

def delete_ref(ref_name):
    subprocess.run(["git", "-C", str(owner_repo), "update-ref", "-d", ref_name],
                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)

def reset_owner_case():
    delete_ref(current_ref)
    delete_ref(marker_ref)
    delete_ref(invalidation_ref)
    git(owner_repo, "update-ref", controller_ref, controller_oid)
    git(owner_repo, "update-ref", receipt_ref, receipt_oid)
    git(owner_repo, "update-ref", owner_segment_ref, owner_segment_oid)
    for name, data in mutable_content.items():
        (run_root / name).write_bytes(data)
    lock_path = Path(git(owner_repo, "rev-parse", "--path-format=absolute", "--git-path",
                         "implementaudit-r0039-publication.lock").decode().strip())
    if lock_path.exists():
        lock_path.unlink()

def current_oid():
    result = subprocess.run(["git", "-C", str(owner_repo), "rev-parse", "--verify", current_ref],
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    return result.stdout.decode().strip() if result.returncode == 0 else None

EXPECTED_PUBLISHER_IDS = (
    "wrong-live", "stored-controller", "stored-source-epoch", "winner", "loser",
    "guard-controller", "guard-invalidation", "guard-receipt", "guard-marker",
    "mutation-STATE-in-place", "mutation-STATE-replacement", "mutation-STATE-write-restore",
    "mutation-ROADMAP-in-place", "mutation-ROADMAP-replacement", "mutation-ROADMAP-write-restore",
    "mutation-WORK_GRAPH-in-place", "mutation-WORK_GRAPH-replacement",
    "mutation-WORK_GRAPH-write-restore", "immutable-path", "immutable-object",
    "lease-held", "final-trace", "unknown-effect", "hostile-hooks-env",
)
executed_publisher_ids = []

def record_publisher(case_id):
    if case_id in executed_publisher_ids:
        raise SystemExit("duplicate publisher case execution: " + case_id)
    executed_publisher_ids.append(case_id)

class SubprocessProxy:
    PIPE = subprocess.PIPE
    DEVNULL = subprocess.DEVNULL
    STDOUT = subprocess.STDOUT
    def __init__(self, hook=None, trace=None):
        self.hook = hook
        self.trace = trace
    def run(self, argv, *args, **kwargs):
        values = [str(value) for value in argv]
        if self.trace is not None:
            if "update-ref" in values and "--stdin" in values:
                self.trace.append("update-ref")
            elif "rev-parse" in values and "--verify" in values and current_ref in values:
                self.trace.append("readback")
            else:
                self.trace.append("other")
        if self.hook is not None:
            replacement = self.hook(values, args, kwargs)
            if replacement is not None:
                return replacement
        return subprocess.run(argv, *args, **kwargs)

def with_subprocess_proxy(proxy, action):
    original = owner_rotation.subprocess
    owner_rotation.subprocess = proxy
    try:
        return action()
    finally:
        owner_rotation.subprocess = original

reset_owner_case()
owner_error(lambda: owner_rotation.publish_generation_pointer_v1(
    candidate_pointer_oid=owner_wrong_live_oid),
    "generation pointer authority disagrees with live custody")
if current_oid() is not None:
    raise SystemExit("wrong-live publisher changed current ref")
record_publisher("wrong-live")

for case_id, bad_oid in (("stored-controller", bad_controller_oid),
                         ("stored-source-epoch", bad_epoch_oid)):
    reset_owner_case()
    git(owner_repo, "update-ref", owner_segment_ref, bad_oid, owner_segment_oid)
    owner_error(lambda: owner_rotation.publish_generation_pointer_v1(
        candidate_pointer_oid=owner_pointer_oid),
        "manifest row and segment semantics disagree")
    if current_oid() is not None:
        raise SystemExit(case_id + " publisher changed current ref")
    record_publisher(case_id)

reset_owner_case()
if owner_rotation.publish_generation_pointer_v1(
        candidate_pointer_oid=owner_pointer_oid) != owner_pointer_oid or current_oid() != owner_pointer_oid:
    raise SystemExit("publisher winner did not commit/read back its candidate")
record_publisher("winner")

reset_owner_case()
loser_injected = {"done": False}
def loser_hook(values, _args, _kwargs):
    if not loser_injected["done"] and "update-ref" in values and "--stdin" in values:
        git(owner_repo, "update-ref", current_ref, owner_pointer_oid)
        loser_injected["done"] = True
    return None
try:
    with_subprocess_proxy(SubprocessProxy(loser_hook), lambda:
        owner_rotation.publish_generation_pointer_v1(candidate_pointer_oid=owner_loser_oid))
except owner_rotation.ExpectedOldCasLost as loser_receipt:
    if (loser_receipt.candidate_oid != owner_loser_oid
            or loser_receipt.expected_old != owner_rotation.ZERO_OID
            or loser_receipt.observed_after_loss != owner_pointer_oid
            or loser_receipt.classification != "UNREFERENCED_LOSER_QUARANTINED"):
        raise SystemExit("publisher loser receipt is not exact")
else:
    raise SystemExit("publisher loser unexpectedly succeeded")
if not loser_injected["done"] or current_oid() != owner_pointer_oid:
    raise SystemExit("publisher loser did not preserve the observed winner")
record_publisher("loser")

guard_cases = (
    ("guard-controller", controller_ref, controller_oid),
    ("guard-invalidation", invalidation_ref, owner_rotation.ZERO_OID),
    ("guard-receipt", receipt_ref, receipt_oid),
    ("guard-marker", marker_ref, owner_rotation.ZERO_OID),
)
for case_id, guard_ref_name, guard_before in guard_cases:
    reset_owner_case()
    guard_after = blob(owner_repo, (case_id + "-after").encode())
    injected = {"done": False}
    def guard_hook(values, _args, _kwargs, guard_ref_name=guard_ref_name,
                   guard_before=guard_before, guard_after=guard_after):
        if not injected["done"] and "update-ref" in values and "--stdin" in values:
            if guard_before == owner_rotation.ZERO_OID:
                git(owner_repo, "update-ref", guard_ref_name, guard_after)
            else:
                git(owner_repo, "update-ref", guard_ref_name, guard_after, guard_before)
            injected["done"] = True
        return None
    owner_error(lambda: with_subprocess_proxy(SubprocessProxy(guard_hook), lambda:
        owner_rotation.publish_generation_pointer_v1(candidate_pointer_oid=owner_pointer_oid)))
    if not injected["done"] or current_oid() is not None:
        raise SystemExit(case_id + " escaped the post-equality transaction guard")
    record_publisher(case_id)

for role, filename in (("STATE", "STATE.md"), ("ROADMAP", "ROADMAP.md"),
                       ("WORK_GRAPH", "WORK_GRAPH.json")):
    for mutation in ("in-place", "replacement", "write-restore"):
        case_id = "mutation-%s-%s" % (role, mutation)
        reset_owner_case()
        target = run_root / filename
        original_native_read = (owner_rotation._windows_read_handle_bytes_v1
                                if os.name == "nt"
                                else owner_rotation._read_posix_descriptor_bytes_v1)
        injected = {"done": False}
        def mutating_read(handle, target=target, filename=filename, mutation=mutation):
            data = original_native_read(handle)
            if not injected["done"] and data == mutable_content[filename]:
                if mutation == "in-place":
                    target.write_bytes(data + b"-changed")
                elif mutation == "replacement":
                    replacement = target.with_name(target.name + ".replacement")
                    replacement.write_bytes(data)
                    try:
                        os.replace(replacement, target)
                    except PermissionError as exc:
                        # A retained native Windows handle may prevent the path
                        # replacement outright.  That is the stronger safe
                        # outcome for this adversarial boundary: the attempted
                        # replacement cannot reach the CAS.
                        replacement.unlink(missing_ok=True)
                        injected["done"] = True
                        raise owner_rotation.RotationError(
                            "sandbox replacement blocked by retained handle") from exc
                else:
                    target.write_bytes(data + b"-changed")
                    target.write_bytes(data)
                injected["done"] = True
            return data
        if os.name == "nt":
            owner_rotation._windows_read_handle_bytes_v1 = mutating_read
        else:
            owner_rotation._read_posix_descriptor_bytes_v1 = mutating_read
        try:
            owner_error(lambda: owner_rotation.publish_generation_pointer_v1(
                candidate_pointer_oid=owner_pointer_oid))
        finally:
            if os.name == "nt":
                owner_rotation._windows_read_handle_bytes_v1 = original_native_read
            else:
                owner_rotation._read_posix_descriptor_bytes_v1 = original_native_read
        if not injected["done"] or current_oid() is not None:
            raise SystemExit(case_id + " escaped the publisher fence")
        record_publisher(case_id)

reset_owner_case()
path_injected = {"count": 0, "done": False}
def immutable_path_hook(values, _args, kwargs):
    if "rev-parse" in values and "--verify" in values and owner_segment_ref in values:
        result = subprocess.run(values, **kwargs)
        path_injected["count"] += 1
        if path_injected["count"] == 2:
            git(owner_repo, "update-ref", owner_segment_ref, bad_controller_oid, owner_segment_oid)
            path_injected["done"] = True
        return result
    return None
owner_error(lambda: with_subprocess_proxy(SubprocessProxy(immutable_path_hook), lambda:
    owner_rotation.publish_generation_pointer_v1(candidate_pointer_oid=owner_pointer_oid)))
if not path_injected["done"] or current_oid() is not None:
    raise SystemExit("immutable path mutation escaped publisher verification")
record_publisher("immutable-path")

reset_owner_case()
object_injected = {"count": 0, "done": False}
def immutable_object_hook(values, _args, kwargs):
    if "cat-file" in values and "blob" in values and owner_pointer_oid in values:
        result = subprocess.run(values, **kwargs)
        object_injected["count"] += 1
        if object_injected["count"] == 4:
            object_injected["done"] = True
            return subprocess.CompletedProcess(
                result.args, 0, stdout=result.stdout + b" ", stderr=result.stderr)
        return result
    return None
owner_error(lambda: with_subprocess_proxy(SubprocessProxy(immutable_object_hook), lambda:
    owner_rotation.publish_generation_pointer_v1(candidate_pointer_oid=owner_pointer_oid)))
if not object_injected["done"] or current_oid() is not None:
    raise SystemExit("immutable object corruption escaped publisher verification")
record_publisher("immutable-object")

reset_owner_case()
lease_path = Path(git(owner_repo, "rev-parse", "--path-format=absolute", "--git-path",
                      "implementaudit-r0039-publication.lock").decode().strip())
lease_path.write_bytes(b"held")
owner_error(lambda: owner_rotation.publish_generation_pointer_v1(
    candidate_pointer_oid=owner_pointer_oid), "R0039 publication writer lease is held")
if current_oid() is not None:
    raise SystemExit("lease-held publisher changed current ref")
lease_path.unlink()
record_publisher("lease-held")

reset_owner_case()
operation_trace = []
if with_subprocess_proxy(SubprocessProxy(trace=operation_trace), lambda:
        owner_rotation.publish_generation_pointer_v1(
            candidate_pointer_oid=owner_pointer_oid)) != owner_pointer_oid:
    raise SystemExit("final-trace publisher did not succeed")
final_index = operation_trace.index("update-ref")
if (operation_trace.count("update-ref") != 1
        or operation_trace[final_index:] != ["update-ref", "readback"]
        or current_oid() != owner_pointer_oid):
    raise SystemExit("post-equality trace is not one update-ref then readback")
record_publisher("final-trace")

reset_owner_case()
unknown_trace = []
unknown_state = {"committed": False}
def unknown_hook(values, _args, kwargs):
    if "update-ref" in values and "--stdin" in values:
        result = subprocess.run(values, **kwargs)
        unknown_state["committed"] = result.returncode == 0
        return result
    if (unknown_state["committed"] and "rev-parse" in values
            and "--verify" in values and current_ref in values):
        return subprocess.CompletedProcess(values, 1, stdout=b"", stderr=b"readback outage")
    return None
owner_error(lambda: with_subprocess_proxy(SubprocessProxy(unknown_hook, unknown_trace), lambda:
    owner_rotation.publish_generation_pointer_v1(candidate_pointer_oid=owner_pointer_oid)),
    "publication readback has unknown effect")
if (unknown_trace.count("update-ref") != 1 or current_oid() != owner_pointer_oid):
    raise SystemExit("unknown-effect publisher retried or lost its first effect")
record_publisher("unknown-effect")

reset_owner_case()
owner_git_dir = Path(git(owner_repo, "rev-parse", "--git-dir").decode().strip())
if not owner_git_dir.is_absolute():
    owner_git_dir = owner_repo / owner_git_dir
sentinel = Path(sys.argv[3]) / "hostile-owner-hook-ran"
hook = owner_git_dir / "hooks" / "reference-transaction"
hook.parent.mkdir(exist_ok=True)
hook.write_text("#!/usr/bin/env sh\nprintf hook > '" + sentinel.as_posix().replace("'", "") + "'\n",
                encoding="utf-8")
hook.chmod(0o700)
hostile_environment = {
    "ProgramFiles": str(fake_pf.parents[1]), "GIT_DIR": "hostile",
    "GIT_CONFIG_GLOBAL": "hostile", "BASH_ENV": "hostile", "ENV": "hostile",
    "BASH_FUNC_git%%": "() { printf hostile; }", "LD_PRELOAD": "hostile",
    "DYLD_INSERT_LIBRARIES": "hostile", "PATH": str(fake_pf),
}
saved_hostile = {key: os.environ.get(key) for key in hostile_environment}
os.environ.update(hostile_environment)
try:
    hostile_result = owner_rotation.publish_generation_pointer_v1(
        candidate_pointer_oid=owner_pointer_oid)
finally:
    for key, value in saved_hostile.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value
if hostile_result != owner_pointer_oid or current_oid() != owner_pointer_oid or sentinel.exists():
    raise SystemExit("hostile hook/environment affected the copied publisher")
record_publisher("hostile-hooks-env")

if (tuple(executed_publisher_ids) != EXPECTED_PUBLISHER_IDS
        or len(executed_publisher_ids) != len(set(executed_publisher_ids))):
    raise SystemExit("publisher execution population disagrees: expected=%r actual=%r"
                     % (EXPECTED_PUBLISHER_IDS, executed_publisher_ids))
print("CANONICAL_STATE_ROTATION_SEQUENCE_CAS_GREEN=SC01-SC10 fixture=10/10 "
      "publisher-cas=PASS executed=%d/%d ids=%s" % (
          len(executed_publisher_ids), len(EXPECTED_PUBLISHER_IDS),
          ",".join(executed_publisher_ids)))
PY
  exit 0
fi
if $event_bytes_only; then
  [ -f "$event_byte_fixture" ] || fail "missing event-byte fixture"
  [ -f "$event_schema_fixture" ] || fail "missing event-schema fixture"
  [ -f "$evidence_helper" ] || fail "missing operational evidence carrier"
  python - "$helper" "$evidence_helper" "$event_byte_fixture" "$event_schema_fixture" <<'PY'
import importlib.util
import json
import sys
import copy


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


rotation = load("rotation_event_bytes", sys.argv[1])
evidence = load("evidence_event_bytes", sys.argv[2])
with open(sys.argv[3], encoding="utf-8") as stream:
    byte_cases = json.load(stream)
with open(sys.argv[4], encoding="utf-8") as stream:
    schema_cases = json.load(stream)
if byte_cases.get("schema") != "implementaudit.canonical-state-rotation-event-byte-cases.v1":
    raise SystemExit("event-byte fixture schema drift")
if schema_cases.get("schema") != "implementaudit.history-event-schema-cases.v1":
    raise SystemExit("event-schema fixture schema drift")
root = "sha256:" + "a" * 64
win_entry = {"kind": "repo-relative", "root_identity": root,
             "host_identity": None, "input_path_flavor": "windows"}
posix_entry = {"kind": "repo-relative", "root_identity": root,
               "host_identity": None, "input_path_flavor": "posix"}
win_locator = {"kind": "repo-relative", "root_identity": root,
               "path": "dir\\caf\u00e9.txt", "host_identity": None}
posix_locator = {"kind": "repo-relative", "root_identity": root,
                 "path": "dir/cafe\u0301.txt", "host_identity": None}
posix_trailing_backslash = {"kind": "repo-relative", "root_identity": root,
                            "path": "dir/file\\", "host_identity": None}
expected_enums = {
    name: frozenset(values) for name, values in schema_cases["enums"].items()
}
entry = {
    "source_evidence_id": "iasrc-v1-r0039-archive-entry-1",
    "sha256": "b" * 64,
    "kind": "repo-relative", "root_identity": root, "host_identity": None,
    "input_path_flavor": "posix",
    "source_locator": {"kind": "repo-relative", "root_identity": root,
                       "path": "owner/evidence.json", "host_identity": None},
}
manifest = {"entries": [entry]}
base_event = schema_cases["valid_event"]


def expect_error(action, code):
    try:
        action()
    except rotation.RotationError as exc:
        if str(exc) != code:
            raise SystemExit(f"expected {code}, got {exc}")
    else:
        raise SystemExit(f"expected {code}, action was accepted")


if rotation.EVENT_ENUMS_V1 != expected_enums:
    raise SystemExit("event vocabulary drift")
for rejection in schema_cases["rejections"]:
    event = dict(base_event)
    event.update(rejection["patch"])
    expect_error(lambda event=event: rotation.validate_event_request_v1(event),
                 rejection["code"])


def synthetic_context(source_evidence_id):
    if source_evidence_id != entry["source_evidence_id"]:
        raise SystemExit("builder asked for an unexpected source identity")
    return {
        "run_id": base_event["run_id"],
        "controller_id": base_event["controller_id"],
        "generation_id": base_event["generation_id"],
        "source_epoch": base_event["source_epoch"],
        "owner_manifest": manifest,
    }


def case_eb01():
    payload = {"z": [0, "\u00e9"], "a": {"n": None}}
    if rotation.canonical_json_v1(payload) != evidence.canonical_json_v1(payload):
        raise SystemExit("R0038/R0039 key-order bytes diverged")


def case_eb02():
    if rotation.canonical_json_v1({"value": 1}).endswith(b"\n"):
        raise SystemExit("event bytes retained terminal LF")


def case_eb03():
    if rotation.canonical_json_v1({"value": "\u00e9"}).startswith(b"\xef\xbb\xbf"):
        raise SystemExit("event bytes retained UTF-8 BOM")


def case_eb04():
    raw = "cafe\u0301"
    if raw.encode("utf-8") not in rotation.canonical_json_v1({"value": raw}):
        raise SystemExit("ordinary event string was normalized")


def case_eb05():
    expect_error(lambda: rotation.canonical_json_v1({"bad": 1.5}), "OE_EVENT_PAYLOAD_INVALID")


def case_eb06():
    rotation.canonical_json_v1({"low": -(2**63), "high": 2**63 - 1})


def case_eb07():
    if rotation.normalize_source_locator_v1(win_locator, owner_entry=win_entry) != \
            rotation.normalize_source_locator_v1(posix_locator, owner_entry=posix_entry):
        raise SystemExit("Windows/POSIX typed paths diverged")


def case_eb08():
    upper = dict(posix_locator, path="Dir/file")
    lower = dict(posix_locator, path="dir/file")
    if rotation.normalize_source_locator_v1(upper, owner_entry=posix_entry) == \
            rotation.normalize_source_locator_v1(lower, owner_entry=posix_entry):
        raise SystemExit("case was erased from locator identity")


def case_eb09():
    host = dict(posix_locator, kind="host-bound")
    host_entry = dict(posix_entry, kind="host-bound")
    expect_error(lambda: rotation.normalize_source_locator_v1(host, owner_entry=host_entry),
                 "OE_SOURCE_LOCATOR_INVALID")


def case_eb10():
    literal = dict(posix_locator, path="dir/file\\name")
    if not rotation.normalize_source_locator_v1(literal, owner_entry=posix_entry)["path"].endswith("%5Cname"):
        raise SystemExit("POSIX literal backslash was not data")


def case_eb11():
    expect_error(lambda: rotation.validate_event_request_v1(
        dict(base_event, source_locator={})), "OE_EVENT_REQUEST_KEYS_NOT_EXACT")


def case_eb12():
    if not rotation.normalize_source_locator_v1(
            posix_trailing_backslash, owner_entry=posix_entry)["path"].endswith("%5C"):
        raise SystemExit("POSIX trailing backslash was not data")


def case_eb13():
    bad_entry = dict(entry)
    bad_entry["source_locator"] = dict(entry["source_locator"], root_identity="sha256:" + "c" * 64)
    expect_error(lambda: rotation.resolve_owner_source_evidence_in_context_v1(
        {"owner_manifest": {"entries": [bad_entry]}}, entry["source_evidence_id"]),
        "OE_SOURCE_EVIDENCE_CONTEXT_MISMATCH")


def case_eb14():
    expect_error(lambda: rotation.validate_event_request_v1(dict(base_event, extra=True)),
                 "OE_EVENT_REQUEST_KEYS_NOT_EXACT")


def case_eb15():
    incomplete = dict(base_event)
    del incomplete["payload"]
    expect_error(lambda: rotation.validate_event_request_v1(incomplete),
                 "OE_EVENT_REQUEST_KEYS_NOT_EXACT")


def case_eb16():
    expect_error(lambda: rotation.resolve_owner_source_evidence_in_context_v1(
        {"owner_manifest": {"entries": []}}, entry["source_evidence_id"]),
        "OE_SOURCE_EVIDENCE_NOT_ADMITTED")


def case_eb17():
    expect_error(lambda: rotation.resolve_owner_source_evidence_in_context_v1(
        {"owner_manifest": {"entries": [dict(entry, unexpected=True)]}}, entry["source_evidence_id"]),
        "OE_SOURCE_EVIDENCE_NOT_ADMITTED")
    expect_error(lambda: rotation.resolve_owner_source_evidence_in_context_v1(
        {"owner_manifest": {"entries": [entry], "unexpected": True}}, entry["source_evidence_id"]),
        "OE_SOURCE_EVIDENCE_CONTEXT_MISMATCH")
    malformed_non_target = dict(
        entry, source_evidence_id="iasrc-v1-r0038-snapshot-non-target", sha256="bad")
    expect_error(lambda: rotation.resolve_owner_source_evidence_in_context_v1(
        {"owner_manifest": {"entries": [entry, malformed_non_target]}},
        entry["source_evidence_id"]), "OE_SOURCE_EVIDENCE_NOT_ADMITTED")


def case_eb18():
    original = rotation.load_governed_source_context_v1
    wrong_context = synthetic_context(entry["source_evidence_id"])
    wrong_context["controller_id"] = "controller-2"
    rotation.load_governed_source_context_v1 = lambda source_evidence_id: wrong_context
    try:
        expect_error(lambda: rotation.build_event_segment_v1(
            copy.deepcopy(base_event), source_evidence_id=entry["source_evidence_id"]),
        "OE_SOURCE_EVIDENCE_CONTEXT_MISMATCH")
    finally:
        rotation.load_governed_source_context_v1 = original


def case_eb19():
    expect_error(lambda: rotation.resolve_owner_source_evidence_in_context_v1(
        {"owner_manifest": manifest}, "malformed source id"), "OE_SOURCE_EVIDENCE_NOT_ADMITTED")


def case_eb20():
    original = rotation.load_governed_source_context_v1
    rotation.load_governed_source_context_v1 = synthetic_context
    try:
        built, raw = rotation.build_event_segment_v1(
            copy.deepcopy(base_event), source_evidence_id=entry["source_evidence_id"])
    finally:
        rotation.load_governed_source_context_v1 = original
    rotation.validate_event_output_v1(built)
    if raw != rotation.canonical_json_v1(built) or raw.endswith(b"\n"):
        raise SystemExit("successful event did not retain canonical bytes")


case_tests = {
    "EB01-key-order": case_eb01, "EB02-no-terminal-lf": case_eb02,
    "EB03-utf8-no-bom": case_eb03, "EB04-unicode-preserved": case_eb04,
    "EB05-float-rejected": case_eb05, "EB06-int64-boundary": case_eb06,
    "EB07-windows-posix-path-converges": case_eb07,
    "EB08-case-remains-semantic": case_eb08,
    "EB09-host-bound-requires-host-identity": case_eb09,
    "EB10-posix-literal-backslash-distinct": case_eb10,
    "EB11-caller-source-fields-rejected": case_eb11,
    "EB12-posix-trailing-backslash-is-data": case_eb12,
    "EB13-owner-manifest-context-mismatch": case_eb13,
    "EB14-event-extra-key-rejected": case_eb14,
    "EB15-event-missing-key-rejected": case_eb15,
    "EB16-self-hashed-source-absent-owner-manifest": case_eb16,
    "EB17-wrong-owner-manifest-ref": case_eb17,
    "EB18-wrong-owner-run-controller": case_eb18,
    "EB19-unknown-source-evidence-id": case_eb19,
    "EB20-stored-source-evidence-revalidated": case_eb20,
}
fixture_ids = [case.get("id") for case in byte_cases["cases"]]
if (len(fixture_ids) != len(set(fixture_ids))
        or set(fixture_ids) != set(case_tests)
        or any(case.get("expect") not in {"ACCEPT", "REJECT"}
               for case in byte_cases["cases"])):
    raise SystemExit("event-byte fixture rows are not exact and uniquely mapped")
executed_case_rows = 0
for case in byte_cases["cases"]:
    try:
        case_tests[case["id"]]()
    except KeyError as exc:
        raise SystemExit(f"fixture case is not executed: {case['id']}") from exc
    executed_case_rows += 1
malformed_output = dict(base_event, source_evidence_id=entry["source_evidence_id"],
                        source_locator=[], source_digest="sha256:" + "b" * 64,
                        payload_digest="b" * 64, event_id="iaevt-v1-" + "b" * 64)
expect_error(lambda: rotation.validate_event_output_v1(malformed_output),
             "OE_SOURCE_LOCATOR_INVALID")
for malformed_locator in (
        dict(entry["source_locator"], kind=[]),
        dict(entry["source_locator"], path="\ud800")):
    malformed_output = dict(
        base_event, source_evidence_id=entry["source_evidence_id"],
        source_locator=malformed_locator, source_digest="sha256:" + "b" * 64,
        payload_digest="b" * 64, event_id="iaevt-v1-" + "b" * 64)
    expect_error(lambda malformed_output=malformed_output: rotation.validate_event_output_v1(
        malformed_output), "OE_SOURCE_LOCATOR_INVALID")
    malformed_non_target = dict(
        entry, source_evidence_id="iasrc-v1-r0038-snapshot-malformed-locator",
        source_locator=malformed_locator)
    expect_error(lambda malformed_non_target=malformed_non_target:
        rotation.resolve_owner_source_evidence_in_context_v1(
            {"owner_manifest": {"entries": [entry, malformed_non_target]}},
            entry["source_evidence_id"]), "OE_SOURCE_EVIDENCE_NOT_ADMITTED")
valid_ids = (
    "iasrc-v1-r0039-archive-entry-1",
    "iasrc-v1-r0038-snapshot-entry-1",
)
def no_live_call(*args, **kwargs):
    raise SystemExit("public source facade attempted repository custody")

rotation.git = no_live_call
for source_evidence_id in valid_ids:
    for public_call in (
            lambda: rotation.load_governed_source_context_v1(source_evidence_id),
            lambda: rotation.resolve_owner_source_evidence_v1(source_evidence_id),
            lambda: rotation.build_event_segment_v1(
                schema_cases["valid_event"], source_evidence_id=source_evidence_id)):
        try:
            public_call()
        except rotation.RotationError as exc:
            if str(exc) != "OE_SOURCE_CONTEXT_NOT_AVAILABLE":
                raise SystemExit(f"public source facade returned {exc}")
        else:
            raise SystemExit("public source facade escaped its unavailable boundary")
print("CANONICAL_STATE_ROTATION_EVENT_BYTES_GREEN=PASS cases=" +
      str(executed_case_rows))
PY
  exit 0
fi
fixture_output="$(bash "$checker" --fixture-self-check)"
printf '%s\n' "$fixture_output"
grep -Fq 'denominator=110 omission=110 mutation=110 owner-mutation=110 root-semantic-red=56' <<<"$fixture_output" \
  || fail 'protected denominator is not the exact reviewed four-part population'
grep -Fq 'partitions={"ARCHIVED_ONLY_HISTORY":14,"DERIVED_BINDINGS":29,"MONOTONIC_TRANSITION":18,"PRESERVED_PAYLOAD":49}' <<<"$fixture_output" \
  || fail 'protected denominator is not exactly four-part'
if grep -Fq 'TRIGGER_CALIBRATION' <<<"$fixture_output"; then
  fail 'trigger/calibration leaked into the protected-state partitions'
fi
trigger_output="$(bash "$checker" --trigger-self-check)"
printf '%s\n' "$trigger_output"
grep -Fq 'CANONICAL_STATE_ROTATION_TRIGGER_SELF_CHECK=PASS' <<<"$trigger_output" \
  || fail 'trigger/calibration self-check did not pass'
grep -Fq 'large-root=TRIGGER below-threshold=NO_TRIGGER archive=0 model=0 extra-ceremony=0' <<<"$trigger_output" \
  || fail 'trigger self-check did not preserve the positive and cheap-path outcomes'
grep -Fq 'population-sha256=b3df1ff07d18f8f5de145cf6d10f48a15f0a0416b392d0ca84567dce6d23e497 digest-mutations=55/55' <<<"$trigger_output" \
  || fail 'trigger self-check did not prove canonical population digest mutation coverage'
bash "$checker" --assert-root-red

before_shared_refs="$(git -C "$repo_root" for-each-ref --format='%(refname) %(objectname)' \
  refs/implementaudit/current-generations/ \
  refs/implementaudit/current-generation-migrations/ \
  refs/implementaudit/continuity-invalidations/ \
  refs/implementaudit/continuity-receipts/ \
  refs/implementaudit/state-archives/)"

[ -f "$f2_fixture" ] || fail "missing F2 fixture: $f2_fixture"
if [ ! -f "$helper" ]; then
  printf '%s\n' \
    'CANONICAL_STATE_ROTATION_F2_RED=DRAFT_ARCHIVE_OWNER_ABSENT' >&2
  exit 1
fi
bash "$checker" --f2-fixture-self-check

make_clean_root() {
  local root="$1"
  local run="$root/.IMPLEMENTAUDIT/runs/run-f2"
  mkdir -p "$run"
  git -C "$root" init -q
  printf 'controller: v0333-release\nphase: R39-F2\nnext: implement draft and archive\n' >"$run/STATE.md"
  printf 'audit: R0039\nfrontier: R39-F2\nnext: implement draft and archive\n' >"$run/ROADMAP.md"
  printf '{"active":["R39-F2"],"blocked":["R39-F3"]}\n' >"$run/WORK_GRAPH.json"
  cp "$f2_fixture" "$run/archive-population.json"
  git -C "$root" add .
  GIT_AUTHOR_DATE='2000-01-01T00:00:00Z' \
    GIT_COMMITTER_DATE='2000-01-01T00:00:00Z' \
    git -C "$root" -c user.name=fixture -c user.email=fixture@example.invalid \
      -c commit.gpgsign=false commit -qm preimage
  [ -z "$(git -C "$root" status --porcelain)" ] \
    || fail "two-clean-root control did not start clean: $root"
}

root_a="$tmp/root-a"
root_b="$tmp/root-b"
mkdir -p "$root_a" "$root_b"
make_clean_root "$root_a"
make_clean_root "$root_b"
run_a="$root_a/.IMPLEMENTAUDIT/runs/run-f2"
run_b="$root_b/.IMPLEMENTAUDIT/runs/run-f2"

draft_a="$(python "$helper" draft \
  --repo-root "$root_a" --run-root "$run_a" \
  --controller v0333-release --generation g0008 \
  --manifest "$run_a/archive-population.json")"
draft_b="$(python "$helper" draft \
  --repo-root "$root_b" --run-root "$run_b" \
  --controller v0333-release --generation g0008 \
  --manifest "$run_b/archive-population.json")"

draft_dir_a="$run_a/state-generations/g0008/draft"
draft_dir_b="$run_b/state-generations/g0008/draft"
diff -ru "$draft_dir_a" "$draft_dir_b" >/dev/null \
  || fail 'two clean roots produced different projection-draft bytes'

archive_a="$(python "$helper" archive \
  --repo-root "$root_a" --run-root "$run_a" \
  --controller v0333-release --generation g0008 \
  --draft-dir "$draft_dir_a")"
archive_b="$(python "$helper" archive \
  --repo-root "$root_b" --run-root "$run_b" \
  --controller v0333-release --generation g0008 \
  --draft-dir "$draft_dir_b")"

archive_ref='refs/implementaudit/state-archives/v0333-release/g0008'
archive_oid_a="$(git -C "$root_a" rev-parse --verify "$archive_ref")"
archive_oid_b="$(git -C "$root_b" rev-parse --verify "$archive_ref")"
[ "$archive_oid_a" = "$archive_oid_b" ] \
  || fail 'two clean roots produced different archive-manifest OIDs'
[ "$(git -C "$root_a" cat-file -t "$archive_oid_a")" = blob ] \
  || fail 'archive ref does not resolve to a typed blob'
[ "$(git -C "$root_a" cat-file blob "$archive_oid_a")" = \
   "$(git -C "$root_b" cat-file blob "$archive_oid_b")" ] \
  || fail 'two clean roots produced different archive-manifest bytes'

verify_a="$(python "$helper" verify-archive \
  --repo-root "$root_a" --controller v0333-release --generation g0008)"
verify_b="$(python "$helper" verify-archive \
  --repo-root "$root_b" --controller v0333-release --generation g0008)"

foreign="$tmp/foreign"
mkdir -p "$foreign"
git -C "$foreign" init -q
if ! verify_sanitized="$(GIT_DIR="$foreign/.git" GIT_WORK_TREE="$foreign" \
    python "$helper" verify-archive \
      --repo-root "$root_a" --controller v0333-release --generation g0008)"; then
  fail 'ambient Git repository variables overrode the explicit repository root'
fi
[ "$verify_sanitized" = "$verify_a" ] \
  || fail 'ambient Git repository variables changed typed archive retrieval'

if python "$helper" archive \
    --repo-root "$root_a" --run-root "$run_a" \
    --controller v0333-release --generation g0008 \
    --draft-dir "$draft_dir_a" >"$tmp/reanchor.out" 2>&1; then
  fail 'archive ref accepted a non-zero predecessor'
fi
grep -Fq 'archive ref already exists; expected-zero CAS refused' "$tmp/reanchor.out" \
  || fail 'archive ref collision did not fail with the expected-zero diagnostic'

for root in "$root_a" "$root_b"; do
  [ -z "$(git -C "$root" for-each-ref --format='%(refname)' \
      refs/implementaudit/current-generations/ \
      refs/implementaudit/current-generation-migrations/ \
      refs/implementaudit/continuity-invalidations/ \
      refs/implementaudit/continuity-receipts/)" ] \
    || fail 'F2 wrote a current-generation, marker, invalidation, or receipt ref'
done

python - "$draft_a" "$draft_b" "$archive_a" "$archive_b" \
  "$verify_a" "$verify_b" <<'PY' || fail 'F2 receipts are malformed or nondeterministic'
import json,sys
draft_a,draft_b,archive_a,archive_b,verify_a,verify_b = map(json.loads,sys.argv[1:])
if draft_a != draft_b:
    raise SystemExit("draft receipts differ")
if archive_a != archive_b:
    raise SystemExit("archive receipts differ")
if verify_a != verify_b or verify_a != archive_a:
    raise SystemExit("archive readback receipt differs")
if draft_a.get("schema") != "implementaudit.canonical-state-projection-draft-receipt.v1":
    raise SystemExit("draft receipt schema")
if archive_a.get("schema") != "implementaudit.canonical-state-archive-receipt.v1":
    raise SystemExit("archive receipt schema")
PY

python - "$root_a" "$draft_dir_a" "$archive_oid_a" <<'PY' \
  || fail 'archive typed retrieval, discovery exclusion, or permission readback failed'
import hashlib,json,os,stat,subprocess,sys
from pathlib import Path
root,draft_dir,manifest_oid=Path(sys.argv[1]),Path(sys.argv[2]),sys.argv[3]
draft=json.loads((draft_dir/'draft-manifest.json').read_text(encoding='utf-8'))
for forbidden in ('current_generation','epoch','invalidation_oid','migration_marker','pointer_oid','predecessor_receipt','receipt_oid'):
    if forbidden in draft:
        raise SystemExit(f"transition envelope leaked: {forbidden}")
archive=json.loads(subprocess.check_output(['git','-C',str(root),'cat-file','blob',manifest_oid],text=True))
if archive['entries'] != draft['entries']:
    raise SystemExit('archive and draft entries differ')
for entry in archive['entries']:
    if any(part in {'state-generations','state-archives','quarantine'} for part in Path(entry['source_path']).parts):
        raise SystemExit('recursive population leak')
    data=subprocess.check_output(['git','-C',str(root),'cat-file','blob',entry['blob_oid']])
    if hashlib.sha256(data).hexdigest()!=entry['sha256'] or len(data)!=entry['byte_length']:
        raise SystemExit('typed object identity mismatch')
    if subprocess.check_output(['git','-C',str(root),'cat-file','-t',entry['blob_oid']],text=True).strip()!='blob':
        raise SystemExit('archive entry is not a blob')
    draft_path=draft_dir/entry['draft_path']
    if f"{stat.S_IMODE(os.lstat(draft_path).st_mode):04o}" != entry['mode']:
        raise SystemExit('draft permission readback mismatch')
PY

negative="$tmp/negative"
mkdir -p "$negative"
make_clean_root "$negative"
negative_run="$negative/.IMPLEMENTAUDIT/runs/run-f2"
python - "$negative_run/archive-population.json" <<'PY'
import json,sys
from pathlib import Path
path=Path(sys.argv[1]); data=json.loads(path.read_text(encoding='utf-8'))
data['protected_files'][0]['path']='../STATE.md'
path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
PY
if python "$helper" draft --repo-root "$negative" --run-root "$negative_run" \
    --controller v0333-release --generation g0008 \
    --manifest "$negative_run/archive-population.json" >"$tmp/traversal.out" 2>&1; then
  fail 'path traversal reached the draft writer'
fi
grep -Fq 'unsafe protected path: ../STATE.md' "$tmp/traversal.out" \
  || fail 'path traversal did not fail with the bounded diagnostic'

mkdir -p "$negative_run/STATE-GENERATIONS"
printf 'recursive preimage\n' >"$negative_run/STATE-GENERATIONS/STATE.md"
python - "$negative_run/archive-population.json" "$f2_fixture" <<'PY'
import json,sys
from pathlib import Path
path,fixture=map(Path,sys.argv[1:])
data=json.loads(fixture.read_text(encoding='utf-8'))
data['protected_files'][0]['path']='STATE-GENERATIONS/STATE.md'
path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
PY
if python "$helper" draft --repo-root "$negative" --run-root "$negative_run" \
    --controller v0333-release --generation g0008 \
    --manifest "$negative_run/archive-population.json" >"$tmp/recursive-case.out" 2>&1; then
  fail 'case-aliased recursive population reached the draft writer'
fi
grep -Fq 'unsafe protected path: STATE-GENERATIONS/STATE.md' "$tmp/recursive-case.out" \
  || fail 'case-aliased recursive population lacked the bounded diagnostic'

tampered="$tmp/tampered-draft"
mkdir -p "$tampered"
make_clean_root "$tampered"
tampered_run="$tampered/.IMPLEMENTAUDIT/runs/run-f2"
python "$helper" draft --repo-root "$tampered" --run-root "$tampered_run" \
  --controller v0333-release --generation g0008 \
  --manifest "$tampered_run/archive-population.json" >/dev/null
tampered_draft="$tampered_run/state-generations/g0008/draft"
python - "$tampered_draft/draft-manifest.json" <<'PY'
import json,sys
from pathlib import Path
path=Path(sys.argv[1]); data=json.loads(path.read_text(encoding='utf-8'))
data['entries'][0]['source_path']='state-archives/recursive/STATE.md'
path.write_bytes((json.dumps(data,sort_keys=True,separators=(',',':'))+'\n').encode('utf-8'))
PY
if python "$helper" archive --repo-root "$tampered" --run-root "$tampered_run" \
    --controller v0333-release --generation g0008 \
    --draft-dir "$tampered_draft" >"$tmp/tampered-draft.out" 2>&1; then
  fail 'recursive source-path mutation reached the archive writer'
fi
grep -Fq 'unsafe protected path: state-archives/recursive/STATE.md' "$tmp/tampered-draft.out" \
  || fail 'recursive source-path mutation lacked the bounded diagnostic'

cp "$f2_fixture" "$negative_run/archive-population.json"
python - "$negative_run/STATE.md" <<'PY'
import os,stat,sys
os.chmod(sys.argv[1],stat.S_IREAD)
PY
if python "$helper" draft --repo-root "$negative" --run-root "$negative_run" \
    --controller v0333-release --generation g0008 \
    --manifest "$negative_run/archive-population.json" >"$tmp/permission.out" 2>&1; then
  fail 'read-only protected input reached the draft writer'
fi
grep -Fq 'unsafe permissions for protected file: STATE.md' "$tmp/permission.out" \
  || fail 'permission mutation did not fail with the bounded diagnostic'

cp "$f2_fixture" "$negative_run/archive-population.json"
reparse_kind="$(python - "$negative_run" <<'PY'
import os,subprocess,sys
from pathlib import Path
root=Path(sys.argv[1]); outside=root.parent.parent.parent/'reparse-outside'; alias=root/'alias'
outside.mkdir(); (outside/'STATE.md').write_text('outside\n',encoding='utf-8')
try:
    os.symlink(outside,alias,target_is_directory=True)
    print('symlink')
except OSError:
    result=subprocess.run(
        ['cmd.exe','/d','/c','mklink','/J',str(alias),str(outside)],
        stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=False,
    )
    if result.returncode:
        raise SystemExit('could not create a symlink or reparse-point control')
    print('reparse-junction')
PY
)"
python - "$negative_run/archive-population.json" <<'PY'
import json,sys
from pathlib import Path
path=Path(sys.argv[1]); data=json.loads(path.read_text(encoding='utf-8'))
data['protected_files'][0]['path']='alias/STATE.md'
path.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
PY
set +e
python "$helper" draft --repo-root "$negative" --run-root "$negative_run" \
  --controller v0333-release --generation g0008 \
  --manifest "$negative_run/archive-population.json" >"$tmp/reparse.out" 2>&1
reparse_rc=$?
set -e
python - "$negative_run/alias" <<'PY'
import os,sys
from pathlib import Path
path=Path(sys.argv[1])
if path.is_symlink():
    path.unlink()
elif path.exists():
    os.rmdir(path)
PY
[ "$reparse_rc" -ne 0 ] || fail "$reparse_kind path reached the draft writer"
grep -Fq 'directory custody contains a symlink or reparse point' "$tmp/reparse.out" \
  || fail "$reparse_kind path did not fail with the bounded diagnostic"

python - "$helper" <<'PY' \
  || fail 'Windows reparse-point detector did not reject the held-out attribute'
import importlib.util,sys
from types import SimpleNamespace
spec=importlib.util.spec_from_file_location('rotation_helper',sys.argv[1])
module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
if not module.is_reparse(SimpleNamespace(st_file_attributes=0x400)):
    raise SystemExit('reparse bit accepted')
PY

printf '%s\n' \
  'CANONICAL_STATE_ROTATION_F2_GREEN=PASS draft=BYTE_IDENTICAL archive=BYTE_IDENTICAL typed-retrieval=PASS archive-ref=EXPECTED_ZERO_CAS discovery=EXCLUDED recursive-population=EXCLUDED path=REJECTED symlink-reparse=REJECTED permissions=EXACT_READBACK'

after_shared_refs="$(git -C "$repo_root" for-each-ref --format='%(refname) %(objectname)' \
  refs/implementaudit/current-generations/ \
  refs/implementaudit/current-generation-migrations/ \
  refs/implementaudit/continuity-invalidations/ \
  refs/implementaudit/continuity-receipts/ \
  refs/implementaudit/state-archives/)"
[ "$before_shared_refs" = "$after_shared_refs" ] \
  || fail 'F2 test mutated a shared protected Git-ref namespace'

if $f2_only; then
  exit 0
fi

[ -f "$f3_fixture" ] || fail "missing F3 fixture: $f3_fixture"
[ -f "$claim_helper" ] || fail "missing claim reader owner: $claim_helper"
bash "$checker" --f3-fixture-self-check

matrix_repo="$tmp/matrix-repo"
mkdir -p "$matrix_repo"
git -C "$matrix_repo" init -q
git -C "$matrix_repo" config user.name 'reader matrix fixture'
git -C "$matrix_repo" config user.email 'reader-matrix@example.invalid'
printf 'reader matrix\n' >"$matrix_repo/product.txt"
git -C "$matrix_repo" add product.txt
GIT_AUTHOR_DATE='2000-01-01T00:00:00Z' \
  GIT_COMMITTER_DATE='2000-01-01T00:00:00Z' \
  git -C "$matrix_repo" -c commit.gpgsign=false commit -qm preimage
matrix_rel="$(cd "$matrix_repo" && IMPLEMENTAUDIT_BASE=.IMPLEMENTAUDIT/runs \
  bash "$claim_helper" --controller reader-controller 'reader migration matrix')" \
  || fail 'F3 matrix controller claim failed'
matrix_root="$matrix_repo/$matrix_rel"
matrix_claim="$(sed -n 's/^claim_id=//p' "$matrix_root/.claimed")"
for file in STATE.md PROTOCOL.md ROADMAP.md THINKING.md sidecars.md tools.md context.md; do
  cp "$repo_root/skills/implementaudit/templates/$file" "$matrix_root/$file"
done
matrix_head="$(git -C "$matrix_repo" rev-parse HEAD)"
matrix_tree="$(git -C "$matrix_repo" rev-parse 'HEAD^{tree}')"
python - "$matrix_root/STATE.md" "$matrix_rel" "$matrix_head" "$matrix_tree" <<'PY'
import sys
from pathlib import Path
path=Path(sys.argv[1]); run,head,tree=sys.argv[2:]
text=path.read_text(encoding='utf-8')
text=text.replace('| Run root |  |',f'| Run root | `{run}` |')
text=text.replace('| Next action |  |','| Next action | exercise the complete reader migration matrix |')
anchor='| Epoch | Boundary provenance | Established at | Repo identity | Reconciled | Notes |\n|---|---|---|---|---|---|'
row=f'| G0001 | new-session | 2000-01-01T00:00:00Z | repo at `{head}` / `{tree}` | yes | exact legacy reader fixture |'
path.write_text(text.replace(anchor,anchor+'\n'+row),encoding='utf-8')
PY
legacy_token="$(cd "$matrix_repo" && bash "$claim_helper" --resume-controller \
  reader-controller --boundary new-session --epoch G0001)" \
  || fail 'F3 matrix could not mint its isolated exact-v2 control'
legacy_token_base="$legacy_token"
legacy_ref="${legacy_token%@*}"
legacy_oid="${legacy_token##*@}"
controller_oid="$(git -C "$matrix_repo" rev-parse refs/implementaudit/controllers/reader-controller)"
legacy_v1_oid="$(printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
  implementaudit.continuity-receipt.v1 reader-controller "$controller_oid" "$matrix_claim" \
  "$matrix_head" "$matrix_tree" \
  "$(sha256sum "$matrix_root/STATE.md" | cut -d' ' -f1)" \
  "$(sha256sum "$matrix_root/ROADMAP.md" | cut -d' ' -f1)" \
  | git -C "$matrix_repo" hash-object -w --stdin)"
run_identity="$matrix_rel"
pointer_ref='refs/implementaudit/current-generations/reader-controller'
marker_ref='refs/implementaudit/current-generation-migrations/reader-controller'
v3_ref='refs/implementaudit/continuity-receipts/reader-controller/G0002'
invalidation_ref='refs/implementaudit/continuity-invalidations/reader-controller'
state_pristine="$tmp/matrix-state-pristine.md"
cp "$matrix_root/STATE.md" "$state_pristine"
invalidation_oid='1111111111111111111111111111111111111111'
state_sha='2222222222222222222222222222222222222222222222222222222222222222'
roadmap_sha='3333333333333333333333333333333333333333333333333333333333333333'
protected_sha='4444444444444444444444444444444444444444444444444444444444444444'
archive_sha='5555555555555555555555555555555555555555555555555555555555555555'
next_action='exercise the complete reader migration matrix'

# A current pointer must be tied to the actual run, rather than merely to a
# self-consistent synthetic tuple. Legacy cases deliberately retain no live
# invalidation and their original G0001 STATE.md.
prepare_live_tuple() {
  local generation="$1"
  cp "$state_pristine" "$matrix_root/STATE.md"
  git -C "$matrix_repo" update-ref -d "$invalidation_ref" >/dev/null 2>&1 || true
  invalidation_oid='1111111111111111111111111111111111111111'
  legacy_token="$legacy_token_base"
  next_action='exercise the complete reader migration matrix'
  if [ "$generation" = yes ]; then
    python - "$matrix_root/STATE.md" "$matrix_head" "$matrix_tree" <<'PY'
import sys
from pathlib import Path
p=Path(sys.argv[1]); head,tree=sys.argv[2:]
s=p.read_text(encoding='utf-8')
s=s.replace('Current epoch: G0001', 'Current epoch: G0002')
anchor=f'| G0001 | new-session | 2000-01-01T00:00:00Z | repo at `{head}` / `{tree}` | yes | exact legacy reader fixture |'
row=f'| G0002 | inferred-context-gap | 2000-01-01T00:01:00Z | repo at `{head}` / `{tree}` | yes | current generation reader fixture |'
p.write_text(s.replace(anchor, anchor+'\n'+row), encoding='utf-8')
PY
    invalidation_token="$(cd "$matrix_repo" && bash "$claim_helper" --invalidate-continuity \
      reader-controller --boundary inferred-context-gap --event reader-matrix-g0002)" \
      || fail 'F3 matrix could not mint its isolated live invalidation'
    invalidation_oid="${invalidation_token##*@}"
  fi
  state_sha="$(sha256sum "$matrix_root/STATE.md" | cut -d' ' -f1)"
  roadmap_sha="$(sha256sum "$matrix_root/ROADMAP.md" | cut -d' ' -f1)"
}

make_matrix_objects() {
  local mutation="$1" object_controller=reader-controller object_claim="$matrix_claim"
  local object_run="$run_identity" pointer_schema=implementaudit.current-generation.v1
  local marker_schema=implementaudit.current-generation-migration.v1
  local receipt_schema=implementaudit.continuity-receipt.v3
  case "$mutation" in
    none) ;;
    controller) object_controller=other-controller ;;
    claim) object_claim=other-claim ;;
    run) object_run=.IMPLEMENTAUDIT/runs/other-run ;;
    pointer-schema) pointer_schema=implementaudit.current-generation.v0 ;;
    marker-schema) marker_schema=implementaudit.current-generation-migration.v0 ;;
    receipt-schema) receipt_schema=implementaudit.continuity-receipt.v2 ;;
    live-invalidation) invalidation_oid=9999999999999999999999999999999999999999 ;;
    live-state-hash) state_sha=aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa ;;
    live-roadmap-hash) roadmap_sha=bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb ;;
    live-next-action) next_action='stale reader action' ;;
    predecessor-ref) legacy_token="refs/implementaudit/continuity-receipts/reader-controller/G00FF@$legacy_oid" ;;
    predecessor-oid) legacy_token="$legacy_ref@0000000000000000000000000000000000000000" ;;
    *) fail "unknown F3 owner mutation: $mutation" ;;
  esac
  pointer_oid="$(printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$pointer_schema" "$object_controller" "$object_claim" "$object_run" g0008 G0002 \
    "$invalidation_oid" "$legacy_token" "$v3_ref" implementaudit.canonical-state-projection.v1 \
    "$state_sha" "$roadmap_sha" "$protected_sha" "$archive_sha" "$next_action" \
    | git -C "$matrix_repo" hash-object -w --stdin)"
  v3_oid="$(printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$receipt_schema" "$object_controller" "$object_claim" "$object_run" G0002 \
    "$invalidation_oid" "$pointer_ref" "$pointer_oid" "$state_sha" "$roadmap_sha" \
    "$protected_sha" "$archive_sha" "$next_action" "$legacy_token" \
    | git -C "$matrix_repo" hash-object -w --stdin)"
  marker_oid="$(printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    "$marker_schema" "$object_controller" "$object_claim" "$object_run" G0002 \
    "$pointer_ref" implementaudit.current-generation.v1 "$v3_ref" "$v3_oid" true \
    | git -C "$matrix_repo" hash-object -w --stdin)"
  malformed_oid="$(printf 'malformed\n' | git -C "$matrix_repo" hash-object -w --stdin)"
  stale_v3_oid="$(printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    implementaudit.continuity-receipt.v3 reader-controller "$matrix_claim" "$run_identity" G0002 \
    "$invalidation_oid" "$pointer_ref" 9999999999999999999999999999999999999999 \
    "$state_sha" "$roadmap_sha" "$protected_sha" "$archive_sha" "$next_action" "$legacy_token" \
    | git -C "$matrix_repo" hash-object -w --stdin)"
  mismatch_v3_oid="$(printf '%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n' \
    implementaudit.continuity-receipt.v3 reader-controller other-claim "$run_identity" G0002 \
    "$invalidation_oid" "$pointer_ref" "$pointer_oid" "$state_sha" "$roadmap_sha" \
    "$protected_sha" "$archive_sha" "$next_action" "$legacy_token" \
    | git -C "$matrix_repo" hash-object -w --stdin)"
  invalidated_v2_oid="$(git -C "$matrix_repo" cat-file blob "$legacy_oid" \
    | sed $'s/\tnone\tnew-session\t/\t8888888888888888888888888888888888888888\tnew-session\t/' \
    | git -C "$matrix_repo" hash-object -w --stdin)"
  mismatched_v2_oid="$(git -C "$matrix_repo" cat-file blob "$legacy_oid" \
    | sed $'s/\t'$matrix_claim$'\t/\tother-claim\t/' \
    | git -C "$matrix_repo" hash-object -w --stdin)"
}

matrix_cases="$(python - "$f3_fixture" <<'PY'
import json,sys
for row in json.load(open(sys.argv[1],encoding='utf-8'))['cases']:
    print('\t'.join(str(row[key]) for key in ('id','marker','pointer','receipt','owner_mutation','expected')))
PY
)"
matrix_pass=0
while IFS=$'\t' read -r case_id marker_state pointer_state receipt_state mutation expected; do
  [ -n "$case_id" ] || continue
  expected="${expected%$'\r'}"
  if [ "$pointer_state" = valid ]; then prepare_live_tuple yes; else prepare_live_tuple no; fi
  make_matrix_objects "$mutation"
  git -C "$matrix_repo" update-ref -d "$pointer_ref" >/dev/null 2>&1 || true
  git -C "$matrix_repo" update-ref -d "$marker_ref" >/dev/null 2>&1 || true
  git -C "$matrix_repo" update-ref -d "$legacy_ref" >/dev/null 2>&1 || true
  git -C "$matrix_repo" update-ref -d "$v3_ref" >/dev/null 2>&1 || true
  [ "$pointer_state" != valid ] || git -C "$matrix_repo" update-ref "$legacy_ref" "$legacy_oid"
  case "$pointer_state" in
    absent) ;;
    valid) git -C "$matrix_repo" update-ref "$pointer_ref" "$pointer_oid" ;;
    malformed) git -C "$matrix_repo" update-ref "$pointer_ref" "$malformed_oid" ;;
  esac
  case "$receipt_state" in
    absent) current_token='' ;;
    exact-v1) git -C "$matrix_repo" update-ref "$legacy_ref" "$legacy_v1_oid"; current_token="$legacy_ref@$legacy_v1_oid" ;;
    exact-v2) git -C "$matrix_repo" update-ref "$legacy_ref" "$legacy_oid"; current_token="$legacy_token" ;;
    invalidated-v2) git -C "$matrix_repo" update-ref "$legacy_ref" "$invalidated_v2_oid"; current_token="$legacy_ref@$invalidated_v2_oid" ;;
    mismatched-v2) git -C "$matrix_repo" update-ref "$legacy_ref" "$mismatched_v2_oid"; current_token="$legacy_ref@$mismatched_v2_oid" ;;
    exact-v3) git -C "$matrix_repo" update-ref "$v3_ref" "$v3_oid"; current_token="$v3_ref@$v3_oid" ;;
    stale-v3) git -C "$matrix_repo" update-ref "$v3_ref" "$stale_v3_oid"; current_token="$v3_ref@$stale_v3_oid" ;;
    mismatched-v3) git -C "$matrix_repo" update-ref "$v3_ref" "$mismatch_v3_oid"; current_token="$v3_ref@$mismatch_v3_oid" ;;
  esac
  case "$marker_state" in
    absent) ;;
    valid) git -C "$matrix_repo" update-ref "$marker_ref" "$marker_oid" ;;
    malformed) git -C "$matrix_repo" update-ref "$marker_ref" "$malformed_oid" ;;
  esac
  set +e
  matrix_output="$(cd "$matrix_repo" && bash "$claim_helper" \
    --require-current-continuity reader-controller 2>&1)"
  matrix_rc=$?
  set -e
  matrix_actual=STOP
  if [ "$matrix_rc" -eq 0 ] && [ "$matrix_output" = "$legacy_token" ]; then
    matrix_actual=LEGACY_COMPATIBILITY
  elif [ "$matrix_rc" -eq 0 ] && [ "$matrix_output" = "$current_token" ]; then
    matrix_actual=POINTER_CURRENT
  elif grep -Fq 'FIRST_MIGRATION_INCOMPLETE' <<<"$matrix_output"; then
    matrix_actual=FIRST_MIGRATION_INCOMPLETE
  elif grep -Fq 'STOP_NO_ROOT_FALLBACK' <<<"$matrix_output"; then
    matrix_actual=STOP_NO_ROOT_FALLBACK
  fi
  if [ "$matrix_actual" != "$expected" ]; then
    printf '%s\n' "CANONICAL_STATE_ROTATION_F3_RED=READER_MATRIX_NOT_ENFORCED case=$case_id expected=$expected actual=$matrix_actual" >&2
    exit 1
  fi
  matrix_pass=$((matrix_pass + 1))
done <<<"$matrix_cases"
[ "$matrix_pass" -eq 24 ] || fail "F3 matrix executed $matrix_pass cases instead of 24"

# Held-out live binding negatives. Each begins from a real current G0002
# tuple; a reader that validates only pointer/v3/marker self-consistency would
# incorrectly accept these mutations.
install_held_out_current() {
  prepare_live_tuple yes
  make_matrix_objects none
  git -C "$matrix_repo" update-ref "$legacy_ref" "$legacy_oid"
  git -C "$matrix_repo" update-ref "$pointer_ref" "$pointer_oid"
  git -C "$matrix_repo" update-ref "$v3_ref" "$v3_oid"
  git -C "$matrix_repo" update-ref "$marker_ref" "$marker_oid"
}

assert_held_out_stop() {
  local label="$1" marker_message="${2:-no}"
  local out rc
  set +e
  out="$(cd "$matrix_repo" && bash "$claim_helper" --require-current-continuity reader-controller 2>&1)"
  rc=$?
  set -e
  [ "$rc" -ne 0 ] || fail "held-out $label incorrectly accepted a stale generation tuple"
  if [ "$marker_message" = yes ]; then
    grep -Fq STOP_NO_ROOT_FALLBACK <<<"$out" || fail "held-out $label did not forbid root fallback"
  fi
}

held_out_pass=0
for mutation in live-invalidation live-state-hash live-roadmap-hash live-next-action predecessor-ref predecessor-oid; do
  install_held_out_current
  make_matrix_objects "$mutation"
  git -C "$matrix_repo" update-ref "$pointer_ref" "$pointer_oid"
  git -C "$matrix_repo" update-ref "$v3_ref" "$v3_oid"
  git -C "$matrix_repo" update-ref "$marker_ref" "$marker_oid"
  assert_held_out_stop "$mutation"
  held_out_pass=$((held_out_pass + 1))
done

install_held_out_current
pointer_path="$(git -C "$matrix_repo" rev-parse --path-format=absolute --git-path "$pointer_ref")"
rm -f -- "$pointer_path"
mkdir -p "$(dirname "$pointer_path")"
printf 'not-an-object-id\n' >"$pointer_path"
assert_held_out_stop broken-pointer-ref yes
rm -f -- "$pointer_path"
held_out_pass=$((held_out_pass + 1))

install_held_out_current
marker_path="$(git -C "$matrix_repo" rev-parse --path-format=absolute --git-path "$marker_ref")"
rm -f -- "$marker_path"
mkdir -p "$(dirname "$marker_path")"
printf 'not-an-object-id\n' >"$marker_path"
assert_held_out_stop broken-marker-ref yes
rm -f -- "$marker_path"
held_out_pass=$((held_out_pass + 1))

[ "$held_out_pass" -eq 8 ] || fail "F3 held-out reader negatives executed $held_out_pass cases instead of 8"
printf '%s\n' \
  'CANONICAL_STATE_ROTATION_F3_HELD_OUT_GREEN=PASS cases=8 live=invalidation,state,roadmap,next-action,predecessor-ref,predecessor-oid broken-refs=pointer,marker'

printf '%s\n' \
  'CANONICAL_STATE_ROTATION_F3_GREEN=PASS matrix=24/24 legacy=EXACT_V2_ONLY first-migration=STOP pointer-current=MARKER_POINTER_V3_JOIN marker-fallback=FORBIDDEN owner-schema-mismatch=REJECTED refs=READ_ONLY'

after_f3_shared_refs="$(git -C "$repo_root" for-each-ref --format='%(refname) %(objectname)' \
  refs/implementaudit/current-generations/ \
  refs/implementaudit/current-generation-migrations/ \
  refs/implementaudit/continuity-invalidations/ \
  refs/implementaudit/continuity-receipts/ \
  refs/implementaudit/state-archives/)"
[ "$before_shared_refs" = "$after_f3_shared_refs" ] \
  || fail 'F3 reader matrix mutated a shared protected Git-ref namespace'

if $f3_only; then
  exit 0
fi

set +e
bash "$checker" --assert-f3-residual-red >"$tmp/f3-red.out" 2>&1
f3_red_rc=$?
set -e
[ "$f3_red_rc" -eq 1 ] \
  || fail "F3 residual oracle exited $f3_red_rc instead of semantic RED 1"

grep -Fq 'CANONICAL_STATE_ROTATION_RED=F3_READERS_ONLY_NOT_EQUIVALENT semantic-failures=37 preserved-payload=49/49 missing-equivalence=transition,pointer+marker+v3-publication,rehydration' "$tmp/f3-red.out" \
  || fail 'F3 residual did not preserve the exact later-cell semantic RED'
for anchor in \
  'M01-generation-successor:semantic-mutation' \
  'D05-pointer-ref:semantic-mutation' \
  'D23-rehydrate-identity:semantic-mutation'; do
  grep -Fq "$anchor" "$tmp/f3-red.out" || fail "F3 residual RED omitted anchor $anchor"
done
if grep -Eq '(^|,)(A|D1[5-9]|D2[0-2])[0-9-]' "$tmp/f3-red.out"; then
  fail 'F3 residual still reports a completed archive or reader-matrix slice RED'
fi

cat "$tmp/f3-red.out" >&2
printf '%s\n' \
  'canonical-state-rotation.test: INTENDED_RED later F4-F7 currentness transaction remains absent' >&2
exit 1
