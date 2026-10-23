#!/usr/bin/env python3
"""R0037 TY records through the real run-root owner; no host-Stop claim."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "skills/implementaudit/scripts/validate-run-root.sh"


def inventory(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file() and not p.is_symlink()}


def write_case(root, changes=None, *, omit=(), suffix="", phase=True, legacy_andon=False):
    shutil.copytree(ROOT / "fixtures/run-root-example", root)
    values = {
        "Run root": str(root), "Phase": "1", "Status": "IN_PHASE",
        "Audit object state": "open", "Owner/source": "issue207/211 governor",
        "Last check": "Focused input validation completed at checkpoint C1",
        "Next action": "Run the remaining evidence-consumption control",
        "Authorization state": "Portable read-only qualification authorized by task grant",
        "Re-entry condition": "Re-read checkpoint C1 and verify current inputs before continuation",
        "Current checkpoint": "C1 input-validation boundary",
        "Last completed step": "Smoke A input validation",
    }
    values.update(changes or {})
    rows = [f"| {key} | {value} |" for key, value in values.items() if key not in omit]
    (root / "STATE.md").write_text(
        "# State\n\n## Current phase\n\n| Field | Value |\n|---|---|\n"
        + "\n".join(rows)
        + "\n\n## Andon log\n\n"
          "| # | Occ | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome |\n"
          "|---|---|---|---|---|---|---|---|\n"
        + suffix, encoding="utf-8")
    if legacy_andon:
        state = root / "STATE.md"
        state.write_text(state.read_text().replace("| # | Occ | Phase | Class |", "| # | Phase | Class |"))
    if not phase:
        shutil.rmtree(root / "phases")
        (root / "ROADMAP.md").write_text("# Roadmap\nIntake decision remains open.\n")
    return root


def main():
    cases = []
    # A valid current progress record must pass; missing mode is an explicit
    # feature-gap assertion on the old owner, never an accidental import error.
    cases.append(("TY5-progress", True, {}, {}, ""))
    pause = {"Status": "PAUSED", "Pause reason": "Clarification of target dataset is required",
             "Resume point": "Input selection before processing",
             "Pause trigger": "clarification", "Next action": "Ask the owner which dataset is intended"}
    cases.append(("TY1-required-clarification", True, pause, {}, ""))
    cases.append(("TY2-owner-authority-wait", True, pause | {
        "Pause trigger": "owner-authority", "Pause reason": "Publication authority is absent",
        "Authorization state": "Publication not authorized; no effect performed",
        "Next action": "Request the exact publication grant from the owner"}, {}, ""))
    blocked = {"Status": "BLOCKED", "Blocker": "external-job-27 has no terminal output",
               "Containment": "No dependent effect or completion claim is admitted",
               "Next probe": "Read external-job-27 terminal status after its owner update",
               "Next action": "Inspect external-job-27 after the owner update"}
    cases.append(("TY3-external-dependency", True, blocked, {}, ""))
    pause_record = ("\nIMPLEMENTAUDIT_PAUSE\nPhase: 1\nStatus: paused at boundary\n"
                    "Last completed step: Smoke A input validation\nSTATE.md: updated\n")
    cases.append(("TY4-user-pause", True, pause | {"Pause trigger": "user-interruption", "Pause phase context": "IN_PROGRESS"}, {}, pause_record))
    interruption = {"Status": "INTERRUPTED", "Stop source": "owner-event-17",
                    "Interruption point": "Smoke A input validation", "Interruption log": "1",
                    "Next action": "Wait for owner-event-17 continuation authorization"}
    log = "| 1 | i17 | 1 | input-contract | owner-event-17 at Smoke A input validation | Hold affected work | checkpoint C1 | open (rerun pending) |\n"
    cases.append(("TY4-owner-interruption", True, interruption, {}, log))
    intake = {"Phase": "intake", "Status": "open", "Pending decision": "Which of two input datasets is intended",
              "Last check": "not-yet-run: input dataset identity needs the owner answer",
              "Next action": "Ask the owner to select the input dataset"}
    cases.append(("TY5-open-intake", True, intake, {"phase": False}, ""))
    cases.append(("TY5-ready-dispatch", True, {"Status": "READY_TO_DISPATCH", "Pending decision": "Dispatch the reviewed phase1 verifier"}, {}, ""))
    for field in ("Last check", "Next action", "Owner/source", "Authorization state", "Re-entry condition",
                  "Current checkpoint", "Last completed step", "Audit object state", "Phase"):
        cases.append(("TY6-missing-" + field, False, {}, {"omit": (field,)}, ""))
    for value in ("", "none", "pending", "TODO", "run it", "continue", "wait for it"):
        cases.append(("TY6-vague-next-" + repr(value), False, {"Next action": value}, {}, ""))
    cases.extend([
        ("terminal-object-not-yield", False, {"Audit object state": "terminal verified closure"}, {}, ""),
        ("done-is-not-yield", False, {"Status": "DONE"}, {}, ""),
        ("bare-paused", False, {"Status": "PAUSED"}, {}, ""),
        ("bare-blocked", False, {"Status": "BLOCKED"}, {}, ""),
        ("bare-interrupted", False, {"Status": "INTERRUPTED"}, {}, ""),
        ("open-without-decision", False, {"Status": "open"}, {}, ""),
        ("ready-without-decision", False, {"Status": "READY_TO_DISPATCH"}, {}, ""),
        ("user-pause-record-missing", False, pause | {"Pause trigger": "user-interruption", "Pause phase context": "IN_PROGRESS"}, {}, ""),
        ("user-pause-foreign-phase", False, pause | {"Pause trigger": "user-interruption", "Pause phase context": "IN_PROGRESS"}, {}, pause_record.replace("Phase: 1", "Phase: 2")),
        ("user-pause-state-not-updated", False, pause | {"Pause trigger": "user-interruption", "Pause phase context": "IN_PROGRESS"}, {}, pause_record.replace("STATE.md: updated", "STATE.md: not updated")),
        ("interruption-log-absent", False, interruption, {}, ""),
        ("interruption-log-foreign", False, interruption, {}, log.replace("owner-event-17", "owner-event-18")),
        ("blocker-no-containment", False, blocked, {"omit": ("Containment",)}, ""),
        ("blocker-no-probe", False, blocked, {"omit": ("Next probe",)}, ""),
        ("missing-phase-spec", False, {}, {"phase": False}, ""),
    ])
    # Independent review found these counterexamples after the first 45 passed.
    cases.extend([
        ("interruption-prefix-is-foreign", False, interruption | {"Stop source": "owner-event-1"}, {}, log),
        ("interruption-suffix-is-foreign", False, interruption | {"Stop source": "event-17"}, {}, log),
        ("interruption-phase-is-foreign", False, interruption, {}, log.replace("| i17 | 1 |", "| i17 | 2 |")),
        ("interruption-duplicate-row", False, interruption, {}, log + log),
        ("interruption-legacy-row", True, interruption, {"legacy_andon": True}, log.replace("| 1 | i17 |", "| 1 |")),
        ("concrete-check-action", True, {"Next action": "Check external-job-27 terminal status"}, {}, ""),
        ("concrete-execute-action", True, {"Next action": "Execute tests/run-root-validation.test.sh and inspect its exit status"}, {}, ""),
        ("concrete-unfamiliar-action", True, {"Next action": "Recalculate case-27 checksum from its retained bytes"}, {}, ""),
        ("unresolved-command-template", False, {"Next action": "Run <command>"}, {}, ""),
        ("unresolved-target-template", False, {"Next action": "Check [target]"}, {}, ""),
        ("concrete-indexed-action", True, {"Next action": "Inspect external-job-27 JSON field records[0].id before resuming phase 1"}, {}, ""),
        ("concrete-parametrized-test-action", True, {"Next action": "Run pytest tests/test_config.py::test_load[linux] and inspect its exit status"}, {}, ""),
        ("concrete-braced-shell-action", True, {"Next action": "Inspect the output from printf '%s' {a,b} in case 27"}, {}, ""),
        ("unresolved-braced-command-template", False, {"Next action": "Run {command}"}, {}, ""),
        ("quoted-phase-identity", True, {"Phase": "`1`"}, {}, ""),
        ("pause-conflicting-last-step", False, pause | {"Pause trigger": "user-interruption", "Pause phase context": "IN_PROGRESS"}, {},
         pause_record.replace("Last completed step: Smoke A input validation", "Last completed step: Step 11 phase verification")),
        ("pause-without-redundant-table-step", True, pause | {"Pause trigger": "user-interruption", "Pause phase context": "IN_PROGRESS"},
         {"omit": ("Last completed step",)}, pause_record),
    ])
    outside = pause | {"Pause trigger": "user-interruption", "Pause phase context": "OUTSIDE_PHASE",
                       "Phase": "intake", "Last check": "not-yet-run: owner paused before dispatch",
                       "Pause reason": "Owner paused intake before selecting the target",
                       "Resume point": "Resume input selection after the owner returns"}
    cases.extend([
        ("user-pause-before-intake-dispatch", True, outside,
         {"phase": False, "omit": ("Current checkpoint", "Last completed step")}, ""),
        ("user-pause-planned-numbered-phase", True, outside | {"Phase": "1"},
         {"omit": ("Current checkpoint", "Last completed step")}, ""),
        ("user-pause-outside-phase-rejects-fabricated-marker", False, outside,
         {"phase": False}, pause_record.replace("Phase: 1", "Phase: intake")),
        ("user-pause-context-missing", False, pause | {"Pause trigger": "user-interruption"}, {}, pause_record),
        ("user-pause-context-unknown", False, pause | {"Pause trigger": "user-interruption", "Pause phase context": "UNKNOWN"}, {}, pause_record),
        ("user-pause-active-context-requires-numbered-phase", False, outside | {"Pause phase context": "IN_PROGRESS"},
         {"phase": False}, pause_record.replace("Phase: 1", "Phase: intake")),
    ])
    external = pause | {"Pause trigger": "external-wait", "Pause reason": "external-job-27 terminal output is missing",
                        "Blocker": blocked["Blocker"], "Containment": blocked["Containment"],
                        "Next probe": blocked["Next probe"]}
    cases.append(("external-pause-complete", True, external, {}, ""))
    for missing in ("Blocker", "Containment", "Next probe"):
        cases.append(("external-pause-missing-" + missing, False, external, {"omit": (missing,)}, ""))
    for marker in ("AUDIT_COMPLETE", "IMPLEMENTAUDIT_RUN_COMPLETE", "AUDIT_HANDOFF", "ANDON_HANDOFF"):
        cases.append(("marker-cannot-use-yield-" + marker, False, {}, {}, "\n" + marker + "\n"))
    fifo_count = 0
    with tempfile.TemporaryDirectory(prefix="r37-yield-") as temporary:
        parent = Path(temporary)
        for index, (name, want, changes, kwargs, suffix) in enumerate(cases):
            root = write_case(parent / str(index), changes, suffix=suffix, **kwargs)
            before = inventory(root)
            result = subprocess.run(["bash", str(HELPER), "--nonterminal-yield", str(root)],
                                    text=True, capture_output=True, env=os.environ | {"PYTHONDONTWRITEBYTECODE": "1"})
            if (result.returncode == 0) != want:
                raise AssertionError(f"{name}: expected {'accept' if want else 'refuse'}, exit={result.returncode}\n{result.stdout}{result.stderr}")
            assert inventory(root) == before, f"{name}: read-only validator mutated run artifacts"
            if want:
                assert "nonterminal yield record ok" in result.stdout, f"{name}: generic structural success substituted for yield validation"
            print(f"PASS {name}")
        root = write_case(parent / "duplicate")
        state = root / "STATE.md"
        state.write_text(state.read_text().replace("| Status | IN_PHASE |", "| Status | IN_PHASE |\n| Status | PAUSED |"))
        result = subprocess.run(["bash", str(HELPER), "--nonterminal-yield", str(root)], capture_output=True)
        assert result.returncode != 0, "duplicate current status admitted"
        print("PASS duplicate-current-status")
        root = write_case(parent / "symlink")
        state = root / "STATE.md"
        target = parent / "aliased-state.md"
        state.rename(target)
        state.symlink_to(target)
        result = subprocess.run(["bash", str(HELPER), "--nonterminal-yield", str(root)], capture_output=True)
        assert result.returncode != 0, "symlink STATE admitted"
        print("PASS symlink-state")
        # Schedule a real temporary-record mutation between the two consumer
        # stages. The wrapper selects only the late predicate's argv shape;
        # it grants no authority and is never installed into a user environment.
        race = write_case(parent / "legacy-read-drift")
        wrapper = parent / "bin"
        wrapper.mkdir()
        trigger = parent / "mutation-triggered"
        python = wrapper / "python"
        python.write_text("\n".join([
            "#!" + sys.executable, "from pathlib import Path", "import os,sys",
            "args=[a for a in sys.argv[1:] if a != '-B']",
            "if len(args)==3 and args[0]=='-' and args[1].endswith('/STATE.md'):",
            "    state=Path(args[1])",
            "    state.write_text(state.read_text().replace('## Andon log','## Removed Andon log'))",
            "    Path(" + repr(str(trigger)) + ").write_text('observed')",
            "os.execv(" + repr(sys.executable) + ", [" + repr(sys.executable) + "] + sys.argv[1:])", ""
        ]))
        python.chmod(0o700)
        environment = os.environ | {"PATH": str(wrapper) + os.pathsep + os.environ["PATH"]}
        result = subprocess.run(["bash", str(HELPER), "--nonterminal-yield", str(race)],
                                text=True, capture_output=True, env=environment)
        assert trigger.exists(), "mutation schedule did not reach the late consumer"
        assert result.returncode != 0 and "yield read-set changed" in result.stderr, result.stdout + result.stderr
        print("PASS legacy-structural-yield-read-drift")
        # Both spellings accepted by the actual table consumer must select the
        # same phase member for the before/after read-set comparison.
        phase_wrapper = parent / "phase-bin"
        phase_wrapper.mkdir()
        python = phase_wrapper / "python"
        python.write_text("\n".join([
            "#!" + sys.executable, "from pathlib import Path", "import os,sys,subprocess",
            "args=[a for a in sys.argv[1:] if a != '-B']",
            "if len(args)==3 and args[0]=='-' and args[1].endswith('/STATE.md'):",
            "    result=subprocess.run([sys.executable]+sys.argv[1:])",
            "    phase=Path(args[2])/'phases/phase-1.md'",
            "    phase.write_text(phase.read_text()+'\\nPhase: 99\\n')",
            "    (Path(args[2])/'schedule-triggered').write_text(str(result.returncode))",
            "    raise SystemExit(result.returncode)",
            "os.execv(sys.executable,[sys.executable]+sys.argv[1:])", ""
        ]))
        python.chmod(0o700)
        environment = os.environ | {"PATH": str(phase_wrapper) + os.pathsep + os.environ["PATH"]}
        for label, phase in (("plain", "1"), ("quoted", "`1`")):
            race = write_case(parent / (label + "-phase-read-drift"), {"Phase": phase})
            result = subprocess.run(["bash", str(HELPER), "--nonterminal-yield", str(race)],
                                    text=True, capture_output=True, env=environment)
            assert (race / "schedule-triggered").read_text() == "0", "phase mutation must follow a successful predicate"
            assert result.returncode != 0 and "yield read-set changed" in result.stderr, result.stdout + result.stderr
            print("PASS " + label + "-phase-read-drift")
        # The regular-file lstat can race an actual FIFO replacement. Exercise
        # both new open sites without altering the source being executed.
        if hasattr(os, "mkfifo"):
            for stage, argument_count in (("initial", 4), ("predicate", 3)):
                race = write_case(parent / (stage + "-fifo-race"))
                wrapper = parent / (stage + "-fifo-bin")
                wrapper.mkdir()
                trigger = parent / (stage + "-fifo-trigger.json")
                python = wrapper / "python"
                python.write_text("\n".join([
                    "#!" + sys.executable, "from pathlib import Path", "import os,sys,json",
                    "args=[a for a in sys.argv[1:] if a != '-B']",
                    "if len(args)==" + str(argument_count) + " and args[0]=='-' and args[1].endswith('/STATE.md'):",
                    "    source=sys.stdin.read();state=Path(args[1]);prior_open=os.open",
                    "    trigger=Path(" + repr(str(trigger)) + ")",
                    "    def scheduled_open(path,flags,*rest,**kw):",
                    "        if str(path)==str(state) and not trigger.exists():",
                    "            state.rename(state.with_suffix('.regular-preimage'))",
                    "            os.mkfifo(state)",
                    "            trigger.write_text(json.dumps({'scheduled':True,'nonblock':bool(flags & getattr(os,'O_NONBLOCK',0))}))",
                    "        return prior_open(path,flags,*rest,**kw)",
                    "    os.open=scheduled_open;sys.argv=args",
                    "    exec(compile(source,'<unchanged-yield-consumer>','exec'),{'__name__':'__main__'})",
                    "else:",
                    "    os.execv(sys.executable,[sys.executable]+sys.argv[1:])", ""
                ]))
                python.chmod(0o700)
                process = subprocess.Popen(["bash", str(HELPER), "--nonterminal-yield", str(race)],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True,
                    env=os.environ | {"PATH": str(wrapper) + os.pathsep + os.environ["PATH"]})
                try:
                    stdout, stderr = process.communicate(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.communicate()
                    raise AssertionError(stage + " FIFO replacement blocked the read instead of refusing")
                observed = json.loads(trigger.read_text())
                assert observed == {"scheduled": True, "nonblock": True}, observed
                expected = "yield read-set unavailable" if stage == "initial" else "nonterminal yield refused"
                assert process.returncode != 0 and expected in stderr and "nonregular" in stderr, stdout + stderr
                fifo_count += 1
                print("PASS " + stage + "-fifo-replacement-refused")
        else:
            print("SKIP FIFO race controls: host has no mkfifo")
    print(f"nonterminal-yield-cases: ok ({len(cases) + 5 + fifo_count} record controls; native Stop UNVERIFIED)")


if __name__ == "__main__":
    main()
