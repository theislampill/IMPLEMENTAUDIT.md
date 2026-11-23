#!/usr/bin/env python3
"""Receive a selective projection before reopening ordinary governed phases."""

import argparse
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


MAX_BYTES = 1024 * 1024
PHASE = re.compile(r"phase-([1-9][0-9]*)")
SHA256 = re.compile(r"[a-f0-9]{64}")


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return sha256(data).hexdigest()


def read(path):
    path = path.absolute()
    require(path.resolve(strict=True) == path and path.is_file()
            and not getattr(path.lstat(), "st_file_attributes", 0) & 0x400,
            f"unsafe evidence path: {path.name}")
    with path.open("rb") as stream:
        raw = stream.read(MAX_BYTES + 1)
    require(len(raw) <= MAX_BYTES, f"oversized evidence: {path.name}")
    return raw


def object_pairs(pairs):
    obj = dict(pairs)
    require(len(obj) == len(pairs), "duplicate JSON member")
    return obj


def invalid_number(value):
    raise ValueError(f"non-JSON number: {value}")


def decode(raw):
    return json.loads(raw, object_pairs_hook=object_pairs, parse_constant=invalid_number)


def encoded(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False) + "\n").encode()


def beneath(root, name):
    require(type(name) is str and name and not any(s in ("", ".", "..") for s in name.split("/"))
            and ":" not in name and "\\" not in name, "unsafe run input path")
    path = root / name
    require(path.is_relative_to(root), "input is outside the selected run")
    return path


def run(command, cwd):
    return subprocess.run(command, cwd=cwd, capture_output=True, timeout=60)


def verify_current(repo, claim, bash, controller, receipt):
    result = run([bash, str(claim), "--require-current-continuity", controller], repo)
    require(result.returncode == 0 and result.stdout.decode().strip() == receipt,
            "expected current re-entry receipt is not live")


def verify_owner(repo, tool):
    result = run(["git", "show", "HEAD:" + tool.relative_to(repo).as_posix()], repo)
    require(result.returncode == 0 and result.stdout == read(tool), "selected tool differs from HEAD")


def reopen_phase(text):
    require(len(re.findall(r"(?m)^Status: done$", text)) == 1,
            "affected phase does not have one done status")
    text = re.sub(r"(?m)^Status: done$", "Status: open", text, count=1)
    acceptance = re.compile(r"(?ms)(^## Acceptance criteria\s*\n)(.*?)(?=^## |\Z)")
    require(len(acceptance.findall(text)) == 1, "affected phase acceptance block is ambiguous")
    return acceptance.sub(lambda m: m[1] + re.sub(r"(?m)^- \[x\]", "- [ ]", m[2]), text)


def roadmap_rows(text):
    lines = text.splitlines(keepends=True)
    rows = {}
    seen = active = False
    for i, row in enumerate(lines):
        if row.rstrip() == "| # | Phase | Depends on | Status |":
            require(not seen, "ambiguous roadmap phase table")
            seen = active = True
        elif active and not row.startswith("|"):
            active = False
        elif active:
            values = row.strip().split("|")
            if len(values) != 6 or not re.fullmatch(r"[1-9][0-9]*", values[1].strip()):
                continue
            phase = "phase-" + values[1].strip()
            require(phase not in rows, "duplicate roadmap phase")
            rows[phase] = i, values[-2].strip()
    return lines, rows


def reopen_roadmap(text, phases):
    lines, rows = roadmap_rows(text)
    for phase in phases:
        i, status = rows[phase]
        require(status == "done", "affected roadmap row is not done")
        lines[i] = re.sub(r"[ \t]*done[ \t]*\|([ \t]*\r?\n?)$", r" open |\1", lines[i], count=1)
    return "".join(lines)


def replace(path, raw):
    fd, temporary = tempfile.mkstemp(prefix=".reentry-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def reopen(args):
    repo = Path.cwd().resolve()
    bash = shutil.which("bash")
    require(bash is not None, "Bash is unavailable")
    bash = str(Path(bash).resolve(strict=True))
    root = beneath(repo, args.run_root)
    require(root.parent == repo / ".IMPLEMENTAUDIT/runs", "expected an ordinary claimed run root")
    claim_tool = repo / "skills/implementaudit/scripts/claim-run.sh"
    compiler = repo / "skills/implementaudit/scripts/compile-work-graph.py"
    for tool in (claim_tool, compiler):
        verify_owner(repo, tool)

    inputs = {}
    def observe(name):
        path = beneath(root, name)
        raw = read(path)
        inputs[path] = raw
        return raw

    claim = dict(line.split("=", 1) for line in observe(".claimed").decode().splitlines())
    require(claim.get("run_root") == args.run_root and claim.get("repo_root") == repo.as_posix(),
            "claim does not bind the selected run")
    require(re.fullmatch(r"[a-z0-9][a-z0-9-]{0,47}", args.controller)
            and observe(".controller").decode().strip() == "controller_id="+args.controller,
            "run controller differs from the supplied identity")
    binding = run(["git", "cat-file", "blob", "refs/implementaudit/controllers/"+args.controller], repo)
    require(binding.returncode == 0 and binding.stdout.decode().rstrip("\n").split("\t") ==
            ["implementaudit.controller-current.v1", args.controller, claim["claim_id"], root.as_posix()],
            "current controller does not own this run root")
    state = observe("STATE.md").decode()
    roadmap = observe("ROADMAP.md").decode()
    baseline_raw = observe("evidence/reentry-baseline.json")
    require(re.findall(r"(?m)^Re-entry baseline SHA-256: ([a-f0-9]{64})$", state) == [digest(baseline_raw)],
            "current STATE does not bind the exact re-entry baseline")
    baseline = decode(baseline_raw)
    require(type(baseline) is dict and set(baseline) == {"schema", "phases"}
            and baseline["schema"] == "implementaudit.phase-reentry-baseline.v1"
            and type(baseline["phases"]) is dict and 1 <= len(baseline["phases"]) <= 64,
            "invalid re-entry baseline")
    _, roadmap_phases = roadmap_rows(roadmap)
    require({p for p, (_, status) in roadmap_phases.items() if status == "done"} == set(baseline["phases"]),
            "baseline does not cover the completed roadmap phases")
    consumers, phases, changed = [], {}, set()
    for phase, row in sorted(baseline["phases"].items()):
        require(PHASE.fullmatch(phase) and type(row) is dict and set(row) == {"phase_sha256", "inputs"}
                and type(row["inputs"]) is dict and 1 <= len(row["inputs"]) <= 64, "invalid phase binding")
        name = f"phases/{phase}.md"
        phases[phase] = observe(name)
        require(digest(phases[phase]) == row["phase_sha256"], "phase changed from its re-entry baseline")
        for name, expected in sorted(row["inputs"].items()):
            require(name.startswith("inputs/") and type(expected) is str and SHA256.fullmatch(expected),
                    "invalid bound phase input")
            if digest(observe(name)) != expected:
                changed.add(name)
        consumers.append({"id":phase,"kind":"TEST","paths":sorted(row["inputs"]),"impact":"KNOWN"})

    request_raw = observe("evidence/reentry-request.json")
    request = decode(request_raw)
    require(type(request) is dict and request.get("invalidation") == {
        "changed_paths": sorted(changed), "change_kind":"SOURCE", "consumers":consumers
    }, "request differs from actual changed files or anchored consumers")
    verify_current(repo, claim_tool, bash, args.controller, args.receipt)
    with tempfile.TemporaryDirectory(prefix="phase-reentry-input-") as directory:
        captured = Path(directory) / "request.json"
        captured.write_bytes(request_raw)
        result = run([sys.executable, "-B", str(compiler), "--native-a-g", str(captured)], repo)
    require(result.returncode == 0 and not result.stderr, "exact compiler refused the request")
    verdict = decode(result.stdout)
    require(encoded(decode(read(Path(args.projection)))) == encoded(verdict),
            "projection differs from the exact compiler result")
    invalidation = verdict["invalidation"]
    affected = invalidation["invalidated"]
    require(affected and not invalidation["blocked"] and not invalidation["global_replay"],
            "compiler supplied no representable selective reopening")
    changes = {root/"ROADMAP.md":reopen_roadmap(roadmap, affected).encode()}
    for phase in affected:
        changes[root/f"phases/{phase}.md"] = reopen_phase(phases[phase].decode()).encode()

    lock = root/"evidence/.phase-reentry.lock"
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    owned_lock = os.fstat(fd)
    try:
        require(all(read(path) == raw for path, raw in inputs.items()), "run inputs changed before re-entry")
        verify_owner(repo, compiler)
        verify_owner(repo, claim_tool)
        verify_current(repo, claim_tool, bash, args.controller, args.receipt)
        event = "phase-reentry-" + digest(args.receipt.encode())[:24]
        journal = root/f"evidence/{event}.json"
        with journal.open("xb") as f:
            f.write(encoded({"receipt":args.receipt,"request_sha256":digest(request_raw),"affected":affected,
                "prior":{str(p.relative_to(root)):inputs[p].decode() for p in changes},
                "next_sha256":{str(p.relative_to(root)):digest(b) for p,b in changes.items()}}))
            f.flush()
            os.fsync(f.fileno())
        stopped = run([bash, str(claim_tool), "--invalidate-continuity", args.controller,
                       "--boundary", "manual-resume", "--event", event], repo)
        require(stopped.returncode == 0 and stopped.stdout.strip(), "continuity invalidation unresolved")
        check = run([bash, str(claim_tool), "--require-current-continuity", args.controller], repo)
        require(check.returncode == 1 and not check.stdout, "old continuity remained usable")
        for path, content in changes.items():
            require(read(path)==inputs[path], "phase control changed after invalidation")
            replace(path, content)
        require(all(read(path)==raw for path,raw in changes.items()), "reopened phase readback differs")
        print(encoded({"status":"REOPENED","affected":affected,"next":"Replan and establish fresh currentness.",
                       "phase_dispatch_authorized":False}).decode(),end="")
    finally:
        os.close(fd)
        if os.path.samestat(lock.lstat(), owned_lock):
            lock.unlink()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for name in ("run-root","controller","receipt","projection"):
        parser.add_argument("--"+name,required=True)
    try:
        reopen(parser.parse_args())
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        print(f"phase-reentry: {exc}",file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
