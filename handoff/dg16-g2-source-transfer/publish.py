#!/usr/bin/env python3
"""Transfer exact public source bytes to immutable Git objects; never move refs."""
import argparse
import hashlib
import http.client
import json
import os
from pathlib import Path, PurePosixPath
import re
import signal
import stat
import subprocess
import time

REPOSITORY = "theislampill/IMPLEMENTAUDIT.md"
BRANCH = "pro/dg16-g2-source-transfer-20261117"
BASE_COMMIT = "b41e2d7100008cdb2f2fcd77b1543a25ad7b9140"
BASE_TREE = "5f1fc39bd60afe361d3f70e446ec91e10d004db1"
SKIP = ".github/workflows/dg16-r5-full-g2.yml"


class Refusal(Exception):
    """Only messages written as constants in this helper may enter this class."""


def require(ok, message):
    if not ok:
        raise Refusal(message)


def failure(error):
    detail = {"error_type": type(error).__name__}
    if isinstance(error, Refusal):
        detail.update(error_code=str(error).upper().replace(" ", "_")[:100], error_message=str(error)[:200])
    elif isinstance(error, TimeoutError):
        detail.update(error_code="TRANSPORT_TIMEOUT", error_message="Transport timed out; no retry")
    return detail


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def object_id(kind, data):
    return hashlib.sha1(kind + b" " + str(len(data)).encode() + b"\0" + data).hexdigest()


def json_bytes(value):
    return (json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n").encode()


def prepare(delta_path, source, expected_delta):
    """Pure byte reconstruction; read files as data, without importing any of them."""
    raw = delta_path.read_bytes()
    require(sha256(raw) == expected_delta, "delta digest")
    delta = json.loads(raw)
    require(delta["schema"] == "dg16-g2-source-transfer-delta.v1", "schema")
    require(delta["repository"] == REPOSITORY, "repository")
    require(delta["base_commit"] == BASE_COMMIT and delta["base_tree"] == BASE_TREE, "base")
    require(delta["operation_fields"] == ["offset", "delete_bytes", "insert_utf8"], "edit format")
    entries = delta["entries"]
    require(len(entries) == 24 and len({e["path"] for e in entries}) == 24, "path count")
    require(sum(e["path"] == SKIP for e in entries) == 1, "workflow skip")
    rebuilt = []
    for entry in entries:
        path = entry["path"]
        parts = PurePosixPath(path).parts
        require(parts and not path.startswith("/") and all(p not in (".", "..") for p in parts), "path")
        require(str(PurePosixPath(path)) == path, "canonical path")
        require(path == SKIP or path.startswith(("qualification/dg16-r5-full-g2/", "qualification/dg16-r5-full-g2-decisions/")), "scope")
        require(entry["mode"] == "100644", "mode")
        current = source
        for part in parts:
            current = current / part
            require(not current.is_symlink(), "symlink")
        mode = current.stat().st_mode
        require(stat.S_ISREG(mode) and mode & 0o111 == 0, "regular non-executable file")
        old = current.read_bytes()
        require(len(old) == entry["old_bytes"] and sha256(old) == entry["old_sha256"], "old bytes")
        require(object_id(b"blob", old) == entry["old_git_blob"], "old Git blob")
        chunks, cursor, last_offset = [], 0, -1
        require(entry["operations"], "empty edits")
        for operation in entry["operations"]:
            require(type(operation) is list and len(operation) == 3, "edit shape")
            offset, delete, insert = operation
            require(type(offset) is int and type(delete) is int and type(insert) is str, "edit types")
            require(offset > last_offset and offset >= cursor and delete >= 0 and offset + delete <= len(old), "ordered non-overlap bounds")
            chunks.extend((old[cursor:offset], insert.encode("utf-8")))
            cursor, last_offset = offset + delete, offset
        new = b"".join(chunks) + old[cursor:]
        require(len(new) == entry["new_bytes"] and sha256(new) == entry["new_sha256"], "new bytes")
        require(object_id(b"blob", new) == entry["new_git_blob"], "new Git blob")
        new.decode("utf-8")
        rebuilt.append((entry, new))
    return delta, rebuilt


def git(directory, *args):
    # Read-only commands, no inherited token, no target hooks or target Python.
    return subprocess.run(
        ["/usr/bin/git", "-c", "safe.directory=" + str(directory), "-C", str(directory), *args],
        check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=30,
        env={"PATH": "/usr/bin:/bin", "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_TERMINAL_PROMPT": "0"},
    ).stdout


def expected_tree(source, rebuilt):
    """Hash changed ancestor trees; preserve every other base entry."""
    require(git(source, "rev-parse", "HEAD").strip().decode() == BASE_COMMIT, "source HEAD")
    require(git(source, "rev-parse", "HEAD^{tree}").strip().decode() == BASE_TREE, "source tree")
    rows, children = {}, {}
    for row in git(source, "ls-tree", "-r", "-t", "-z", "HEAD").split(b"\0"):
        if not row:
            continue
        header, path = row.split(b"\t", 1)
        mode, kind, oid = header.split()
        require(path not in rows, "duplicate tree path")
        rows[path] = (mode, kind, oid)
        parent, _, name = path.rpartition(b"/")
        children.setdefault(parent, []).append((name, path))

    def tree(parent, replacements):
        body = bytearray()
        order = sorted(children.get(parent, []), key=lambda pair: pair[0] + (b"/" if rows[pair[1]][1] == b"tree" else b""))
        for name, path in order:
            mode, kind, oid = rows[path]
            digest = replacements.get(path, oid.decode())
            if kind == b"tree" and any(p.startswith(path + b"/") for p in replacements):
                digest = tree(path, replacements)
            body.extend(mode.lstrip(b"0") + b" " + name + b"\0" + bytes.fromhex(digest))
        return object_id(b"tree", bytes(body))

    require(tree(b"", {}) == BASE_TREE, "base tree reconstruction")
    replacements = {}
    for entry, _ in rebuilt:
        path = entry["path"].encode()
        require(rows.get(path) == (entry["mode"].encode(), b"blob", entry["old_git_blob"].encode()), "base tree member")
        if entry["path"] != SKIP:
            replacements[path] = entry["new_git_blob"]
    require(len(replacements) == 23, "23 non-workflow changes")
    return tree(b"", replacements)


class Journal:
    def __init__(self, directory):
        self.directory = directory
        directory.mkdir(parents=True, exist_ok=True)
        self.log = (directory / "receipts.jsonl").open("x", encoding="utf-8")
        self.sequence = 0
        self.sync_directory()

    def sync_directory(self):
        fd = os.open(self.directory, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)

    def record(self, value):
        value = {"time_ns": time.time_ns(), **value}
        line = json_bytes(value).decode()
        self.log.write(line)
        self.log.flush()
        os.fsync(self.log.fileno())
        print(line, end="", flush=True)

    def result(self, value):
        temporary = self.directory / "result.tmp"
        with temporary.open("wb") as stream:
            stream.write(json_bytes(value))
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, self.directory / "result.json")
        self.sync_directory()

    def response_body(self, sequence, raw, token):
        # Git Database responses are public object metadata/errors. Never save a token.
        if token.encode() in raw:
            return "WITHHELD_TOKEN_SUBSTRING"
        name = "response-" + str(sequence).zfill(2) + ".body"
        with (self.directory / name).open("xb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        self.sync_directory()
        return name

    def post(self, token, kind, body, expected_sha, source_path=None):
        require(kind in ("blobs", "trees"), "immutable object endpoint")
        self.sequence += 1
        endpoint = "/repos/" + REPOSITORY + "/git/" + kind
        payload = json_bytes(body)
        self.record({"type": "intent", "sequence": self.sequence, "method": "POST", "endpoint": endpoint,
                     "source_path": source_path, "body_bytes": len(payload), "body_sha256": sha256(payload), "expected_sha": expected_sha})
        receipt = {"type": "result", "sequence": self.sequence, "status": "UNKNOWN", "expected_sha": expected_sha}
        connection = None
        raw = None
        try:
            connection = http.client.HTTPSConnection("api.github.com", timeout=15)
            # Exactly one request. No redirects, retries, commits, refs, or dispatch.
            connection.request("POST", endpoint, body=payload, headers={
                "Authorization": "Bearer " + token, "Accept": "application/vnd.github+json",
                "Content-Type": "application/json", "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "dg16-g2-source-transfer",
            })
            response = connection.getresponse()
            receipt["http_status"] = response.status
            raw = response.read(8 * 1024 * 1024 + 1)
            receipt.update(response_bytes=len(raw), response_sha256=sha256(raw), response_truncated=len(raw) > 8 * 1024 * 1024)
            require(len(raw) <= 8 * 1024 * 1024 and response.status == 201, "non-success response")
            received = json.loads(raw)
            require(received.get("sha") == expected_sha, "provider object identity")
            receipt.update(status="CONFIRMED", returned_sha=received["sha"])
        except BaseException as error:
            receipt.update(failure(error))
            if raw is not None:
                receipt["response_body"] = self.response_body(self.sequence, raw, token)
            self.record(receipt)
            raise Refusal("object creation unconfirmed; no retry") from None
        else:
            self.record(receipt)
        finally:
            if connection is not None:
                connection.close()
        return expected_sha


def check_event(publisher):
    env = os.environ
    require(env.get("GITHUB_EVENT_NAME") == "push" and env.get("GITHUB_RUN_ATTEMPT") == "1", "first push attempt")
    require(env.get("GITHUB_REPOSITORY") == REPOSITORY and env.get("GITHUB_REF") == "refs/heads/" + BRANCH, "owned fresh branch")
    require(env.get("GITHUB_API_URL") == "https://api.github.com" and env.get("GITHUB_SERVER_URL") == "https://github.com", "provider")
    event = json.loads(Path(env["GITHUB_EVENT_PATH"]).read_bytes())
    require(event.get("created") is True and event.get("deleted") is False and event.get("forced") is False, "new non-forced push")
    require(event.get("before") == "0" * 40 and event.get("ref") == env["GITHUB_REF"], "zero-before ref")
    commit = env.get("GITHUB_SHA", "")
    require(re.fullmatch("[0-9a-f]{40}", commit) and event.get("after") == commit, "event commit")
    require(event.get("repository", {}).get("full_name") == REPOSITORY, "event repository")
    require(env.get("GITHUB_WORKFLOW_SHA") == commit, "workflow commit")
    require(git(publisher, "rev-parse", "HEAD").strip().decode() == commit, "publisher checkout")
    return commit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    journal = Journal(args.output)
    result = {"schema": "dg16-g2-source-transfer-result.v1", "status": "PREFLIGHT_PENDING", "repository": REPOSITORY}
    journal.result(result)

    def expired(_signum, _frame):
        raise Refusal("transfer time bound reached")

    signal.signal(signal.SIGALRM, expired)
    signal.signal(signal.SIGTERM, expired)
    signal.alarm(360)
    try:
        helper = Path(__file__).resolve()
        commit = check_event(helper.parents[2])
        delta_hash = os.environ["EXPECTED_DELTA_SHA256"]
        delta, rebuilt = prepare(helper.with_name("delta.json"), args.source.resolve(), delta_hash)
        tree_sha = expected_tree(args.source.resolve(), rebuilt)
        identities = {k: v for k, v in delta.items() if k not in ("entries", "operation_fields")}
        identities.update(delta_sha256=delta_hash, publisher_sha256=sha256(helper.read_bytes()), bootstrap_commit=commit,
                          run_id=os.environ["GITHUB_RUN_ID"], run_attempt="1")
        files = [{k: v for k, v in entry.items() if k != "operations"} for entry, _ in rebuilt]
        result.update(status="PREFLIGHT_VERIFIED", source_identities=identities, files=files,
                      expected_nonworkflow_tree=tree_sha, skipped_workflow=SKIP)
        journal.record({"type": "preflight_verified", "delta_sha256": delta_hash, "verified_files": 24,
                        "planned_blobs": 23, "planned_trees": 1, "expected_tree": tree_sha})
        journal.result(result)
        token = os.environ.pop("GITHUB_TOKEN", "")
        require(token and token.strip() == token, "standard ephemeral token")
        entries = []
        for entry, data in rebuilt:
            if entry["path"] == SKIP:
                continue
            oid = journal.post(token, "blobs", {"content": data.decode("utf-8"), "encoding": "utf-8"}, entry["new_git_blob"], entry["path"])
            entries.append({"path": entry["path"], "mode": entry["mode"], "type": "blob", "sha": oid})
        tree = journal.post(token, "trees", {"base_tree": BASE_TREE, "tree": entries}, tree_sha)
        result.update(status="TRANSFERRED_TREE_ONLY", tree_sha=tree, confirmed_api_writes=journal.sequence)
        journal.result(result)
    except BaseException as error:
        result.update(status="STOPPED_NO_RETRY", api_writes_attempted=journal.sequence, **failure(error))
        journal.result(result)
        print("Source transfer stopped; inspect result.json and receipts.jsonl. No retry.", flush=True)
        return 1
    finally:
        signal.alarm(0)
        journal.log.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
