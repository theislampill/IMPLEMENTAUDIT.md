"""Run the unchanged Task 1 R2 receiver on read-only public roles in a POSIX temp root."""

import base64
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import sys
import tarfile
import tempfile
import types
import zipfile


MANIFEST_SHA256 = "5bc8cfd3aee3ebcd59bad8315ca56de12ebc37753e8ac590f276c996436d9962"
R2_PIN = {"bytes": 23942, "sha256": "081a844e9d5a9877439a2f6490a9452b4dea73f2dfec059adeeda365ec9a30e4"}
GROUPS = ("baseline", "owners", "full_before")
SINGLES = ("composer", "runtime", "reverse_map", "generator")
EXPECTED_COUNTS = {"baseline": 175, "owners": 6, "full_before": 5,
                   "composer": 1, "runtime": 1, "reverse_map": 1, "generator": 1}
ROLE_BYTES = 5999010
TRANSPORT_MAX = 12 * 1024 * 1024
ARCHIVE_MAX = 32 * 1024 * 1024


def require(value, label):
    if not value:
        raise ValueError(label)


def pin(raw):
    return {"bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}


def canonical(value):
    return (json.dumps(value, sort_keys=True, indent=2) + "\n").encode("utf-8")


def git_blob(oid):
    size = int(subprocess.check_output(["git", "cat-file", "-s", oid]))
    require(0 <= size <= ARCHIVE_MAX, "public blob bound")
    return subprocess.check_output(["git", "cat-file", "blob", oid])


def archived_member(raw, kind, ordinal):
    require(type(ordinal) is int and 0 <= ordinal < 5000, "archive ordinal bound")
    if kind == "zip":
        with zipfile.ZipFile(io.BytesIO(raw)) as archive:
            row = archive.infolist()[ordinal]
            require(not row.is_dir() and 0 <= row.file_size <= ARCHIVE_MAX, "ZIP member bound")
            with archive.open(row) as member:
                return member.read(row.file_size + 1)
    require(kind == "tar", "unknown archive locator")
    with tarfile.open(fileobj=io.BytesIO(raw), mode="r|*") as archive:
        expanded = 0
        for index, row in enumerate(archive):
            expanded += row.size
            require(expanded <= 128 * 1024 ** 2, "TAR expansion bound")
            if index == ordinal:
                require(row.isfile() and 0 <= row.size <= ARCHIVE_MAX, "TAR member bound")
                with archive.extractfile(row) as member:
                    return member.read(row.size + 1)
    raise ValueError("archive ordinal outside container")


def indexed_roles(manifest_path):
    raw = manifest_path.read_bytes()
    require(pin(raw)["sha256"] == MANIFEST_SHA256, "prior immutable manifest mismatch")
    manifest = json.loads(raw)
    cache = {}
    for row in manifest["members"]:
        kind, _, identity, *trail = row["locator"]
        if kind == "public_git_blob":
            require(not trail, "unexpected data path under direct blob")
            content = git_blob(identity)
        else:
            require(kind == "public_git_archive" and trail, "unrecognized archive locator")
            key = tuple(identity)
            if key not in cache:
                require(0 < len(key) <= 40, "archive part count")
                sizes = [int(subprocess.check_output(["git", "cat-file", "-s", oid])) for oid in key]
                require(sum(sizes) <= ARCHIVE_MAX, "archive part byte sum")
                cache[key] = b"".join(git_blob(oid) for oid in key)
            content = cache[key]
            for kind, ordinal in trail:
                content = archived_member(content, kind, ordinal)
        require(pin(content) == row["input"], "exact public role mismatch")
        yield row["role"], row["member"], row["input"], content


def load_r2(raw):
    require(pin(raw) == R2_PIN, "pinned R2 source mismatch")
    source = types.ModuleType("verified_task1_r2")
    sys.modules[source.__name__] = source
    # This executes only the previously reviewed Task 1 R2 receiver.
    exec(compile(raw, "<immutable reviewed Task1 R2>", "exec", dont_inherit=True), source.__dict__)
    return source


def stage_member(path, raw):
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW
    fd = os.open(path, flags, 0o400)
    with os.fdopen(fd, "wb") as stream:
        stream.write(raw)
    observed = path.lstat()
    require(stat.S_ISREG(observed.st_mode) and observed.st_nlink == 1
            and stat.S_IMODE(observed.st_mode) == 0o400, "staged inert file kind/mode")


def frozen_file(root, group, member):
    path = PurePosixPath(member)
    require(not path.is_absolute() and str(path) == member and ".." not in path.parts,
            "unsafe member role path")
    return root / group / (member + ".py" if group == "full_before" else member)


def unpack_packet(envelope):
    require(type(envelope) is list and len(envelope) == 190, "public role packet population")
    rows = {}
    for role, member, want, encoded in envelope:
        require(role in EXPECTED_COUNTS and ((role in GROUPS and type(member) is str) or
                (role in SINGLES and member is None)), "public role identity")
        raw = base64.b64decode(encoded, validate=True)
        require((role, member) not in rows and pin(raw) == want, "public role identity or byte pin")
        rows[role, member] = raw
    require(sum(map(len, rows.values())) == ROLE_BYTES, "public input byte population")
    return rows


def receive(envelope):
    require(os.name == "posix" and os.geteuid() != 0 and os.open in os.supports_dir_fd,
            "unprivileged POSIX directory-descriptor receiver required")
    rows = unpack_packet(envelope)
    source = load_r2(rows["generator", None])
    spec = {}
    actual = {}
    with tempfile.TemporaryDirectory(prefix="dg16-task1-r2-public-", dir="/tmp") as directory:
        root = Path(directory)
        require(root.resolve() == root and stat.S_IMODE(root.stat().st_mode) == 0o700,
                "isolated no-alias temporary root")
        for (role, member), raw in rows.items():
            if role in GROUPS:
                path = frozen_file(root, role, member)
                spec.setdefault(role, {})[member] = pin(raw)
                actual[role] = str(root / role)
            else:
                path = root / (role + ".inert")
                spec[role] = pin(raw)
                actual[role] = str(path)
            stage_member(path, raw)
        actual["destination"] = str(root / "uncreated-destination")
        specs, locations = canonical(spec), canonical(actual)
        bundle = source.receive_inputs(specs, locations)
        for key, raw in rows.items():
            role, member = key
            observed = getattr(bundle, role)
            require((observed if member is None else observed[member]) == raw,
                    "returned R2 input bytes differ")
        require(not Path(actual["destination"]).exists(), "unexpected destination materialization")
    require(not root.exists(), "isolated directory cleanup failed")
    return {
        "schema": "dg16.task1-r2.physical-public-receiving.v1",
        "scope": "ONE_ORDINARY_UNPRIVILEGED_POSIX_PUBLIC_INPUT_RECEIVING",
        "prior_manifest_sha256": MANIFEST_SHA256, "receiver": R2_PIN,
        "python": sys.version.split()[0], "platform": os.name,
        "roles": EXPECTED_COUNTS, "bytes": ROLE_BYTES, "roles_received": len(rows),
        "pure_spec": pin(specs), "actual_path_map": pin(locations),
        "physical_roles_matched": True, "receiver_bookends_passed": True,
        "uncreated_destination": True, "temporary_directory_removed": True,
        "input_file_mode": "0400", "temporary_directory_mode": "0700",
        "private_inputs": False, "operational_source_executed": False, "projected_source_exported": False,
        "source_adoption": False, "protected_readiness": False, "original_awards": [],
    }


def main():
    if sys.argv[1:] == ["--receive"]:
        packet = sys.stdin.buffer.read(TRANSPORT_MAX + 1)
        require(len(packet) <= TRANSPORT_MAX, "public transport bound")
        reply = receive(json.loads(packet))
        sys.stdout.buffer.write(canonical(reply))
        return
    require(len(sys.argv) == 3 and sys.argv[1] == "--wsl-distribution", "supply the selected POSIX runtime")
    here = Path(__file__).parent
    packet = [[role, member, want, base64.b64encode(raw).decode("ascii")]
              for role, member, want, raw in indexed_roles(here / "INERT_MANIFEST.json")]
    encoded = canonical(packet)
    require(len(encoded) <= TRANSPORT_MAX, "public transport bound")
    program = Path(__file__).read_text(encoding="utf-8")
    received = subprocess.run(
        ["wsl.exe", "--distribution", sys.argv[2], "--exec", "python3", "-I", "-B", "-c", program, "--receive"],
        input=encoded, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=45,
    )
    require(received.returncode == 0, "POSIX Task 1 R2 process refused: " +
            received.stderr.decode("utf-8", "replace").splitlines()[-1][:200] if received.stderr else
            "POSIX Task 1 R2 process refused")
    result = json.loads(received.stdout)
    require(result["scope"] == "ONE_ORDINARY_UNPRIVILEGED_POSIX_PUBLIC_INPUT_RECEIVING"
            and result["physical_roles_matched"] is True and result["temporary_directory_removed"] is True,
            "unverified physical receiver result")
    sys.stdout.buffer.write(canonical(result))


if __name__ == "__main__":
    main()
