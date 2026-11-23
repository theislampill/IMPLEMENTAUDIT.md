"""Read every file of a fresh, exact public c53 POSIX checkout as inert data."""
from collections import Counter
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import stat
import subprocess
import tempfile

URL = "https://github.com/theislampill/IMPLEMENTAUDIT.md.git"
PUBLIC_REF = "refs/heads/pro/dg16-g132-boot-nss-source-20261122-01"
HEAD = "c53ed7de85de22ce313233472c8d8f02ad8e9d02"
TREE = "d60733459425a059d961b6adc2aae9811bbb761c"
LOCAL_REF = "refs/receiving/exact-c53"
EXPECTED_MODES = {"100644": 1697, "100755": 81}
MODE = {"100644": 0o644, "100755": 0o755}
GIT = ["/usr/bin/git", "--no-replace-objects", "-c", "core.hooksPath=/dev/null",
       "-c", "core.autocrlf=false", "-c", "core.eol=lf", "-c", "advice.detachedHead=false"]
ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(PATH="/usr/bin:/bin", GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1",
           GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0", LC_ALL="C")
MAX_BLOB = 64 * 1024**2
MAX_TOTAL = 512 * 1024**2


def need(value, condition):
    if not value:
        raise ValueError(condition)


def git(*args, cwd=None, timeout=20):
    result = subprocess.run([*GIT, *args], cwd=cwd, env=ENV, stdin=subprocess.DEVNULL,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=timeout)
    need(result.returncode == 0, f"ordinary Git command refused: {args[0]} exit {result.returncode}")
    return result.stdout


def public_ref():
    expected = f"{HEAD}\t{PUBLIC_REF}\n".encode()
    need(git("ls-remote", "--exit-code", "--heads", URL, PUBLIC_REF, cwd="/var/tmp") == expected,
         "live public ref differs")


def tree_files(repo):
    result = {}
    raw = git("ls-tree", "-rz", "-l", TREE, cwd=repo)
    for record in raw.split(b"\0"):
        if not record:
            continue
        head, name = record.decode("utf-8").split("\t", 1)
        mode, kind, oid, size = head.split()
        rel = PurePosixPath(name)
        need(not rel.is_absolute() and rel.as_posix() == name and name not in result
             and not {".", "..", ".git"} & set(rel.parts), "unsafe or duplicate Git pathname")
        need(kind == "blob" and mode in MODE and 0 <= int(size) <= MAX_BLOB,
             "unsupported or oversized Git leaf")
        result[name] = (mode, oid, int(size))
    need(Counter(row[0] for row in result.values()) == EXPECTED_MODES, "Git leaf counts differ")
    need(sum(row[2] for row in result.values()) <= MAX_TOTAL, "Git population exceeds bound")
    return result, hashlib.sha256(raw).hexdigest()


def identity(info):
    return (info.st_dev, info.st_ino, info.st_mode, info.st_size, info.st_nlink,
            info.st_mtime_ns, info.st_ctime_ns)


def physical_inventory(repo, expected):
    result, seen_dirs = {}, set()
    expected_dirs = {d.as_posix() for name in expected for d in PurePosixPath(name).parents}
    for directory, dirs, files in os.walk(repo, followlinks=False):
        parent = Path(directory)
        seen_dirs.add(parent.relative_to(repo).as_posix())
        for name in dirs:
            need(stat.S_ISDIR((parent / name).lstat().st_mode), "symlink or nonphysical directory")
        if parent == repo:
            need(".git" in dirs, "missing fresh Git directory")
            dirs.remove(".git")
        for name in files:
            path = parent / name
            relative = path.relative_to(repo).as_posix()
            info = path.lstat()
            need(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, "nonregular or linked checkout leaf")
            need(relative in expected, "unexpected physical payload")
            mode, _, size = expected[relative]
            need(stat.S_IMODE(info.st_mode) == MODE[mode] and info.st_size == size, "physical mode or size differs")
            result[relative] = identity(info)
    need(set(result) == set(expected) and seen_dirs == expected_dirs, "checkout path census differs")
    return result


def digest_stream(stream, size):
    digest = hashlib.sha256()
    blob = hashlib.sha1(f"blob {size}\0".encode())
    left = size
    while left:
        raw = stream.read(min(left, 1024**2))
        need(raw, "short read of pinned blob")
        digest.update(raw)
        blob.update(raw)
        left -= len(raw)
    return blob.hexdigest(), digest.hexdigest()


def compare_file_bytes(repo, expected, opening):
    rows = []
    with subprocess.Popen([*GIT, "cat-file", "--batch"], cwd=repo, env=ENV,
                          stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL) as proc:
        try:
            for name, (mode, oid, size) in sorted(expected.items()):
                proc.stdin.write(oid.encode("ascii") + b"\n")
                proc.stdin.flush()
                need(proc.stdout.readline() == f"{oid} blob {size}\n".encode(), "Git blob body header differs")
                object_identity = digest_stream(proc.stdout, size)
                need(proc.stdout.read(1) == b"\n" and object_identity[0] == oid, "Git blob body differs")
                fd = os.open(repo / name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC)
                with os.fdopen(fd, "rb") as physical:
                    need(identity(os.fstat(physical.fileno())) == opening[name], "file changed before reading")
                    observed = digest_stream(physical, size)
                    need(observed == object_identity and not physical.read(1), "physical blob or SHA-256 differs")
                    need(identity(os.fstat(physical.fileno())) == opening[name], "file changed during reading")
                rows.append([name, mode, size, oid, observed[1]])
        finally:
            proc.stdin.close()
        need(proc.wait(timeout=20) == 0, "Git batch stream did not close")
    return hashlib.sha256(json.dumps(rows, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def run():
    need(os.name == "posix" and os.geteuid() != 0, "unprivileged POSIX reader required")
    public_ref()
    parent = Path(tempfile.mkdtemp(prefix="dg16-c53-physical-", dir="/var/tmp"))
    need(parent.resolve() == parent and stat.S_IMODE(parent.stat().st_mode) == 0o700,
         "fresh private physical parent required")
    repo = parent / "checkout"
    print(f"PHYSICAL_ROOT={repo}", file=__import__("sys").stderr, flush=True)
    mask = os.umask(0o022)
    try:
        git("init", "--quiet", "--template=", str(repo), cwd=parent)
        git("fetch", "--depth=1", "--no-tags", "--no-recurse-submodules", "--no-auto-maintenance",
            URL, f"{PUBLIC_REF}:{LOCAL_REF}", cwd=repo, timeout=150)
        need(git("rev-parse", f"{LOCAL_REF}^{{commit}}", cwd=repo).decode().strip() == HEAD,
             "fetched commit differs from the public ref check")
        git("switch", "--quiet", "--detach", HEAD, cwd=repo)
    finally:
        os.umask(mask)

    def state():
        return (
            git("rev-parse", "HEAD", "HEAD^{tree}", cwd=repo).decode().splitlines(),
            git("status", "--porcelain=v1", "-z", "--untracked-files=all", cwd=repo, timeout=35),
            git("for-each-ref", "--format=%(refname)", "refs/implementaudit/", cwd=repo),
        )

    opening = state()
    need(opening == ([HEAD, TREE], b"", b""), "source dirty, drifted, or inherited an owner ref")
    expected, tree_sha = tree_files(repo)
    physical = physical_inventory(repo, expected)
    rows_sha = compare_file_bytes(repo, expected, physical)
    need(physical_inventory(repo, expected) == physical, "worktree changed during readback")
    need(state() == opening, "closing source, cleanliness, or owner-ref drift")
    public_ref()
    return {
        "schema": "dg16.c53.physical-public-checkout-receiving.v1",
        "source_ref": PUBLIC_REF, "commit": HEAD, "tree": TREE, "public_ref_bookends_match": True,
        "members": len(expected), "bytes": sum(x[2] for x in expected.values()), "modes": EXPECTED_MODES,
        "git_ls_tree_z_sha256": tree_sha, "physical_and_git_row_census_sha256": rows_sha,
        "census_encoding": "sorted path, Git mode, size, Git blob OID, physical SHA-256, compact UTF-8 JSON array",
        "every_physical_member_and_git_blob_match": True, "physical_identity_bookends_match": True,
        "clean_before_and_after": True, "extra_payload_or_aliased_leaf_admitted": False,
        "checkout_retained_in_private_posix_directory": True,
        "product_or_host_code_executed": False, "protected_inputs": False, "currentness_established": False,
        "v5_grant_issued": False, "joint_adoption": False,
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
