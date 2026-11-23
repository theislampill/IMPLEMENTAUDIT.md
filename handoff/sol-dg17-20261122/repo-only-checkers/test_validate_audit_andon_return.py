"""DRAFT tests for validate_audit_andon_return.py (adviser; fixtures, not native evidence)."""
import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path

TOOL = Path(__file__).with_name("validate_audit_andon_return.py")


def record(route, returns_to, **extra):
    base = {"route": route, "returns_to": returns_to, "classification": "systemic checker gap",
            "causal_account": ["fact", "cause"], "disposition": "SYSTEMIC",
            "countermeasure_options": ["add owner check"], "escalation_recommendation": "L4 decides",
            "follow_up_evidence_obligation": "rerun owner suite"}
    if route == "DIRECT":
        base["recipient_id"] = DIRECT["caller"]
    else:
        base["governor_envelope_digest"] = GOV["governor_envelope_digest"]
    base.update(extra)
    return base


def run(envelope, rec):
    out = subprocess.run([sys.executable, "-I", str(TOOL)], input=json.dumps({"envelope": envelope, "record": rec}),
                         capture_output=True, text=True, timeout=30)
    return out.returncode, json.loads(out.stdout)


FROZEN = {"audit_object": "stocktake", "andon_occurrence": "O1"}
FROZEN_SHA256 = hashlib.sha256(b'{"andon_occurrence":"O1","audit_object":"stocktake"}').hexdigest()
GOV = {"route": "GOVERNED", "governor_envelope": FROZEN, "governor_envelope_digest": FROZEN_SHA256}
DIRECT = {"route": "DIRECT", "caller": "user"}


class AndonReturn(unittest.TestCase):
    def test_governed_returns_to_governor(self):          # positive, N04/H07
        self.assertEqual(run(GOV, record("GOVERNED", "GOVERNOR"))[0], 0)

    def test_direct_returns_to_caller(self):              # positive, N05/H07
        self.assertEqual(run(DIRECT, record("DIRECT", "ACTUAL_CALLER"))[0], 0)

    def test_governed_returning_to_caller_refused(self):  # M11 mutant
        self.assertEqual(run(GOV, record("GOVERNED", "ACTUAL_CALLER"))[0], 1)

    def test_direct_returning_to_governor_refused(self):  # M11 mutant
        self.assertEqual(run(DIRECT, record("DIRECT", "GOVERNOR"))[0], 1)

    def test_governed_without_envelope_refused(self):
        self.assertEqual(run({"route": "GOVERNED"}, record("GOVERNED", "L4"))[0], 1)

    def test_authority_field_refused(self):              # N04/N05 fence
        rec = record("GOVERNED", "L4")
        rec["countermeasure_options"] = [{"patch": "x"}]
        self.assertEqual(run(GOV, rec)[0], 1)

    def test_terminal_marker_refused(self):              # N05 closure attempt
        self.assertEqual(run(DIRECT, record("DIRECT", "ACTUAL_CALLER", escalation_recommendation="AUDIT_COMPLETE"))[0], 1)

    def test_extra_field_refused(self):                  # no sibling route / STOP authority
        self.assertEqual(run(GOV, record("GOVERNED", "L4", next_child="audit-implement"))[0], 1)

    def test_malformed_refused(self):
        out = subprocess.run([sys.executable, "-I", str(TOOL)], input="{", capture_output=True, text=True, timeout=30)
        self.assertEqual(out.returncode, 1)


    def test_direct_without_observed_recipient_refused(self):
        returned = record("DIRECT", "ACTUAL_CALLER")
        del returned["recipient_id"]
        self.assertEqual(run(DIRECT, returned)[0], 1)

    def test_governed_placeholder_digest_refused(self):
        unbound = {"route": "GOVERNED", "governor_envelope_digest": "unknown"}
        self.assertEqual(run(unbound, record("GOVERNED", "L4"))[0], 1)


    def test_direct_different_recipient_refused(self):
        code, verdict = run(DIRECT, record("DIRECT", "ACTUAL_CALLER", recipient_id="other-user"))
        self.assertEqual((code, verdict["reason"]), (1, "direct return recipient differs from the caller"))

    def test_governed_other_return_digest_refused(self):
        code, verdict = run(GOV, record("GOVERNED", "L4", governor_envelope_digest="0" * 64))
        self.assertEqual((code, verdict["reason"]), (1, "governed return differs from the frozen envelope digest"))

    def test_governed_mutated_envelope_refused(self):
        stale = dict(GOV, governor_envelope=dict(FROZEN, andon_occurrence="O2"))
        code, verdict = run(stale, record("GOVERNED", "L4"))
        self.assertEqual((code, verdict["reason"]), (1, "governed return differs from the frozen envelope digest"))

    def test_malformed_envelope_type_refused(self):
        code, verdict = run([], record("GOVERNED", "L4"))
        self.assertEqual((code, verdict["decision"]), (1, "REFUSE"))

    def test_duplicate_member_is_reported_as_malformed(self):
        out = subprocess.run([sys.executable, "-I", str(TOOL)],
                             input='{"envelope":{},"record":{},"record":[]}',
                             capture_output=True, text=True, timeout=30)
        self.assertEqual((out.returncode, json.loads(out.stdout)["reason"]), (1, "malformed input"))


if __name__ == "__main__":
    unittest.main()
