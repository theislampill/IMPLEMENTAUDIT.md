#!/usr/bin/env python3
"""Fixed, declared receiver-controlled fixture inputs; no task decisions."""
import argparse
import hashlib
import json
from pathlib import Path
import stat

p = argparse.ArgumentParser()
p.add_argument("operation", choices=("dependency", "candidate"))
a = p.parse_args()
if a.operation == "dependency":
    path, before, after = Path("incoming/greeting.txt"), b"Hi", b"Hello"
else:
    path = Path("subject/app.txt")
    before, after = b"Hello\nstatus=ready\n", b"Hello\nstatus=ready"
for item in (path, path.parent):
    if item.is_symlink():
        raise SystemExit("fixture input path is aliased")
s = path.stat()
if not stat.S_ISREG(s.st_mode) or s.st_nlink != 1 or path.read_bytes() != before:
    raise SystemExit("fixture input exact preimage differs")
path.write_bytes(after)
if path.read_bytes() != after:
    raise SystemExit("fixture input postimage differs")
def ident(raw):
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
print(json.dumps({"operation": a.operation, "path": str(path),
                  "preimage": ident(before), "postimage": ident(after),
                  "provenance": "explicit receiver-controlled fixture input",
                  "task_decision": False}, sort_keys=True, separators=(",", ":")))
