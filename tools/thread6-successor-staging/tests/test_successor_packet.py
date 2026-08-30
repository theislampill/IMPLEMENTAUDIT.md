import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


TOOL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = TOOL_ROOT / "successor_packet.py"

CONTROLLER = "v0333-release"
CLAIM = "10bd7bc5098af00d26b1c319683a64f5"
RUN = "v041-thread5-autodag-TmDJfs"
OBJECTIVE = "COMPLETE_REMAINING_A_TO_F_PRECUTOVER_PATH_AND_PROVE_HEALTHY_THREAD7_TAKEOVER"

REQUIRED_DO_NOT_REPLAY = [
    "CAMPAIGN_PHASE_A",
    "CAMPAIGN_PHASE_B",
    "ACCEPTED_ENGINEERING_PRODUCTS",
    "ACCEPTED_REVIEWS_AND_QUALIFICATION",
    "PRIOR_HBASE_ATTEMPTS_BEYOND_TERMINAL_FACTS",
    "BROAD_STATE_ROADMAP_HISTORY",
    "WORKER_TRANSCRIPTS",
    "REPAIRED_PACKAGE_FAILURES",
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class SuccessorPacketContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.evidence = self.root / "evidence.json"
        self.evidence.write_text('{"status":"buffered"}\n', encoding="utf-8")
        self.snapshot = self.root / "snapshot.json"
        self.output = self.root / "package"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def base_snapshot(self) -> dict:
        return {
            "schema": "implementaudit.thread6-successor-snapshot.v1",
            "packet_mode": "PROVISIONAL_NONAUTHORITATIVE",
            "entry_point": "UNSET",
            "campaign": {
                "controller": CONTROLLER,
                "claim": CLAIM,
                "run": RUN,
                "current_phase": "C",
            },
            "goal": {
                "governor": "/implementaudit",
                "status": "active",
                "terminal_objective": OBJECTIVE,
                "thread6_10_is_thread7": False,
                "a_to_g_native_closure_before_thread7": True,
            },
            "authority": {
                "continuity_receipt": "UNSET_PENDING_GOVERNOR_REFRESH",
                "generation_pointer": "UNSET_PENDING_GOVERNOR_REFRESH",
                "host_binding": "UNSET_PENDING_GOVERNOR_REFRESH",
                "current_route": "UNSET_PENDING_GOVERNOR_REFRESH",
                "source_ref": "UNSET_PENDING_GOVERNOR_REFRESH",
            },
            "frontier": {
                "next_typed_edge": "UNSET_PENDING_GOVERNOR_REFRESH",
                "summary": "G023x package/HBASE frontier; exact live state requires governor refresh",
            },
            "candidate": {
                "repository": "C:/workspace/ai/improveimplementaudit/IMPLEMENTAUDIT-v041-thread5-controller",
                "head": "57b48140f1266cbd3f6316718463409a134f1969",
                "tree": "UNSET_PENDING_GOVERNOR_REFRESH",
                "branch": "thread5/v041-controller",
                "clean": False,
                "identity_class": "OBSERVED_WORKTREE_NOT_FROZEN_CANDIDATE",
            },
            "corrections": [],
            "shadow": {
                "branch": "experiment/verify-package-shadow-resume",
                "head": "2b8c0bee8d0235374cb361d1e234d998b3f4d4e1",
                "authority": "NONE",
                "status": "DEFERRED_PENDING_EXCLUSIVE_RESOURCE_WINDOW",
            },
            "canonical_verify": {
                "status": "NOT_TERMINAL_OBSERVED",
                "terminal_evidence_ref": "UNSET",
            },
            "hbase": {
                "status": "HELD_NOT_QUALIFIED",
                "result_ref": "UNSET",
            },
            "thread6_9": {"status": "PAUSED"},
            "trigger": {
                "status": "NOT_EVIDENCED_BY_THREAD6_10",
                "evidence_ref": "UNSET",
            },
            "do_not_replay": list(REQUIRED_DO_NOT_REPLAY),
            "evidence": [
                {
                    "id": "buffered-example",
                    "role": "BUFFERED_NONAUTHORITATIVE_EVIDENCE",
                    "path": str(self.evidence),
                }
            ],
        }

    def run_tool(self, *args: str, expect: int = 0) -> subprocess.CompletedProcess[str]:
        completed = subprocess.run(
            [sys.executable, "-I", "-S", str(SCRIPT), *args],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(
            expect,
            completed.returncode,
            msg=f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}",
        )
        return completed

    def write_snapshot(self, snapshot: dict) -> None:
        self.snapshot.write_text(json.dumps(snapshot, indent=2) + "\n", encoding="utf-8")

    def build(self, snapshot: dict | None = None, expect: int = 0) -> subprocess.CompletedProcess[str]:
        self.write_snapshot(snapshot or self.base_snapshot())
        return self.run_tool(
            "build",
            "--snapshot",
            str(self.snapshot),
            "--output-dir",
            str(self.output),
            expect=expect,
        )

    def verify(self, expect: int = 0) -> subprocess.CompletedProcess[str]:
        return self.run_tool("verify", "--package-dir", str(self.output), expect=expect)

    def test_provisional_build_binds_evidence_without_authority(self) -> None:
        """Catches builders that omit evidence digests or imply succession authority."""
        original = self.evidence.read_bytes()
        self.build()
        result = json.loads(self.verify().stdout)

        packet_path = self.output / "THREAD6_11_SUCCESSOR_PACKET.json"
        prompt_path = self.output / "THREAD6_11_LAUNCH_PROMPT.md"
        manifest_path = self.output / "SUCCESSOR_PACKAGE_MANIFEST.json"
        self.assertTrue(packet_path.is_file())
        self.assertTrue(prompt_path.is_file())
        self.assertTrue(manifest_path.is_file())

        packet = json.loads(packet_path.read_text(encoding="utf-8"))
        indexed = packet["evidence_index"][0]
        self.assertEqual(len(original), indexed["bytes"])
        self.assertEqual(sha256_bytes(original), indexed["sha256"])
        self.assertEqual("PROVISIONAL_NONAUTHORITATIVE", packet["packet_mode"])
        self.assertEqual("NONE", packet["authority_ceiling"])
        self.assertFalse(packet["thread6_11_created"])
        self.assertEqual("PAUSED", packet["thread6_9"]["status"])
        self.assertEqual("PROVISIONAL", result["verification"])
        self.assertEqual(original, self.evidence.read_bytes())

    def test_evidence_tamper_is_rejected(self) -> None:
        """Catches verifiers that trust stored evidence hashes without readback."""
        self.build()
        self.evidence.write_text('{"status":"tampered"}\n', encoding="utf-8")
        completed = self.verify(expect=1)
        self.assertIn("evidence drift", completed.stderr.lower())

    def test_packet_tamper_is_rejected(self) -> None:
        """Catches packet edits made after the content and package hashes were issued."""
        self.build()
        packet_path = self.output / "THREAD6_11_SUCCESSOR_PACKET.json"
        packet = json.loads(packet_path.read_text(encoding="utf-8"))
        packet["frontier"]["summary"] = "tampered"
        packet_path.write_text(json.dumps(packet, indent=2) + "\n", encoding="utf-8")
        completed = self.verify(expect=1)
        self.assertIn("packet", completed.stderr.lower())
        self.assertIn("hash", completed.stderr.lower())

    def test_duplicate_evidence_ids_are_rejected(self) -> None:
        """Catches ambiguous first-wins evidence indexing."""
        snapshot = self.base_snapshot()
        snapshot["evidence"].append(dict(snapshot["evidence"][0]))
        completed = self.build(snapshot, expect=1)
        self.assertIn("duplicate evidence id", completed.stderr.lower())

    def test_wrong_campaign_identity_is_rejected(self) -> None:
        """Catches accidental creation of a new controller/run package."""
        snapshot = self.base_snapshot()
        snapshot["campaign"]["run"] = "new-run"
        completed = self.build(snapshot, expect=1)
        self.assertIn("campaign identity", completed.stderr.lower())

    def test_post_hbase_finalization_requires_exact_authority_and_result(self) -> None:
        """Catches false post-HBASE successor readiness from placeholder fields."""
        snapshot = self.base_snapshot()
        snapshot["packet_mode"] = "FINALIZED_FOR_GOVERNOR_VERIFICATION"
        snapshot["entry_point"] = "POST_HBASE"
        snapshot["frontier"]["next_typed_edge"] = "ORDERED_R30_J0_CONSUMPTION_SELECTIVE_REVALIDATION"
        completed = self.build(snapshot, expect=1)
        self.assertIn("finalized packet", completed.stderr.lower())

        snapshot["authority"] = {
            "continuity_receipt": "refs/implementaudit/continuity-receipts/v0333-release/G0XXX@deadbeef",
            "generation_pointer": "1" * 40,
            "host_binding": "codex/thread/G0001",
            "current_route": "2" * 40,
            "source_ref": "governor-final-handoff-snapshot.json@sha256:" + "3" * 64,
        }
        snapshot["candidate"]["tree"] = "8" * 40
        snapshot["candidate"]["identity_class"] = "FROZEN_EXACT_CANDIDATE"
        snapshot["canonical_verify"] = {
            "status": "PASS_TERMINAL",
            "terminal_evidence_ref": "canonical-result.json@sha256:" + "4" * 64,
        }
        snapshot["hbase"] = {
            "status": "QUALIFIED",
            "result_ref": "hbase-result.json@sha256:" + "5" * 64,
        }
        snapshot["trigger"] = {
            "status": "HBASE_QUALIFIED_EVIDENCED_BY_THREAD6_10",
            "evidence_ref": "hbase-authority.json@sha256:" + "6" * 64,
        }
        self.build(snapshot)
        result = json.loads(self.verify().stdout)
        self.assertEqual("FINAL", result["verification"])
        self.assertEqual("POST_HBASE", result["entry_point"])

    def test_pre_hbase_finalization_requires_controller_evidenced_circuit_breaker(self) -> None:
        """Catches this staging lane inferring the succession trigger itself."""
        snapshot = self.base_snapshot()
        snapshot["packet_mode"] = "FINALIZED_FOR_GOVERNOR_VERIFICATION"
        snapshot["entry_point"] = "PRE_HBASE_EXACT_FRONTIER"
        snapshot["authority"] = {
            "continuity_receipt": "refs/implementaudit/continuity-receipts/v0333-release/G0XXX@deadbeef",
            "generation_pointer": "1" * 40,
            "host_binding": "codex/thread/G0001",
            "current_route": "2" * 40,
            "source_ref": "governor-final-handoff-snapshot.json@sha256:" + "3" * 64,
        }
        snapshot["candidate"]["tree"] = "8" * 40
        snapshot["candidate"]["identity_class"] = "FROZEN_EXACT_CANDIDATE"
        snapshot["frontier"]["next_typed_edge"] = "FRESH_PACKAGE_REPAIR_TO_RELAUNCH_TRANCHE"
        completed = self.build(snapshot, expect=1)
        self.assertIn("circuit breaker", completed.stderr.lower())

        snapshot["trigger"] = {
            "status": "CIRCUIT_BREAKER_EVIDENCED_BY_THREAD6_10",
            "evidence_ref": "thread6-10-trigger.json@sha256:" + "7" * 64,
        }
        self.build(snapshot)
        result = json.loads(self.verify().stdout)
        self.assertEqual("FINAL", result["verification"])
        self.assertEqual("PRE_HBASE_EXACT_FRONTIER", result["entry_point"])

    def test_missing_do_not_replay_item_is_rejected(self) -> None:
        """Catches successor packets that silently permit broad campaign replay."""
        snapshot = self.base_snapshot()
        snapshot["do_not_replay"].remove("WORKER_TRANSCRIPTS")
        completed = self.build(snapshot, expect=1)
        self.assertIn("do-not-replay", completed.stderr.lower())

    def test_optional_live_repo_check_rejects_candidate_drift(self) -> None:
        """Catches a package verified against a different live candidate state."""
        repo = self.root / "repo"
        repo.mkdir()
        subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.name", "Test"], check=True)
        subprocess.run(
            ["git", "-C", str(repo), "config", "user.email", "test@example.invalid"],
            check=True,
        )
        tracked = repo / "tracked.txt"
        tracked.write_text("one\n", encoding="utf-8")
        subprocess.run(["git", "-C", str(repo), "add", "tracked.txt"], check=True)
        subprocess.run(["git", "-C", str(repo), "commit", "-qm", "base"], check=True)

        def git(*args: str) -> str:
            return subprocess.run(
                ["git", "-C", str(repo), *args],
                text=True,
                capture_output=True,
                check=True,
            ).stdout.strip()

        tracked.write_text("dirty-one\n", encoding="utf-8")
        status_bytes = subprocess.run(
            ["git", "-C", str(repo), "status", "--porcelain=v2", "-z"],
            stdout=subprocess.PIPE,
            check=True,
        ).stdout
        unstaged_diff = subprocess.run(
            ["git", "-C", str(repo), "diff", "--binary", "--no-ext-diff"],
            stdout=subprocess.PIPE,
            check=True,
        ).stdout
        staged_diff = subprocess.run(
            ["git", "-C", str(repo), "diff", "--cached", "--binary", "--no-ext-diff"],
            stdout=subprocess.PIPE,
            check=True,
        ).stdout
        snapshot = self.base_snapshot()
        snapshot["candidate"] = {
            "repository": str(repo),
            "head": git("rev-parse", "HEAD"),
            "tree": git("rev-parse", "HEAD^{tree}"),
            "branch": git("branch", "--show-current"),
            "clean": False,
            "identity_class": "OBSERVED_WORKTREE_NOT_FROZEN_CANDIDATE",
            "status_porcelain_v2_z_sha256": sha256_bytes(status_bytes),
            "status_bytes": len(status_bytes),
            "unstaged_diff_sha256": sha256_bytes(unstaged_diff),
            "staged_diff_sha256": sha256_bytes(staged_diff),
        }
        self.build(snapshot)
        checked = self.run_tool(
            "verify",
            "--package-dir",
            str(self.output),
            "--repo-root",
            str(repo),
        )
        self.assertTrue(json.loads(checked.stdout)["live_repo_checked"])

        tracked.write_text("dirty-two\n", encoding="utf-8")
        completed = self.run_tool(
            "verify",
            "--package-dir",
            str(self.output),
            "--repo-root",
            str(repo),
            expect=1,
        )
        self.assertIn("live candidate identity mismatch", completed.stderr.lower())


if __name__ == "__main__":
    unittest.main()
