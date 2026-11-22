#!/usr/bin/env python3
"""DRAFT (adviser, not reviewed, not shipped): Jidoka vs Andon distinction check.

Encodes references/lean-operating-discipline.md at 51416b2f:
  Jidoka = stop-the-line when evidence fails (no downstream propagation);
  Andon  = visible abnormality block with status, blocker, failing check,
           owner/source and next concrete action.
#211 N07 rejects both "logged-but-propagated" (Andon without Jidoka) and
"stopped-but-invisible" (Jidoka without Andon). M06 removes either half.
Input: ordered event list (JSON on stdin). Exit 0 accept, 1 refuse.
"""
import json
import sys

FAIL = {"PROOF_FAILURE", "REGRESSION", "HIDDEN_RERUN", "SUBSTITUTED_COMMAND",
        "PACKAGE_BOUNDARY_VIOLATION", "RELEASE_ASSET_MISMATCH"}
PROPAGATING = {"DISPATCH", "PHASE_START", "CLAIM", "CLOSURE", "RELEASE"}
ANDON_FIELDS = {"status", "blocker", "failing_check", "owner_source", "next_action"}


def verdict(events):
    open_failure = None
    for index, event in enumerate(events):
        kind = event.get("kind")
        if kind in FAIL and open_failure is None:
            open_failure = {"index": index, "check": event.get("check"), "andon": False}
        elif kind == "ANDON" and open_failure is not None:
            block = event.get("block", {})
            if not ANDON_FIELDS <= set(block) or block.get("failing_check") != open_failure["check"]:
                return "Andon block incomplete or names a different failing check"
            open_failure["andon"] = True
        elif kind in PROPAGATING and open_failure is not None:
            return "logged-but-propagated: downstream %s after unresolved failure" % kind
        elif kind == "RECOVERED" and open_failure is not None:
            if not open_failure["andon"]:
                return "stopped-but-invisible: recovery without a visible Andon block"
            if not event.get("reverified"):
                return "recovery without reverification of the failing check"
            open_failure = None
    if open_failure is not None and not open_failure["andon"]:
        return "stopped-but-invisible: failure never surfaced as Andon"
    return None


def main():
    try:
        events = json.loads(sys.stdin.read())
        if not isinstance(events, list):
            raise ValueError
        reason = verdict(events)
    except (ValueError, AttributeError):
        reason = "malformed event list"
    print(json.dumps({"schema": "draft.jidoka-andon-verdict.v1",
                      "decision": "REFUSE" if reason else "ACCEPT", "reason": reason}))
    return 1 if reason else 0


if __name__ == "__main__":
    sys.exit(main())
