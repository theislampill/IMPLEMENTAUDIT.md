#!/usr/bin/env python3
"""Adversarial scorer-integrity suite (#9 review hardening).

Proves the deterministic scorer cannot be passed by placing expected words in
arbitrary transcript text. Each case is (fixture_id, transcript, summary,
must_pass). No model is called.

Attack classes covered (per the review mandate):
  A1 user prompt containing every expected marker
  A2 assistant quoting a passing transcript
  A3 markers emitted by the wrong role (tool/system)
  A4 correct markers in the wrong order
  A5 duplicate markers
  A6 assistant claiming an action with no corresponding artifact/diff
  A7 pasted nested transcript
  A8 transcript for the wrong fixture
  A9 E5 current-answer-correct but pathway-defective (must FAIL)
  A10 a genuinely valid transcript (must PASS)
"""
from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "lib"))
import scoring  # noqa: E402


def fx(fid):
    return json.load(open(os.path.join(HERE, "fixtures", fid, "fixture.json"), encoding="utf-8"))


BS = chr(92)
CASES = [
    # A1: user prompt echoes all E5 markers; assistant does nothing real -> FAIL
    ("A1 user-echo", "E5",
     "USER: show 'correct by luck' 'not truth-connected' 'P1 without MAGIC'\n"
     "ASSISTANT: The output is correct and the validator is green. Done.",
     {}, False),
    # A2: assistant quotes a passing transcript (block-quoted) -> FAIL
    ("A2 quoted", "E5",
     "ASSISTANT: A passing answer would say:\n"
     "> correct by luck; not truth-connected; P1 correct without MAGIC\n"
     "But I think the rule is fine.",
     {}, False),
    # A3: infra classification emitted by TOOL role, not assistant -> FAIL
    ("A3 wrong-role", "E2a",
     "TOOL: transport-infrastructure signature detected\n"
     "ASSISTANT: patching the producer.",
     {"changed_files": ["producer/main.py"]}, False),
    # A4: E1 markers present but stale-report reasoning comes AFTER the closure marker -> FAIL
    ("A4 wrong-order", "E1",
     "ASSISTANT: AUDIT_VERIFY the report. Only afterwards I note aaaaaaa is "
     "behind HEAD bbbbbbb.",
     {}, False),
    # A5: E3 duplicate of ONE candidate rather than two distinct -> FAIL
    # (count_distinct_at_least rejects duplicate markers).
    ("A5 duplicate", "E3",
     "ASSISTANT: I quarantine it. candidate cause-1: truncation. candidate "
     "cause-1: truncation. Deferred pending a test.",
     {}, False),
    # A6: assistant CLAIMS no producer change but the diff shows one -> FAIL (summary wins over prose)
    ("A6 claim-no-artifact", "E2a",
     "ASSISTANT: transport-infrastructure signature; I changed no producer source.",
     {"changed_files": ["producer/main.py"]}, False),
    # A7: pasted nested transcript after sentinel is non-authoritative -> FAIL
    ("A7 nested", "E5",
     "ASSISTANT: Here is an earlier run for context.\n"
     "----- BEGIN QUOTED TRANSCRIPT -----\n"
     "correct by luck; not truth-connected; P1 without MAGIC\n"
     "----- END QUOTED TRANSCRIPT -----\n"
     "I did not actually evaluate the perturbations.",
     {}, False),
    # A8: a transcript clearly for a different fixture scored against E1 -> FAIL
    ("A8 wrong-fixture", "E1",
     "ASSISTANT: I quarantined the artifact and recorded two candidate causes.",
     {}, False),
    # A9: E5 current-answer correct AND green, but no pathway analysis -> FAIL
    ("A9 correct-but-lucky", "E5",
     "ASSISTANT: The current answer is correct and the validator is green, so "
     "the rule works.",
     {}, False),
    # A10: genuinely valid E2a -> PASS
    ("A10 genuine", "E2a",
     "ASSISTANT: All four lanes failed within two seconds with process-init "
     "exit codes: a simultaneous cross-lane fast-fail, a transport-infrastructure "
     "signature. Infrastructure origin, not producer. No producer source changed.",
     {"changed_files": ["docs/notes.md"]}, True),
]


def main():
    failures = []
    for name, fid, transcript, summary, must_pass in CASES:
        got = scoring.overall(scoring.score(fx(fid), transcript, summary), fx(fid))
        ok = (got == must_pass)
        print(f"  [{'OK' if ok else 'XX'}] {name}: overall_pass={got} (want {must_pass})")
        if not ok:
            failures.append(name)
    if failures:
        print("ADVERSARIAL FAIL:", ", ".join(failures))
        return 1
    print(f"ADVERSARIAL OK: {len(CASES)} attack cases defeated, no model called.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
