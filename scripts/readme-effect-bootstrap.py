#!/usr/bin/env python3
"""One fixed private README generation operation inside the existing launcher.

This is not a configurable executor. The enclosing VerifierTaskSession owns
the namespace, resources, process group, timeout and retained outer streams.
"""
import base64
import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile

PROGRAM = "scripts/generate-readme-diagrams.sh"
PROGRAM_SHA256 = "607bc8c367989af45dedefcf3a3720af89d88c72d2cf58c0e779b27fade949f5"
DIAGRAMS = tuple("docs/diagrams/" + name + ".mmd" for name in (
    "tooling-architecture", "invocation-modes", "execution-spine"))
SUBJECTS = (PROGRAM, "README.md", *DIAGRAMS)
MAX_ARTIFACT = 512 * 1024
MAX_STREAM = 16 * 1024
MAX_FRAME = 1024 * 1024
MAGIC = b"R0035_README_EFFECT_V1\n"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encode(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False).encode("utf-8") + b"\n"


def read_output(path):
    """Read the fixed ordinary output only after its exact writer returned."""
    def identity(info):
        return (info.st_dev, info.st_ino, info.st_mode, info.st_nlink,
                info.st_size, info.st_mtime_ns, info.st_ctime_ns)
    before = path.lstat()
    if (not stat.S_ISREG(before.st_mode) or before.st_nlink != 1
            or stat.S_IMODE(before.st_mode) != 0o600 or before.st_size > MAX_ARTIFACT):
        raise ValueError("unsupported generated README output")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    try:
        if identity(os.fstat(fd)) != identity(before) or os.listxattr(fd):
            raise ValueError("generated README identity changed")
        with os.fdopen(fd, "rb", closefd=False) as stream:
            data = stream.read(MAX_ARTIFACT + 1)
        if (len(data) > MAX_ARTIFACT or identity(os.fstat(fd)) != identity(before)
                or identity(path.lstat()) != identity(before)):
            raise ValueError("generated README changed during capture")
    finally:
        os.close(fd)
    return dict(path="README.md", mode=0o600, bytes=len(data), sha256=digest(data),
                data=base64.b64encode(data).decode("ascii"))


def produce():
    if sys.argv[1:] != ["--produce"] or Path.cwd() != Path("/work"):
        raise ValueError("bootstrap is only an existing-launcher-owned fixed operation")
    # The owner already acquired and bounded these immutable mounted inputs.
    # Copy only these five names; no directory enumeration or host write bind.
    captured = {}
    for name in SUBJECTS:
        maximum = 256 * 1024 if name == "README.md" else 64 * 1024
        with (Path("/work") / name).open("rb") as stream:
            data = stream.read(maximum + 1)
        if len(data) > maximum:
            raise ValueError("private projection input bound exceeded")
        captured[name] = data
    if digest(captured[PROGRAM]) != PROGRAM_SHA256:
        raise ValueError("unsupported original generator")
    with tempfile.TemporaryDirectory(prefix="readme-effect-", dir="/tmp") as temporary:
        root = Path(temporary)
        for name, data in captured.items():
            path = root / name
            path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
            with path.open("xb") as stream:
                stream.write(data)
            path.chmod(0o600)
        observed = subprocess.run(["/usr/bin/bash", PROGRAM], cwd=root,
                                  stdin=subprocess.DEVNULL, capture_output=True,
                                  close_fds=True)
        if len(observed.stdout) > MAX_STREAM or len(observed.stderr) > MAX_STREAM:
            raise ValueError("original producer stream bound exceeded")
        # Pinned original code has one foreground Python writer and no
        # background-launch path. Both the shell and that writer have exited.
        artifact = read_output(root / "README.md") if observed.returncode == 0 else None
        frame = dict(schema="implementaudit.readme-effect-frame.v1",
                     command="bash scripts/generate-readme-diagrams.sh\n",
                     program_sha256=PROGRAM_SHA256, exit=observed.returncode,
                     complete=True, stdout=base64.b64encode(observed.stdout).decode("ascii"),
                     stderr=base64.b64encode(observed.stderr).decode("ascii"), artifact=artifact)
        raw = MAGIC + encode(frame)
        if len(raw) > MAX_FRAME:
            raise ValueError("producer frame bound exceeded")
        sys.stdout.buffer.write(raw)
        sys.stdout.buffer.flush()
        return observed.returncode if 0 <= observed.returncode <= 255 else 1


if __name__ == "__main__":
    raise SystemExit(produce())
