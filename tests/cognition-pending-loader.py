#!/usr/bin/env python3
"""Finite actual-consumer stored-loader controls; no native authority.

The default selection runs stored-loader and top-level counter discriminators
with real H0/pending setup. --top-level-counter-controls-only selects the
finite counter increment without replaying the earlier loader population.
--include-existing-counter-controls also reuses the original selected NaN
counter tests and an actual integer successor, without replaying the old bank.
Every process, preimage and physical before/after census is retained.
"""
from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import os
from pathlib import Path
import stat
import sys
import tempfile
import traceback

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("_pending_loader_durability", ROOT / "tests/cognition-pending-durability.py")
BASE = importlib.util.module_from_spec(spec)
spec.loader.exec_module(BASE)


def stamp(path):
    info = path.lstat()
    return {"device": info.st_dev, "inode": info.st_ino, "mode": info.st_mode,
            "links": info.st_nlink, "bytes": info.st_size,
            "mtime_ns": info.st_mtime_ns, "ctime_ns": info.st_ctime_ns,
            "sha256": BASE.sha(path.read_bytes()) if stat.S_ISREG(info.st_mode) else None}


def replacement_worker(source_text, store_text, session, owner, action):
    """Schedule a same-byte replacement after the real descriptor read."""
    source, store = Path(source_text), Path(store_text)
    module_spec = importlib.util.spec_from_file_location("_actual_pending_loader", source)
    pending = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(pending)
    target = pending.state_path(store, session)
    BASE.require(action == "status" and target.is_relative_to(store), "fault target escaped fixture")
    retained = target.with_name("retained-postread.pending.json")
    replacement = target.with_name("replacement-postread.pending.json")
    before = stamp(target)
    replacement.write_bytes(target.read_bytes())
    actual_read = pending.os.read
    reached = []

    def scheduled_read(descriptor, length):
        raw = actual_read(descriptor, length)
        info = os.fstat(descriptor)
        if raw and not reached and (info.st_dev, info.st_ino) == (before["device"], before["inode"]):
            target.rename(retained)
            os.replace(replacement, target)
            reached.append({"old": stamp(retained), "live": stamp(target), "bytes_returned": len(raw)})
        return raw

    pending.os.read = scheduled_read
    sys.argv = [str(source), "--store", str(store), "--session", session, "--owner-id", owner, action]
    result = pending.main()
    BASE.require(len(reached) == 1, "controlled postread replacement was not reached")
    BASE.require(retained.read_bytes() == target.read_bytes(), "fault changed payload instead of physical identity")
    sys.stderr.write(json.dumps({"fault": "same-byte-target-replacement-after-read", "before": before,
                                 "replacement": reached[0], "actual_owner_exit": result}, sort_keys=True) + "\n")
    return result


class RecordedHarness(BASE.Harness):
    def physical_snapshot(self):
        return self.snapshot() if self.store.exists() else {"store_absent": True}

    def call(self, *args, **kwargs):
        number = len(self.records) + 1
        before = self.physical_snapshot()
        original_location = BASE.__file__
        if kwargs.get("mode") == "pending-postread-replacement":
            # Only redirect the existing harness's worker executable locator.
            # All consumer code and stored-state semantics remain untouched.
            BASE.__file__ = __file__
        try:
            return super().call(*args, **kwargs)
        finally:
            BASE.__file__ = original_location
            after = self.physical_snapshot()
            (self.evidence / f"{number:03d}.physical.json").write_text(json.dumps({"before": before, "after": after}, indent=2, sort_keys=True) + "\n")
            if self.records and self.records[-1]["number"] == number:
                row = self.records[-1]
                for stream in ("stdout", "stderr"):
                    (self.evidence / f"{number:03d}.{stream}").write_bytes(row[stream].encode("utf-8"))
                (self.evidence / f"{number:03d}.stdin").write_bytes(row["input"].encode("utf-8"))


def setup(h):
    repository, common, work = (h.fixture / name for name in ("repository", "git-common", "worktree"))
    run = work / ".IMPLEMENTAUDIT/runs/fixture"
    for path in (repository, common, run):
        path.mkdir(parents=True)
    initialized = h.call("init", script="host-session-binding.py",
                         args=["--store", str(h.store), "init", "--owner-id", BASE.OWNER])
    BASE.require(initialized["status"] == "READY", "real H0 initialization failed")
    fields = {
        "owner-id": BASE.OWNER, "host-id": "codex", "host-session-id": BASE.SESSION,
        "controller-id": "fixture-controller", "claim-id": "fixture-claim",
        "explicit-run-root": run, "repository-identity": repository,
        "git-common-directory-identity": common, "worktree-identity": work,
        "activation-event-id": "fixture-activation", "activation-receipt": "opaque-fixture-activation",
        "continuity-generation": "G0001", "continuity-receipt": "opaque-fixture-continuity",
    }
    bound = h.call("bind", script="host-session-binding.py",
                   args=["--store", str(h.store), "bind", *[part for key, value in fields.items() for part in ("--" + key, str(value))]])
    BASE.require(bound["host_activation_proven"] is False and bound["proof_layers"]["host_activation"] == "UNVERIFIED",
                 "constructed attribution gained host authority")
    h.mark("constructed-attribution-host-activation-false")
    before = h.snapshot()
    empty = h.call("status", mode="status-guard")
    BASE.require(empty["decision"] == "NO_PENDING_AUDIT" and before == h.snapshot(), "absent status changed state")
    h.mark("absent-status-original-three-file-read-guard")
    resumed = h.call("resume", {"currentness": "UNRESOLVED", "measured_epoch": None})
    state = h.held(resumed)
    BASE.require(len(state["observations"]) == 1, "setup did not retain one real unresolved delivery")
    before = h.snapshot()
    regular = h.call("status", mode="status-guard")
    BASE.require(regular == resumed and before == h.snapshot(), "finite stored state drifted through original read guard")
    h.mark("finite-status-original-four-file-read-guard")
    return regular


def exercise_new_controls(h, regular):
    original = h.pending.read_bytes()
    BASE.require(original.count(b'"signals": 0') == 1, "fixture requires one genuine zero signals field")
    failures = []
    for name, token, reason in [("nan", b"NaN", "PENDING_STATE_JSON_CONSTANT"),
                                ("overflow", b"1e999", "PENDING_STATE_JSON_NUMBER")]:
        case = "stored-nonfinite-" + name + "-outside-counter-refuses-status"
        wire = original.replace(b'"signals": 0', b'"signals": ' + token, 1)
        h.pending.write_bytes(wire)
        (h.evidence / (case + ".input")).write_bytes(wire)
        before = h.snapshot()
        try:
            value = h.call("status", expected_exit=2)
            BASE.require(value["status"] == "PENDING_OPERATION_REFUSED" and "decision" not in value
                         and value["reason"] == reason, case + ": malformed JSON yielded wrong result")
            BASE.require(before == h.snapshot(), case + ": refusal changed store")
            h.mark(case)
        except AssertionError as error:
            failures.append({"case": case, "error": str(error)})
        finally:
            h.pending.write_bytes(original)
            BASE.require(h.call("status") == regular and h.pending.read_bytes() == original,
                         case + ": original obligation was not restored")

    case = "stored-target-replaced-after-read-refuses-status"
    retained = h.pending.with_name("retained-postread.pending.json")
    replacement = h.pending.with_name("replacement-postread.pending.json")
    before = h.snapshot()
    try:
        value = h.call("status", mode="pending-postread-replacement", expected_exit=2)
        BASE.require(value["status"] == "PENDING_OPERATION_REFUSED" and "decision" not in value
                     and value["reason"] == "PENDING_STATE_CHANGED_DURING_READ", case + ": physical drift yielded wrong result")
        BASE.require(retained.read_bytes() == original and h.pending.read_bytes() == original,
                     "same-byte replacement changed logical data")
        after = h.snapshot()
        excluded = {str(path.relative_to(h.store)) for path in (h.pending, retained, h.pending.parent)}
        BASE.require({k: v for k, v in before.items() if k not in excluded}
                     == {k: v for k, v in after.items() if k not in excluded}, "consumer changed files outside controlled replacement")
        h.mark(case)
    except AssertionError as error:
        failures.append({"case": case, "error": str(error)})
    finally:
        replacement.unlink(missing_ok=True)
        if retained.exists():
            h.pending.unlink()
            retained.rename(h.pending)
        BASE.require(h.call("status") == regular and h.pending.read_bytes() == original,
                     "postread fault restoration changed original obligation")
    return failures


def compatibility(h):
    # Reuse original case bodies with the exact selected source profile's oracle.
    profile = BASE.reservation_refusal_profile(BASE.source_pins(h.repo))
    BASE.exercise_stored_counter_refusals(h, selected=("version-nan", "consumed-nan"),
        nonfinite_reason=profile.get("nonfinite_counter_refusal", "PENDING_OBSERVATION_COUNTERS"))
    before = h.state()
    resumed = h.call("resume", {"currentness": "UNRESOLVED", "measured_epoch": None})
    after = h.held(resumed)
    BASE.successor(before, after)
    BASE.require(all(type(row["version"]) is int and type(row["consumed_version"]) is int
                     for row in after["observations"].values()), "actual successor lost integer counters")
    snapshot = h.snapshot()
    BASE.require(h.call("status", mode="status-guard") == resumed and snapshot == h.snapshot(),
                 "actual integer successor lost four-file read domain")
    h.mark("actual-integer-successor-retains-original-four-file-read-guard")


def top_level_counter_controls(h, regular):
    """A malformed finite counter cannot supply a decision or be overwritten.

    The initial empty-state pair is a fresh fixed-source successor to the
    retained first negative-counter witness. Remaining cases change one field
    in a real unresolved-resume state. No signal hook or native event runs.
    """
    profile = BASE.reservation_refusal_profile(BASE.source_pins(h.repo))
    # The exact combined profiles reject nonfinite JSON tokens before shape.
    # Donor profiles retain their original deferred-rejection precedence.
    immediate_nonfinite = profile.get("nonfinite_counter_refusal") == "PENDING_STATE_JSON_CONSTANT"
    original = h.pending.read_bytes()
    state = json.loads(original)
    empty = dict(state)
    empty.update(revision=0, signals=0, unresolved_signal_version=0,
                 observations={})
    empty_wire = (json.dumps(empty, indent=2, sort_keys=True) + "\n").encode()
    try:
        h.pending.write_bytes(empty_wire)
        before = h.snapshot()
        value = h.call("status", mode="status-guard")
        BASE.require(value["decision"] == "NO_PENDING_AUDIT" and before == h.snapshot(),
                     "genuine empty counters did not retain read-only empty status")
        h.mark("top-counter-empty-zero-status")
        wire = empty_wire.replace(b'"unresolved_signal_version": 0',
                                  b'"unresolved_signal_version": -1', 1)
        BASE.require(wire != empty_wire, "empty negative counter was not substituted")
        h.pending.write_bytes(wire)
        (h.evidence / "top-counter-empty-negative.input").write_bytes(wire)
        before = h.snapshot()
        value = h.call("status", expected_exit=2)
        BASE.require(value["status"] == "PENDING_OPERATION_REFUSED"
                     and value["reason"] == "PENDING_STATE_COUNTERS" and "decision" not in value,
                     "negative empty counter reached a pending decision")
        BASE.require(before == h.snapshot(), "negative empty counter refusal changed store")
        h.mark("top-counter-empty-negative-refuses-status")
    finally:
        h.pending.write_bytes(original)

    for key in ("revision", "signals", "unresolved_signal_version"):
        prefix = ('"' + key + '": ').encode()
        needle = prefix + json.dumps(state[key]).encode()
        BASE.require(original.count(needle) == 1, "top-level field is not unique")
        for integer in (0, 1):
            try:
                h.pending.write_bytes(original.replace(needle, prefix + str(integer).encode(), 1))
                before = h.snapshot()
                value = h.call("status", mode="status-guard")
                h.held(value)
                BASE.require(before == h.snapshot(), "valid integer status changed store")
                h.mark("top-counter-" + key + "-integer-" + str(integer) + "-held")
            finally:
                h.pending.write_bytes(original)
        tokens = [("negative", b"-1"), ("boolean", b"true"),
                  ("fraction", b"0.5"), ("string", b'"0"'), ("null", b"null"),
                  ("nan", b"NaN"), ("overflow", b"1e999")]
        for name, token in tokens:
            if immediate_nonfinite and name in ("nan", "overflow"):
                reason = ("PENDING_STATE_JSON_CONSTANT" if name == "nan"
                          else "PENDING_STATE_JSON_NUMBER")
            else:
                reason = ("PENDING_STATE_SHAPE" if key == "revision" and name != "negative"
                          else "PENDING_STATE_JSON_CONSTANT" if name == "nan"
                          else "PENDING_STATE_JSON_NUMBER" if name == "overflow"
                          else "PENDING_STATE_COUNTERS")
            wire = original.replace(needle, prefix + token, 1)
            changed = json.loads(wire)
            BASE.require({k: v for k, v in changed.items() if k != key}
                         == {k: v for k, v in state.items() if k != key},
                         "counter mutation changed another field")
            for action in ("status", "resume"):
                case = "top-counter-" + key + "-" + name + "-refuses-" + action
                try:
                    h.pending.write_bytes(wire)
                    (h.evidence / (case + ".input")).write_bytes(wire)
                    before = h.snapshot()
                    value = h.call(action, {"currentness": "UNRESOLVED", "measured_epoch": None}
                                   if action == "resume" else None, expected_exit=2)
                    BASE.require(value["status"] == "PENDING_OPERATION_REFUSED"
                                 and value["reason"] == reason and "decision" not in value,
                                 case + ": malformed state yielded wrong refusal")
                    BASE.require(before == h.snapshot(), case + ": refusal changed store")
                    h.mark(case)
                finally:
                    h.pending.write_bytes(original)
    before = h.snapshot()
    BASE.require(h.call("status", mode="status-guard") == regular and before == h.snapshot()
                 and h.pending.read_bytes() == original, "original unresolved state was not retained")
    h.mark("top-counter-original-unresolved-state-retained")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=ROOT)
    parser.add_argument("--evidence-dir", type=Path)
    parser.add_argument("--include-existing-counter-controls", action="store_true")
    parser.add_argument("--top-level-counter-controls-only", action="store_true")
    args = parser.parse_args()
    repo = args.repo_root.resolve(strict=True)
    evidence = args.evidence_dir.absolute() if args.evidence_dir else Path(tempfile.mkdtemp(prefix="pending-loader-"))
    if args.evidence_dir:
        evidence.mkdir(parents=True, exist_ok=False)
    h = RecordedHarness(repo, evidence)
    pins = BASE.source_pins(repo)
    report = {"schema": "constructed.pending-stored-loader-qualification.v1", "authority": "NONE",
              "host_activation_proven": False, "native_JOIN_consumption": "UNPROVED",
              "native_lifecycle": "NOT_CLAIMED", "source_sha256": pins, "evidence_dir": str(evidence),
              "selection": "top-level-counter-controls-only" if args.top_level_counter_controls_only else "stored-loader-and-top-level-counters",
              "include_existing_counter_controls": args.include_existing_counter_controls,
              "failures": []}
    try:
        tree = ast.parse((repo / BASE.PEER / "compaction-source-owner-codex-app.py").read_bytes())
        selections = [ast.literal_eval(node.value) for node in tree.body if isinstance(node, ast.Assign)
                      and any(isinstance(target, ast.Name) and target.id == "NONPROTECTED_SELECTION_PIN" for target in node.targets)]
        BASE.require(selections == [None], "original absent native selection required")
        regular = setup(h)
        if not args.top_level_counter_controls_only:
            report["failures"] = exercise_new_controls(h, regular)
        top_level_counter_controls(h, regular)
        if args.include_existing_counter_controls:
            compatibility(h)
        BASE.require(BASE.source_pins(repo) == pins, "actual source owners changed")
        report["result"] = "FAIL" if report["failures"] else "PASS"
    except Exception as error:
        report.update(result="FAIL", error=str(error), traceback=traceback.format_exc())
    finally:
        report.update(controls=h.controls, process_count=len(h.records), source_unchanged=BASE.source_pins(repo) == pins)
        (evidence / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))
    return 0 if report["result"] == "PASS" else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--worker":
        BASE.require(sys.argv[2] == "pending-postread-replacement", "unsupported loader worker")
        raise SystemExit(replacement_worker(*sys.argv[3:]))
    raise SystemExit(main())
