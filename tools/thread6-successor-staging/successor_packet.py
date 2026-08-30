#!/usr/bin/env python3
"""Build and verify a nonauthoritative Thread6.11 successor package.

The tool is deliberately outside the campaign control plane.  It reads only
explicitly named snapshot/evidence files, writes only its requested output
directory, and never reads or mutates continuity, route, HBASE, install, or
release state on its own.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


SNAPSHOT_SCHEMA = "implementaudit.thread6-successor-snapshot.v1"
PACKET_SCHEMA = "implementaudit.thread6-successor-packet.v1"
MANIFEST_SCHEMA = "implementaudit.thread6-successor-package-manifest.v1"

CONTROLLER = "v0333-release"
CLAIM = "10bd7bc5098af00d26b1c319683a64f5"
RUN = "v041-thread5-autodag-TmDJfs"
OBJECTIVE = "COMPLETE_REMAINING_A_TO_F_PRECUTOVER_PATH_AND_PROVE_HEALTHY_THREAD7_TAKEOVER"

PROVISIONAL = "PROVISIONAL_NONAUTHORITATIVE"
FINAL = "FINALIZED_FOR_GOVERNOR_VERIFICATION"
POST_HBASE = "POST_HBASE"
PRE_HBASE = "PRE_HBASE_EXACT_FRONTIER"

PACKET_NAME = "THREAD6_11_SUCCESSOR_PACKET.json"
PROMPT_NAME = "THREAD6_11_LAUNCH_PROMPT.md"
MANIFEST_NAME = "SUCCESSOR_PACKAGE_MANIFEST.json"

REQUIRED_DO_NOT_REPLAY = {
    "CAMPAIGN_PHASE_A",
    "CAMPAIGN_PHASE_B",
    "ACCEPTED_ENGINEERING_PRODUCTS",
    "ACCEPTED_REVIEWS_AND_QUALIFICATION",
    "PRIOR_HBASE_ATTEMPTS_BEYOND_TERMINAL_FACTS",
    "BROAD_STATE_ROADMAP_HISTORY",
    "WORKER_TRANSCRIPTS",
    "REPAIRED_PACKAGE_FAILURES",
}


class ContractError(ValueError):
    pass


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ContractError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_pairs,
        )
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"top-level JSON must be an object: {path}")
    return value


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def pretty_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode(
        "utf-8"
    )


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> tuple[int, str]:
    digest = hashlib.sha256()
    size = 0
    try:
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                size += len(chunk)
                digest.update(chunk)
    except OSError as exc:
        raise ContractError(f"cannot read evidence file {path}: {exc}") from exc
    return size, digest.hexdigest()


def is_unset(value: Any) -> bool:
    return value is None or not isinstance(value, str) or not value or value.upper().startswith(
        "UNSET"
    )


def require_mapping(parent: dict[str, Any], key: str) -> dict[str, Any]:
    value = parent.get(key)
    if not isinstance(value, dict):
        raise ContractError(f"{key} must be an object")
    return value


def require_exact_identity(snapshot: dict[str, Any]) -> None:
    campaign = require_mapping(snapshot, "campaign")
    expected = {
        "controller": CONTROLLER,
        "claim": CLAIM,
        "run": RUN,
        "current_phase": "C",
    }
    if any(campaign.get(key) != value for key, value in expected.items()):
        raise ContractError("campaign identity does not match the existing Thread6.10 campaign/run")

    goal = require_mapping(snapshot, "goal")
    if goal.get("governor") != "/implementaudit":
        raise ContractError("goal governor must remain /implementaudit")
    if goal.get("terminal_objective") != OBJECTIVE:
        raise ContractError("terminal objective is not preserved")
    if goal.get("thread6_10_is_thread7") is not False:
        raise ContractError("Thread6.10 must not be represented as Thread7")
    if goal.get("a_to_g_native_closure_before_thread7") is not True:
        raise ContractError("A-to-G native closure before Thread7 must remain required")


def require_do_not_replay(snapshot: dict[str, Any]) -> None:
    values = snapshot.get("do_not_replay")
    if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
        raise ContractError("do-not-replay inventory must be a string list")
    missing = sorted(REQUIRED_DO_NOT_REPLAY - set(values))
    if missing:
        raise ContractError("do-not-replay inventory missing: " + ", ".join(missing))


def require_full_hex(value: Any, length: int, label: str) -> None:
    if not isinstance(value, str) or len(value) != length:
        raise ContractError(f"{label} must be exactly {length} hexadecimal characters")
    try:
        int(value, 16)
    except ValueError as exc:
        raise ContractError(f"{label} must be exactly {length} hexadecimal characters") from exc


def validate_final_snapshot(snapshot: dict[str, Any]) -> None:
    authority = require_mapping(snapshot, "authority")
    missing_authority = [
        key
        for key in (
            "continuity_receipt",
            "generation_pointer",
            "host_binding",
            "current_route",
            "source_ref",
        )
        if is_unset(authority.get(key))
    ]
    if missing_authority:
        raise ContractError(
            "finalized packet lacks exact authority identities: " + ", ".join(missing_authority)
        )
    require_full_hex(authority["generation_pointer"], 40, "generation_pointer")
    require_full_hex(authority["current_route"], 40, "current_route")

    candidate = require_mapping(snapshot, "candidate")
    if candidate.get("identity_class") != "FROZEN_EXACT_CANDIDATE":
        raise ContractError("finalized packet requires a frozen exact candidate")
    require_full_hex(candidate.get("head"), 40, "candidate head")
    require_full_hex(candidate.get("tree"), 40, "candidate tree")

    frontier = require_mapping(snapshot, "frontier")
    trigger = require_mapping(snapshot, "trigger")
    hbase = require_mapping(snapshot, "hbase")
    canonical = require_mapping(snapshot, "canonical_verify")
    entry_point = snapshot.get("entry_point")

    if entry_point == POST_HBASE:
        if trigger.get("status") != "HBASE_QUALIFIED_EVIDENCED_BY_THREAD6_10" or is_unset(
            trigger.get("evidence_ref")
        ):
            raise ContractError("post-HBASE finalization lacks Thread6.10-qualified trigger evidence")
        if hbase.get("status") != "QUALIFIED" or is_unset(hbase.get("result_ref")):
            raise ContractError("post-HBASE finalization lacks an exact qualified HBASE result")
        if canonical.get("status") != "PASS_TERMINAL" or is_unset(
            canonical.get("terminal_evidence_ref")
        ):
            raise ContractError("post-HBASE finalization lacks canonical terminal package evidence")
        if (
            frontier.get("next_typed_edge")
            != "ORDERED_R30_J0_CONSUMPTION_SELECTIVE_REVALIDATION"
        ):
            raise ContractError("post-HBASE next typed edge is not the ordered R30-J0 edge")
    elif entry_point == PRE_HBASE:
        if trigger.get("status") != "CIRCUIT_BREAKER_EVIDENCED_BY_THREAD6_10" or is_unset(
            trigger.get("evidence_ref")
        ):
            raise ContractError(
                "pre-HBASE finalization requires a circuit breaker evidenced by Thread6.10"
            )
        if is_unset(frontier.get("next_typed_edge")):
            raise ContractError("pre-HBASE finalization lacks the exact next typed edge")
    else:
        raise ContractError("finalized packet entry_point must be POST_HBASE or PRE_HBASE_EXACT_FRONTIER")


def validate_snapshot(snapshot: dict[str, Any]) -> None:
    if snapshot.get("schema") != SNAPSHOT_SCHEMA:
        raise ContractError(f"snapshot schema must be {SNAPSHOT_SCHEMA}")
    mode = snapshot.get("packet_mode")
    if mode not in {PROVISIONAL, FINAL}:
        raise ContractError("packet_mode must be provisional or finalized-for-governor-verification")
    if require_mapping(snapshot, "thread6_9").get("status") != "PAUSED":
        raise ContractError("Thread6.9 must remain PAUSED")
    require_exact_identity(snapshot)
    require_do_not_replay(snapshot)
    if mode == FINAL:
        validate_final_snapshot(snapshot)
    elif snapshot.get("entry_point") != "UNSET":
        raise ContractError("provisional packet entry_point must remain UNSET")


def build_evidence_index(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    evidence = snapshot.get("evidence")
    if not isinstance(evidence, list):
        raise ContractError("evidence must be a list")
    seen: set[str] = set()
    indexed: list[dict[str, Any]] = []
    for item in evidence:
        if not isinstance(item, dict):
            raise ContractError("each evidence entry must be an object")
        evidence_id = item.get("id")
        if not isinstance(evidence_id, str) or not evidence_id:
            raise ContractError("evidence id must be a nonempty string")
        if evidence_id in seen:
            raise ContractError(f"duplicate evidence id: {evidence_id}")
        seen.add(evidence_id)
        role = item.get("role")
        if not isinstance(role, str) or not role:
            raise ContractError(f"evidence role missing for {evidence_id}")
        path_value = item.get("path")
        if not isinstance(path_value, str) or not path_value:
            raise ContractError(f"evidence path missing for {evidence_id}")
        path = Path(path_value)
        if not path.is_absolute():
            raise ContractError(f"evidence path must be absolute for {evidence_id}")
        if not path.is_file():
            raise ContractError(f"evidence file does not exist for {evidence_id}: {path}")
        size, digest = sha256_file(path)
        expected = item.get("expected_sha256")
        if expected is not None and expected.lower() != digest:
            raise ContractError(
                f"evidence digest mismatch for {evidence_id}: expected {expected}, observed {digest}"
            )
        indexed.append(
            {
                "id": evidence_id,
                "role": role,
                "path": str(path.resolve()),
                "bytes": size,
                "sha256": digest,
            }
        )
    return indexed


def packet_content_hash(packet: dict[str, Any]) -> str:
    material = copy.deepcopy(packet)
    material.pop("packet_content_sha256", None)
    return sha256(canonical_bytes(material))


def render_prompt(packet: dict[str, Any]) -> str:
    campaign = packet["campaign"]
    authority = packet["authority"]
    frontier = packet["frontier"]
    do_not_replay = "\n".join(f"- {item}" for item in packet["do_not_replay"])
    return f"""# Thread6.11 startup packet — staged, not self-authorizing

This packet does not create Thread6.11 and confers no campaign authority.
Thread6.10 must first verify and publish a final handoff under its own authority.

PACKET_MODE={packet['packet_mode']}
SUCCESSOR_ENTRY_POINT={packet['entry_point']}
PACKET_CONTENT_SHA256={packet['packet_content_sha256']}

CONTROLLER={campaign['controller']}
CLAIM={campaign['claim']}
RUN={campaign['run']}
CURRENT_PHASE={campaign['current_phase']}
TERMINAL_OBJECTIVE={packet['goal']['terminal_objective']}

On authorized launch, load the exact installed /implementaudit governor first,
then mechanically verify this package, the final Thread6.10 handoff, and all
current authority identities before any substantive reconstruction.

CONTINUITY_RECEIPT={authority['continuity_receipt']}
GENERATION_POINTER={authority['generation_pointer']}
HOST_BINDING={authority['host_binding']}
CURRENT_ROUTE={authority['current_route']}
NEXT_TYPED_EDGE={frontier['next_typed_edge']}

Hydrate only the compact evidence index and exact frontier. Do not hydrate
broad transcripts, replay accepted work, or infer authority from this packet.

## Explicit do-not-replay inventory

{do_not_replay}

THREAD6_9_REMAINS_PAUSED=YES
THREAD6_11_CREATED_BY_THIS_PACKET=NO
HBASE_STATUS={packet['hbase']['status']}
"""


def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp-{os.getpid()}")
    try:
        with temporary.open("wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        temporary.replace(path)
    finally:
        if temporary.exists():
            temporary.unlink()


def build_package(snapshot_path: Path, output_dir: Path) -> dict[str, Any]:
    snapshot = load_json(snapshot_path)
    validate_snapshot(snapshot)
    evidence_index = build_evidence_index(snapshot)

    packet = copy.deepcopy(snapshot)
    packet.pop("evidence", None)
    packet["schema"] = PACKET_SCHEMA
    packet["source_snapshot_schema"] = SNAPSHOT_SCHEMA
    packet["authority_ceiling"] = "NONE"
    packet["campaign_authority"] = False
    packet["thread6_11_created"] = False
    packet["hbase_authority"] = False
    packet["release_authority"] = False
    packet["evidence_index"] = evidence_index
    packet["packet_content_sha256"] = packet_content_hash(packet)

    prompt = render_prompt(packet).encode("utf-8")
    packet_data = pretty_bytes(packet)
    output_dir.mkdir(parents=True, exist_ok=True)
    packet_path = output_dir / PACKET_NAME
    prompt_path = output_dir / PROMPT_NAME
    atomic_write(packet_path, packet_data)
    atomic_write(prompt_path, prompt)

    manifest = {
        "schema": MANIFEST_SCHEMA,
        "packet_mode": packet["packet_mode"],
        "entry_point": packet["entry_point"],
        "authority_ceiling": "NONE",
        "thread6_11_created": False,
        "packet_content_sha256": packet["packet_content_sha256"],
        "files": {
            PACKET_NAME: {"bytes": len(packet_data), "sha256": sha256(packet_data)},
            PROMPT_NAME: {"bytes": len(prompt), "sha256": sha256(prompt)},
        },
    }
    atomic_write(output_dir / MANIFEST_NAME, pretty_bytes(manifest))
    return {
        "build": "PASS",
        "packet_mode": packet["packet_mode"],
        "entry_point": packet["entry_point"],
        "package_dir": str(output_dir.resolve()),
        "packet_content_sha256": packet["packet_content_sha256"],
    }


def verify_manifest_file(package_dir: Path, name: str, expected: dict[str, Any]) -> None:
    path = package_dir / name
    if not path.is_file():
        raise ContractError(f"manifest file missing: {name}")
    size, digest = sha256_file(path)
    if expected.get("bytes") != size or expected.get("sha256") != digest:
        raise ContractError(f"{name} package hash mismatch")


def verify_live_repo(packet: dict[str, Any], repo_root: Path) -> None:
    if not repo_root.is_dir():
        raise ContractError(f"live repository not found: {repo_root}")
    candidate = require_mapping(packet, "candidate")
    packet_repo = Path(str(candidate.get("repository", "")))
    try:
        if packet_repo.resolve() != repo_root.resolve():
            raise ContractError(
                f"live candidate identity mismatch: repository(packet={packet_repo}, live={repo_root})"
            )
    except OSError as exc:
        raise ContractError(f"cannot resolve live repository identity: {exc}") from exc

    def git(*args: str) -> str:
        completed = subprocess.run(
            ["git", "-C", str(repo_root), *args],
            text=True,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            raise ContractError(f"live Git verification failed: {completed.stderr.strip()}")
        return completed.stdout.strip()

    live_head = git("rev-parse", "HEAD")
    live_tree = git("rev-parse", "HEAD^{tree}")
    live_branch = git("branch", "--show-current")
    live_clean = not bool(git("status", "--porcelain=v1", "--untracked-files=all"))
    mismatches = []
    for label, expected, observed in (
        ("head", candidate.get("head"), live_head),
        ("tree", candidate.get("tree"), live_tree),
        ("branch", candidate.get("branch"), live_branch),
        ("clean", candidate.get("clean"), live_clean),
    ):
        if expected != observed:
            mismatches.append(f"{label}(packet={expected!r}, live={observed!r})")
    if mismatches:
        raise ContractError("live candidate identity mismatch: " + ", ".join(mismatches))

    expected_status_digest = candidate.get("status_porcelain_v2_z_sha256")
    expected_status_bytes = candidate.get("status_bytes")
    if expected_status_digest is not None or expected_status_bytes is not None:
        completed = subprocess.run(
            ["git", "-C", str(repo_root), "status", "--porcelain=v2", "-z"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if completed.returncode != 0:
            raise ContractError(
                "live Git status verification failed: "
                + completed.stderr.decode("utf-8", errors="replace").strip()
            )
        observed_digest = sha256(completed.stdout)
        observed_bytes = len(completed.stdout)
        if expected_status_digest != observed_digest or expected_status_bytes != observed_bytes:
            raise ContractError(
                "live candidate identity mismatch: status porcelain digest/bytes drifted "
                f"(packet={expected_status_digest}/{expected_status_bytes}, "
                f"live={observed_digest}/{observed_bytes})"
            )

    for field, git_args in (
        ("unstaged_diff_sha256", ("diff", "--binary", "--no-ext-diff")),
        ("staged_diff_sha256", ("diff", "--cached", "--binary", "--no-ext-diff")),
    ):
        expected_digest = candidate.get(field)
        if expected_digest is None:
            continue
        completed = subprocess.run(
            ["git", "-C", str(repo_root), *git_args],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if completed.returncode != 0:
            raise ContractError(
                f"live Git {field} verification failed: "
                + completed.stderr.decode("utf-8", errors="replace").strip()
            )
        observed_digest = sha256(completed.stdout)
        if expected_digest != observed_digest:
            raise ContractError(
                f"live candidate identity mismatch: {field} drifted "
                f"(packet={expected_digest}, live={observed_digest})"
            )


def verify_package(package_dir: Path, repo_root: Path | None = None) -> dict[str, Any]:
    manifest = load_json(package_dir / MANIFEST_NAME)
    if manifest.get("schema") != MANIFEST_SCHEMA:
        raise ContractError("package manifest schema mismatch")
    files = manifest.get("files")
    if not isinstance(files, dict):
        raise ContractError("package manifest files map missing")
    for name in (PACKET_NAME, PROMPT_NAME):
        expected = files.get(name)
        if not isinstance(expected, dict):
            raise ContractError(f"package manifest entry missing: {name}")
        verify_manifest_file(package_dir, name, expected)

    packet = load_json(package_dir / PACKET_NAME)
    if packet.get("schema") != PACKET_SCHEMA:
        raise ContractError("successor packet schema mismatch")
    require_exact_identity(packet)
    require_do_not_replay(packet)
    if packet.get("authority_ceiling") != "NONE" or packet.get("campaign_authority") is not False:
        raise ContractError("packet authority ceiling was widened")
    if packet.get("thread6_11_created") is not False:
        raise ContractError("packet falsely claims Thread6.11 creation")
    claimed_content_hash = packet.get("packet_content_sha256")
    recomputed_content_hash = packet_content_hash(packet)
    if claimed_content_hash != recomputed_content_hash:
        raise ContractError(
            f"packet content hash mismatch: claimed {claimed_content_hash}, recomputed {recomputed_content_hash}"
        )
    if manifest.get("packet_content_sha256") != claimed_content_hash:
        raise ContractError("packet content hash disagrees with package manifest")

    evidence_index = packet.get("evidence_index")
    if not isinstance(evidence_index, list):
        raise ContractError("packet evidence index missing")
    seen: set[str] = set()
    for item in evidence_index:
        if not isinstance(item, dict):
            raise ContractError("packet evidence entry must be an object")
        evidence_id = item.get("id")
        if evidence_id in seen:
            raise ContractError(f"duplicate evidence id in packet: {evidence_id}")
        seen.add(evidence_id)
        path = Path(str(item.get("path", "")))
        if not path.is_file():
            raise ContractError(f"evidence drift: file missing for {evidence_id}: {path}")
        size, digest = sha256_file(path)
        if item.get("bytes") != size or item.get("sha256") != digest:
            raise ContractError(f"evidence drift for {evidence_id}")

    mode = packet.get("packet_mode")
    if mode == FINAL:
        validate_final_snapshot(packet)
        verification = "FINAL"
    elif mode == PROVISIONAL:
        if packet.get("entry_point") != "UNSET":
            raise ContractError("provisional packet entry point was promoted")
        verification = "PROVISIONAL"
    else:
        raise ContractError("unknown packet mode")

    prompt = (package_dir / PROMPT_NAME).read_text(encoding="utf-8")
    if claimed_content_hash not in prompt:
        raise ContractError("launch prompt is not bound to the packet content hash")
    if "THREAD6_11_CREATED_BY_THIS_PACKET=NO" not in prompt:
        raise ContractError("launch prompt lacks non-creation boundary")
    if repo_root is not None:
        verify_live_repo(packet, repo_root)

    return {
        "verification": verification,
        "entry_point": packet["entry_point"],
        "packet_content_sha256": claimed_content_hash,
        "evidence_count": len(evidence_index),
        "live_repo_checked": repo_root is not None,
    }


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build", help="build a successor package")
    build.add_argument("--snapshot", type=Path, required=True)
    build.add_argument("--output-dir", type=Path, required=True)

    verify = subparsers.add_parser("verify", help="verify an existing successor package")
    verify.add_argument("--package-dir", type=Path, required=True)
    verify.add_argument("--repo-root", type=Path)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        if args.command == "build":
            result = build_package(args.snapshot, args.output_dir)
        else:
            result = verify_package(args.package_dir, args.repo_root)
    except ContractError as exc:
        print(f"successor-packet: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
