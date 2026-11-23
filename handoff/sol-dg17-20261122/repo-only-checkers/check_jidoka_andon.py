"""Check occurrence visibility and non-propagation in a supplied event fixture."""
import json
import sys

FAIL = {"PROOF_FAILURE", "REGRESSION", "HIDDEN_RERUN", "SUBSTITUTED_COMMAND",
        "PACKAGE_BOUNDARY_VIOLATION", "RELEASE_ASSET_MISMATCH"}
PROPAGATING = {"DISPATCH", "PHASE_START", "CLAIM", "CLOSURE", "RELEASE"}
ANDON_FIELDS = {"status", "blocker", "failing_check", "owner_source", "next_action"}


def concrete(value):
    return isinstance(value, str) and bool(value.strip()) and value == value.strip()


def verdict(events):
    if not isinstance(events, list):
        return "malformed event list"
    open_checks = {}
    for event in events:
        if not isinstance(event, dict) or not isinstance(event.get("kind"), str):
            return "malformed event"
        kind = event["kind"]
        if kind in FAIL:
            check = event.get("check")
            if not concrete(check) or check in open_checks:
                return "failure needs an unambiguous check identity"
            open_checks[check] = False
        elif kind == "ANDON":
            block = event.get("block")
            if not isinstance(block, dict) or not all(concrete(block.get(field)) for field in ANDON_FIELDS):
                return "Andon block is incomplete"
            check = block["failing_check"]
            if check not in open_checks:
                return "Andon names no unresolved check"
            open_checks[check] = True
        elif kind == "RECOVERED":
            check = event.get("check")
            if not concrete(check) or check not in open_checks:
                return "recovery names no unresolved check"
            if not open_checks[check]:
                return "stopped-but-invisible: recovery without a visible Andon block"
            if event.get("reverified") is not True:
                return "recovery without reverification of the failing check"
            del open_checks[check]
        elif kind in PROPAGATING:
            if open_checks:
                return f"logged-but-propagated: downstream {kind} after unresolved failure"
        else:
            return "unknown event kind"
    if any(not visible for visible in open_checks.values()):
        return "stopped-but-invisible: failure never surfaced as Andon"
    return None


def main():
    try:
        reason = verdict(json.load(sys.stdin))
    except (ValueError, RecursionError):
        reason = "malformed event list"
    print(json.dumps({"schema": "sol-dg17.jidoka-andon-fixture-verdict.v1",
                      "decision": "REFUSE" if reason else "ACCEPT", "reason": reason,
                      "authority": "NONE"}))
    return 1 if reason else 0


if __name__ == "__main__":
    sys.exit(main())
