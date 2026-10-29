#!/usr/bin/env python3
"""Ordinary evidence-input custody at the actual disposable mutation sink.

The startup instrument schedules one local path replacement at acquisition;
it is never packaged and grants no native or external authority.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import tempfile

from distributed_generation_fence import Fixture, PREIMAGE, CANDIDATE, require


INSTRUMENT = '''import os
from pathlib import Path
watched = os.environ["MUTATION_CUSTODY_INPUT"]
kind = os.environ["MUTATION_CUSTODY_SWAP"]
marker = Path(os.environ["MUTATION_CUSTODY_MARKER"])
original_read = Path.read_bytes
original_open = os.open
used = False
def swap(path):
    global used
    if used or os.fspath(path) != watched or kind == "none":
        return
    used = True
    os.rename(watched, watched + ".original")
    if kind == "symlink":
        os.symlink(watched + ".foreign", watched)
    elif kind == "regular":
        Path(watched).write_bytes(b"SUBSTITUTED\\n")
    elif kind == "fifo":
        os.mkfifo(watched)
    marker.write_text(kind)
def read(path):
    swap(path)
    return original_read(path)
def acquire(path, flags, *args, **kwargs):
    swap(path)
    return original_open(path, flags, *args, **kwargs)
Path.read_bytes = read
os.open = acquire
if original_open in os.supports_dir_fd:
    os.supports_dir_fd.add(acquire)
'''


def run_case(base, role, kind):
    fixture = Fixture(base)
    # This family tests ordinary v2 inputs, retaining controller currentness.
    fixture.fence_path.unlink()
    preimage = fixture.repo / "artifacts/preimage.bin"
    preimage.write_bytes(PREIMAGE)
    inputs = {"preimage": preimage, "candidate": fixture.candidate}
    command = fixture.command()
    command[command.index("--preimage") + 1] = str(preimage)
    if role in {"region", "replacement"}:
        phase = fixture.run / "phases/phase-1.md"
        phase.write_text(phase.read_text().replace('"operation":"replace"',
                                                  '"operation":"patch"'))
        inputs["region"] = fixture.repo / "artifacts/region.bin"
        inputs["replacement"] = fixture.repo / "artifacts/replacement.bin"
        inputs["region"].write_bytes(PREIMAGE)
        inputs["replacement"].write_bytes(CANDIDATE)
        command = command[:command.index("--preimage")] + [
            "--region", str(inputs["region"]), "--replacement",
            str(inputs["replacement"]), "--offset", "0"]
    watched = inputs[role]
    # An otherwise valid preimage behind a substituted path must also refuse.
    Path(str(watched) + ".foreign").write_bytes(
        PREIMAGE if role in {"preimage", "region"} else b"SUBSTITUTED\n")
    instrument = fixture.base / "instrument"
    instrument.mkdir()
    (instrument / "sitecustomize.py").write_text(INSTRUMENT)
    marker = fixture.base / "swap-fired"
    fixture.env.update(PYTHONPATH=str(instrument),
                       MUTATION_CUSTODY_INPUT=str(watched),
                       MUTATION_CUSTODY_SWAP=kind,
                       MUTATION_CUSTODY_MARKER=str(marker))
    result = fixture.run_command(command, check=False, timeout=10)
    (base / "stdout.json").write_text(result.stdout)
    (base / "stderr.txt").write_text(result.stderr)
    (base / "exit.txt").write_text(str(result.returncode) + "\n")
    payload = json.loads(result.stdout)
    target = (fixture.repo / "target").read_bytes()
    if kind == "none":
        require(result.returncode == 0 and payload["status"] == "COMMITTED"
                and target == CANDIDATE, "unchanged ordinary input did not commit")
    else:
        require(marker.exists(), "scheduled acquisition replacement never fired")
        require(result.returncode == 64 and payload["status"] == "REJECTED_NO_MUTATION"
                and target == PREIMAGE,
                f"unsafe {role}/{kind} reached effects: {payload['status']}, {target!r}")
        require(not (fixture.run / "mutation-transactions").exists(),
                "unsafe evidence created transaction effects")
    require(payload["schema"] == "implementaudit.observation_bound_mutation.v2",
            "ordinary result schema changed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    cases = [(role, kind) for role in ("candidate", "preimage")
             for kind in ("none", "symlink", "regular", "missing")]
    cases += [(role, kind) for role in ("region", "replacement")
              for kind in ("none", "symlink")]
    if hasattr(os, "mkfifo"):
        cases += [(role, "fifo") for role in ("candidate", "preimage")]
    names = {f"{role}-{kind}": (role, kind) for role, kind in cases}
    parser.add_argument("--case", choices=names)
    parser.add_argument("--evidence-dir", type=Path)
    args = parser.parse_args()
    if os.name == "nt":
        print("ordinary-input-custody: SKIP POSIX replacement schedule")
        return
    temporary = tempfile.TemporaryDirectory(prefix="ordinary-input-")
    root = Path(temporary.name)
    if args.evidence_dir:
        args.evidence_dir.mkdir(parents=True, exist_ok=True)
    try:
        selected = [args.case] if args.case else names
        for name in selected:
            run_case(root / name, *names[name])
            print(f"ordinary-input-custody {name}: PASS", flush=True)
        print(f"ordinary-input-custody: {len(selected)}/{len(selected)} PASS")
    finally:
        if args.evidence_dir:
            shutil.copytree(root, args.evidence_dir / root.name, symlinks=True,
                            ignore=lambda path, names: [name for name in names
                                if Path(path, name).is_fifo()])
        temporary.cleanup()


if __name__ == "__main__":
    main()
