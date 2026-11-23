"""DRAFT tests for check_jidoka_andon.py (adviser; fixtures, not native evidence)."""
import json
import subprocess
import sys
import unittest
from pathlib import Path

TOOL = Path(__file__).parents[1] / "scripts/check-jidoka-andon.py"
ANDON = {"kind": "ANDON", "block": {"status": "STOPPED", "blocker": "smoke B regression",
         "failing_check": "smoke-b", "owner_source": "scripts/x.sh", "next_action": "repair owner"}}
FAIL = {"kind": "REGRESSION", "check": "smoke-b"}


def run(events):
    out = subprocess.run([sys.executable, "-I", str(TOOL)], input=json.dumps(events),
                         capture_output=True, text=True, timeout=30)
    return out.returncode


class JidokaAndon(unittest.TestCase):
    def test_stop_signal_repair_reverify(self):        # N07 positive
        self.assertEqual(run([FAIL, ANDON, {"kind": "RECOVERED", "check": "smoke-b", "reverified": True}, {"kind": "CLAIM"}]), 0)

    def test_logged_but_propagated(self):               # N07 arm 1 / M06 non-propagation removed
        self.assertEqual(run([FAIL, ANDON, {"kind": "DISPATCH"}]), 1)

    def test_stopped_but_invisible(self):               # N07 arm 2 / M06 visibility removed
        self.assertEqual(run([FAIL, {"kind": "RECOVERED", "check": "smoke-b", "reverified": True}]), 1)

    def test_never_surfaced(self):
        self.assertEqual(run([FAIL]), 1)

    def test_incomplete_andon_block(self):
        bad = {"kind": "ANDON", "block": {"status": "STOPPED"}}
        self.assertEqual(run([FAIL, bad]), 1)

    def test_andon_for_wrong_check(self):
        wrong = json.loads(json.dumps(ANDON)); wrong["block"]["failing_check"] = "smoke-a"
        self.assertEqual(run([FAIL, wrong]), 1)

    def test_recovery_without_reverify(self):
        self.assertEqual(run([FAIL, ANDON, {"kind": "RECOVERED", "check": "smoke-b", "reverified": False}]), 1)

    def test_clean_run_no_ceremony(self):               # cheap path: no failure, no Andon needed
        self.assertEqual(run([{"kind": "PHASE_START"}, {"kind": "CLAIM"}]), 0)

    def test_malformed(self):
        self.assertEqual(run({"not": "a list"}), 1)


    def test_second_unresolved_check_stops_propagation(self):
        second = {"kind": "PROOF_FAILURE", "check": "inventory-count"}
        recovered = {"kind": "RECOVERED", "check": "smoke-b", "reverified": True}
        self.assertEqual(run([FAIL, second, ANDON, recovered, {"kind": "DISPATCH"}]), 1)

    def test_recovery_without_check_refused(self):
        self.assertEqual(run([FAIL, ANDON, {"kind": "RECOVERED", "reverified": True}]), 1)

    def test_recovery_of_different_check_refused(self):
        recovery = {"kind": "RECOVERED", "check": "inventory-count", "reverified": True}
        self.assertEqual(run([FAIL, ANDON, recovery]), 1)


    def test_two_checks_recover_independently(self):
        second = {"kind": "PROOF_FAILURE", "check": "inventory-count"}
        second_andon = dict(ANDON, block=dict(ANDON["block"], failing_check="inventory-count"))
        first_recovery = {"kind": "RECOVERED", "check": "smoke-b", "reverified": True}
        second_recovery = dict(first_recovery, check="inventory-count")
        self.assertEqual(run([FAIL, second, ANDON, second_andon, first_recovery, second_recovery,
                              {"kind": "DISPATCH"}]), 0)

    def test_duplicate_open_identity_refused(self):
        self.assertEqual(run([FAIL, FAIL, ANDON]), 1)

    def test_non_boolean_reverification_refused(self):
        self.assertEqual(run([FAIL, ANDON, {"kind": "RECOVERED", "check": "smoke-b", "reverified": 1}]), 1)

    def test_malformed_event_kind_refused(self):
        self.assertEqual(run([{"kind": []}]), 1)


if __name__ == "__main__":
    unittest.main()
