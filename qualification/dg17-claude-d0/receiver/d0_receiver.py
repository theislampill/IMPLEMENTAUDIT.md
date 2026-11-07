"""Bounded independent D0 receiver. Importing performs no host observations.

The POSIX adapter is callable only inside a separately admitted same-job D0
operation. This source and its synthetic controls confer no such admission.
"""
from __future__ import annotations
import argparse
import copy
import errno
import hashlib
import json
import os
import stat
import sys

import d0_wire as w

CHUNK = 65536
RECUT_SCHEMA_NAME = "dg17.claude.d0.independent-recut.v1"



CARRIER_WITNESS = w.obj({"before": w.IDENTITY, "after": w.IDENTITY,
                        "path_before": w.IDENTITY, "path_after": w.IDENTITY,
                        "bytes": w.integer(1, w.PRIVATE_LIMIT), "eof": {"const": True}, "sha256": w.HASH})
RECUT_SCHEMA = {"$schema": "https://json-schema.org/draft/2020-12/schema",
                **w.obj({"schema": {"const": RECUT_SCHEMA_NAME}, "binding": w.BINDING,
                         "producer_private_sha256": w.HASH, "public_sha256": w.HASH,
                         "producer_carrier": CARRIER_WITNESS,
                         "before": w.RECUT_RECORDS, "after": w.RECUT_RECORDS,
                         "source_effect_authority": {"const": "NONE"},
                         "historical_before_cut_independently_witnessed": {"const": False}})}
DECISION_SCHEMA = {"$schema": "https://json-schema.org/draft/2020-12/schema",
                   **w.obj({"schema": {"const": "dg17.claude.d0.receiver-decision.v1"},
                            "private_receipt_sha256": w.HASH, "public_receipt_sha256": w.HASH,
                            "operation_binding_sha256": w.HASH, "independent_receipt_sha256": w.HASH,
                            "observation": {"enum": ["RECEIVED_FIXED_HOST_INPUTS", "INCOMPLETE_OR_REFUSED"]},
                            "eligibility": {"enum": ["ELIGIBLE_FOR_SEPARATELY_REVIEWED_FIXED_VIEW", "NOT_ELIGIBLE", "UNDETERMINED_INCOMPLETE_OBSERVATION"]},
                            "reason_codes": w.array(w.CODE, 16), "source_effect_authority": {"const": "NONE"},
                            "original_acceptance": {"const": False},
                            "historical_before_cut_independently_witnessed": {"const": False}})}

def identity(st):
    value = {k: getattr(st, "st_" + k) for k in
             ("dev", "ino", "uid", "gid", "mode", "nlink", "size", "mtime_ns", "ctime_ns")}
    w.validate(value, w.IDENTITY)
    return value


def failed(code, error=None):
    number = error.errno if isinstance(error, OSError) else None
    if number is not None and not 1 <= number <= 4095:
        number = None
    return {"code": code, "errno": number}


class PosixIO:
    """Exact syscall surface; no shell, subprocess, environment, or discovery."""
    def __init__(self):
        for flag in ("O_PATH", "O_DIRECTORY", "O_NOFOLLOW", "O_CLOEXEC", "O_NONBLOCK"):
            w.require(hasattr(os, flag), "REQUIRED_POSIX_PRIMITIVE_MISSING")

    def root(self):
        return os.open("/", os.O_PATH | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC)

    def lstat(self, parent, name):
        return identity(os.stat(name, dir_fd=parent, follow_symlinks=False))

    def fstat(self, fd):
        return identity(os.fstat(fd))

    def open_dir(self, parent, name):
        return os.open(name, os.O_PATH | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=parent)

    def readlink(self, parent, name):
        return os.readlink(name, dir_fd=parent)

    def open_file(self, parent, name):
        return os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK, dir_fd=parent)

    def read(self, fd, size):
        return os.read(fd, size)

    def capability(self, fd):
        return os.getxattr(fd, "security.capability")

    def executable(self, parent, name):
        # No fallback to a weaker access predicate when the native primitive is absent.
        if os.access not in os.supports_dir_fd or os.access not in os.supports_effective_ids or os.access not in os.supports_follow_symlinks:
            raise OSError(errno.ENOTSUP, "unsupported primitive")
        return os.access(name, os.X_OK, dir_fd=parent, effective_ids=True, follow_symlinks=False)

    def close(self, fd):
        os.close(fd)


def probe(call):
    try:
        return {"identity": call(), "errno": None}
    except OSError as error:
        w.require(error.errno is not None and 1 <= error.errno <= 4095, "OS_ERROR_WITHOUT_ERRNO")
        return {"identity": None, "errno": error.errno}


def link_probe(call):
    try:
        value = call()
        w.validate(value, w.PATH)
        return {"value": value, "errno": None}
    except OSError as error:
        w.require(error.errno is not None and 1 <= error.errno <= 4095, "OS_ERROR_WITHOUT_ERRNO")
        return {"value": None, "errno": error.errno}


class PopulationBudget:
    def __init__(self):
        self.seen = {}

    def reserve(self, observed):
        key = (observed["dev"], observed["ino"])
        size = observed["size"]
        w.require(size <= w.PER_FILE, "FILE_BYTE_BOUND")
        if key in self.seen:
            w.require(self.seen[key] == observed, "POPULATION_IDENTITY_CHANGED")
        else:
            w.require(sum(x["size"] for x in self.seen.values()) + size <= w.TOTAL_FILES,
                      "POPULATION_BYTE_BOUND")
            self.seen[key] = copy.deepcopy(observed)


class Observer:
    """Observation policy stays here; an injected adapter does not choose paths."""
    def __init__(self, io):
        self.io = io
        self.budget = PopulationBudget()

    def population(self):
        self.budget = PopulationBudget()
        return [{"fixed_id": fixed_id, "cut": self.observe(fixed_id)} for fixed_id, _, _ in w.FIXED]

    def _body(self, parent, name, observed, helper):
        body = {"fd_before": None, "fd_after": None, "read_lengths": [],
                "read_errno": None, "bytes_read": 0, "eof": False, "sha256": None,
                "prefix_hex": "", "x_ok": None, "access_errno": None,
                "capability": None, "error": None}
        fd = None
        hasher = hashlib.sha256()
        prefix = bytearray()
        try:
            self.budget.reserve(observed)
            fd = self.io.open_file(parent, name)
            body["fd_before"] = probe(lambda: self.io.fstat(fd))
            w.require(body["fd_before"]["identity"] == observed and w.kind(observed) == "REGULAR",
                      "BODY_DESCRIPTOR_CHANGED")
            for _ in range(w.MAX_READS):
                limit = min(CHUNK, w.PER_FILE + 1 - body["bytes_read"])
                w.require(limit > 0, "FILE_BYTE_BOUND")
                try:
                    chunk = self.io.read(fd, limit)
                except OSError as error:
                    body["read_errno"] = error.errno
                    raise
                w.require(type(chunk) is bytes and len(chunk) <= limit, "READ_PRIMITIVE_RELATION")
                body["read_lengths"].append(len(chunk))
                if not chunk:
                    body["eof"] = True
                    break
                body["bytes_read"] += len(chunk)
                hasher.update(chunk)
                if len(prefix) < 20:
                    prefix.extend(chunk[:20 - len(prefix)])
                w.require(body["bytes_read"] <= w.PER_FILE, "FILE_BYTE_BOUND")
            w.require(body["eof"], "READ_OPERATION_BOUND")
            w.require(body["bytes_read"] == observed["size"], "BODY_LENGTH_CHANGED")
            if helper:
                try:
                    body["x_ok"] = self.io.executable(parent, name)
                    w.require(type(body["x_ok"]) is bool, "EXEC_ACCESS_UNKNOWN")
                except OSError as error:
                    body["access_errno"] = error.errno
                    raise
                try:
                    cap = self.io.capability(fd)
                    w.require(type(cap) is bytes and len(cap) <= 65536, "CAPABILITY_BYTE_BOUND")
                    body["capability"] = {"state": "NONEMPTY" if cap else "EMPTY", "length": len(cap),
                                           "sha256": w.digest(cap), "errno": None}
                except OSError as error:
                    if error.errno in (errno.ENODATA, errno.ENOTSUP):
                        body["capability"] = {"state": "NO_DATA" if error.errno == errno.ENODATA else "UNSUPPORTED",
                                               "length": 0, "sha256": None, "errno": error.errno}
                    else:
                        body["capability"] = {"state": "ERROR", "length": None, "sha256": None, "errno": error.errno}
                        raise
        except w.Refusal as error:
            body["error"] = failed(error.code)
        except OSError as error:
            body["error"] = failed("BODY_OS_ERROR", error)
        finally:
            body["sha256"] = hasher.hexdigest()
            body["prefix_hex"] = bytes(prefix).hex()
            if fd is not None:
                try:
                    body["fd_after"] = probe(lambda: self.io.fstat(fd))
                finally:
                    self.io.close(fd)
        return body

    def observe(self, fixed_id):
        w.require(fixed_id in w.FIXED_MAP, "FIXED_ID_UNKNOWN")
        requested, role = w.FIXED_MAP[fixed_id]
        helper = role in w.HELPERS
        pending = w.clean_path(requested)
        cut = {"walk": [], "aliases": [], "body": None, "terminal": None}
        # Internal descriptors and callbacks never appear on the wire.
        nodes = []
        aliases = []
        descriptors = []
        try:
            for hop in range(w.MAX_ALIASES + 1):
                fd = self.io.root()
                descriptors.append(fd)
                root = {"path": "/", "before": probe(lambda: self.io.fstat(fd)), "after": None,
                        "directory_before": probe(lambda: self.io.fstat(fd)), "directory_after": None}
                w.require(len(cut["walk"]) < w.MAX_WALK, "WALK_OPERATION_BOUND")
                cut["walk"].append(root)
                nodes.append((root, None, None, fd))
                w.require(root["before"]["identity"] is not None, "ROOT_OBSERVATION_FAILED")
                restart = False
                for i, component in enumerate(pending):
                    parent = fd
                    path = "/" + "/".join(pending[:i + 1])
                    node = {"path": path, "before": probe(lambda: self.io.lstat(parent, component)),
                            "after": None, "directory_before": None, "directory_after": None}
                    w.require(len(cut["walk"]) < w.MAX_WALK, "WALK_OPERATION_BOUND")
                    index = len(cut["walk"])
                    cut["walk"].append(node)
                    nodes.append((node, parent, component, None))
                    observed = node["before"]["identity"]
                    if observed is None:
                        if node["before"]["errno"] != errno.ENOENT:
                            cut["terminal"] = {"code": "OBSERVATION_OS_ERROR", "errno": node["before"]["errno"]}
                        break
                    leaf = i == len(pending) - 1
                    is_link = w.kind(observed) == "SYMLINK"
                    follow = is_link and (helper or (not leaf and path == "/bin" and requested.startswith("/bin/")))
                    if follow:
                        w.require(hop < w.MAX_ALIASES, "ALIAS_BOUND_OR_MISSING")
                        link = {"walk_index": index, "before": link_probe(lambda: self.io.readlink(parent, component)), "after": None}
                        cut["aliases"].append(link)
                        aliases.append((link, parent, component))
                        w.require(link["before"]["value"] is not None, "READLINK_ERROR")
                        destination = w.alias_destination(path, link["before"]["value"], pending[i + 1:])
                        if not helper:
                            w.require(path == "/bin" and
                                      w.alias_destination(path, link["before"]["value"], []) == "/usr/bin" and
                                      len(cut["aliases"]) == 1, "UNSELECTED_ANCESTOR_ALIAS")
                        pending = w.clean_path(destination)
                        w.require(pending, "HELPER_TARGET_IS_ROOT")
                        restart = True
                        break
                    if not leaf:
                        w.require(not is_link, "UNSELECTED_ANCESTOR_ALIAS")
                        w.require(w.kind(observed) == "DIRECTORY", "ANCESTOR_NOT_DIRECTORY")
                        fd = self.io.open_dir(parent, component)
                        descriptors.append(fd)
                        node["directory_before"] = probe(lambda: self.io.fstat(fd))
                        nodes[-1] = (node, parent, component, fd)
                        w.require(node["directory_before"]["identity"] == observed, "DIRECTORY_DESCRIPTOR_CHANGED")
                    elif (helper or role == "STARTUP") and w.kind(observed) == "REGULAR":
                        cut["body"] = self._body(parent, component, observed, helper)
                if not restart:
                    break
        except w.Refusal as error:
            cut["terminal"] = failed(error.code)
        except OSError as error:
            cut["terminal"] = failed("OBSERVATION_OS_ERROR", error)
        finally:
            for link, parent, name in aliases:
                try:
                    link["after"] = link_probe(lambda: self.io.readlink(parent, name))
                except w.Refusal as error:
                    cut["terminal"] = failed(error.code)
            for node, parent, name, fd in reversed(nodes):
                try:
                    node["after"] = probe(lambda: self.io.fstat(fd)) if parent is None else probe(lambda: self.io.lstat(parent, name))
                    if fd is not None:
                        node["directory_after"] = probe(lambda: self.io.fstat(fd))
                except w.Refusal as error:
                    cut["terminal"] = failed(error.code)
            for fd in reversed(descriptors):
                try:
                    self.io.close(fd)
                except OSError as error:
                    cut["terminal"] = failed("DESCRIPTOR_CLOSE_ERROR", error)
        return cut


def protected_file(observed, binding, limit):
    w.require(w.kind(observed) == "REGULAR" and stat.S_IMODE(observed["mode"]) == 0o600 and
              observed["uid"] == binding["evidence_uid"] and observed["gid"] == binding["evidence_gid"] and
              observed["nlink"] == 1 and 0 < observed["size"] <= limit, "PRIVATE_CARRIER_ADMISSION")


def read_descriptor(fd, limit):
    """Read a caller-admitted regular FD from offset zero with exact EOF and identity."""
    before = identity(os.fstat(fd))
    w.require(w.kind(before) == "REGULAR" and 0 < before["size"] <= limit, "INPUT_FD_ADMISSION")
    data = bytearray()
    offset = 0
    for _ in range(limit // CHUNK + 2):
        chunk = os.pread(fd, min(CHUNK, limit + 1 - offset), offset)
        if not chunk:
            break
        data.extend(chunk)
        offset += len(chunk)
        w.require(offset <= limit, "CARRIER_BYTE_BOUND")
    else:
        raise w.Refusal("CARRIER_READ_OPERATION_BOUND")
    after = identity(os.fstat(fd))
    w.require(before == after and len(data) == before["size"], "CARRIER_CHANGED")
    return bytes(data), {"before": before, "after": after, "bytes": len(data), "eof": True, "sha256": w.digest(bytes(data))}


class PrivateCarriers:
    """Only the three literal evidence filenames in an already admitted episode FD."""
    def __init__(self, episode_fd, binding):
        self.binding = binding
        self.episode_fd = episode_fd
        self.fd = None
        self.before = identity(os.stat("private", dir_fd=episode_fd, follow_symlinks=False))
        w.require(w.kind(self.before) == "DIRECTORY" and stat.S_IMODE(self.before["mode"]) == 0o700 and
                  self.before["uid"] == binding["evidence_uid"] and self.before["gid"] == binding["evidence_gid"],
                  "PRIVATE_DIRECTORY_ADMISSION")
        self.fd = os.open("private", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | os.O_CLOEXEC, dir_fd=episode_fd)
        try:
            w.require(identity(os.fstat(self.fd)) == self.before, "PRIVATE_DIRECTORY_CHANGED")
            # Dedicated container: enumerate names only, never inspect unexpected entries.
            self.inventory(expected={w.RECEIPT_NAME}, reserve=2)
        except BaseException:
            self.close()
            raise

    def inventory(self, expected, reserve=0):
        names = []
        with os.scandir(self.fd) as entries:
            for entry in entries:
                names.append(entry.name)
                w.require(len(names) + 1 + reserve <= w.MAX_ENTRIES, "EVIDENCE_ENTRY_BOUND")
                w.require(entry.name in expected, "UNDECLARED_PRIVATE_ENTRY")
        w.require(set(names) == expected, "PRIVATE_ENTRY_POPULATION")
        return {"entry_count_including_private_directory": len(names) + 1, "names": sorted(names)}

    def read_producer(self):
        before = identity(os.stat(w.RECEIPT_NAME, dir_fd=self.fd, follow_symlinks=False))
        protected_file(before, self.binding, w.PRIVATE_LIMIT)
        fd = os.open(w.RECEIPT_NAME, os.O_RDONLY | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK, dir_fd=self.fd)
        try:
            w.require(identity(os.fstat(fd)) == before, "PRIVATE_CARRIER_CHANGED")
            raw, witness = read_descriptor(fd, w.PRIVATE_LIMIT)
            after = identity(os.stat(w.RECEIPT_NAME, dir_fd=self.fd, follow_symlinks=False))
            w.require(before == after == witness["before"] == witness["after"], "PRIVATE_CARRIER_CHANGED")
        finally:
            os.close(fd)
        witness["path_before"] = before
        witness["path_after"] = after
        return raw, witness

    def check_before_output(self):
        w.require(self.before == identity(os.fstat(self.fd)) ==
                  identity(os.stat("private", dir_fd=self.episode_fd, follow_symlinks=False)), "PRIVATE_DIRECTORY_CHANGED")
        self.inventory(expected={w.RECEIPT_NAME}, reserve=2)

    def write(self, name, raw, limit):
        w.require(name in (w.RECUT_NAME, w.DECISION_NAME) and len(raw) <= limit, "OUTPUT_CARRIER_BOUND")
        fd = os.open(name, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK,
                     0o600, dir_fd=self.fd)
        try:
            initial = identity(os.fstat(fd))
            w.require(w.kind(initial) == "REGULAR" and initial["nlink"] == 1 and
                      stat.S_IMODE(initial["mode"]) == 0o600 and
                      initial["uid"] == self.binding["evidence_uid"] and initial["gid"] == self.binding["evidence_gid"],
                      "OUTPUT_CARRIER_ADMISSION")
            view = memoryview(raw)
            # Bounded calls; a short write is retained and refused, never silently accepted.
            written = os.write(fd, view)
            w.require(written == len(raw), "OUTPUT_SHORT_WRITE")
            os.fsync(fd)
            reread, witness = read_descriptor(fd, limit)
            protected_file(witness["after"], self.binding, limit)
            w.require(all(initial[key] == witness["after"][key] for key in ("dev", "ino", "uid", "gid", "mode", "nlink")) and
                      reread == raw and identity(os.stat(name, dir_fd=self.fd, follow_symlinks=False)) == witness["after"],
                      "OUTPUT_READBACK_CHANGED")
        finally:
            os.close(fd)
        return witness

    def close(self):
        if self.fd is not None:
            os.close(self.fd)
            self.fd = None


def receive(episode_fd, public_raw, expected_binding, public_schema_bytes, io=None):
    """Root supplies an independently admitted episode FD and exact trusted binding.

    No path, host identity, schema, or eligibility is accepted from public input.
    The current caller must already be authorized for this exact same-job D0 cut.
    """
    w.validate(expected_binding, w.BINDING)
    w.require(os.geteuid() == expected_binding["execution_uid"] and os.getegid() == expected_binding["execution_gid"],
              "EXECUTION_IDENTITY_MISMATCH")
    w.require(expected_binding["evidence_uid"] == os.geteuid() and expected_binding["evidence_gid"] == os.getegid(),
              "EVIDENCE_OUTPUT_OWNER_MISMATCH")
    w.require(sys.platform == "linux", "PLATFORM_MISMATCH")
    w.require(type(public_schema_bytes) is bytes and w.digest(public_schema_bytes) == w.PINS["public_schema_sha256"], "PUBLIC_SCHEMA_DIGEST")
    public_schema = json.loads(public_schema_bytes.decode("ascii"))
    public = w.decode(public_raw, w.PUBLIC_LIMIT)
    w.validate_public(public, public_schema)
    carriers = PrivateCarriers(episode_fd, expected_binding)
    try:
        raw, witness = carriers.read_producer()
        receipt = w.decode(raw, w.PRIVATE_LIMIT)
        w.validate(receipt, w.PRIVATE_SCHEMA)
        w.require(receipt["binding"] == expected_binding, "OPERATION_HOST_BINDING_MISMATCH")
        rebuilt, _ = w.derive_public(receipt, w.digest(raw))
        w.require(w.public_projection_matches(public, rebuilt), "PUBLIC_PROJECTION_MISMATCH")
        before, after = [], []
        # A producer partial result never triggers extra host reads to manufacture completion.
        if rebuilt["status"] == "RECEIVED_FIXED_HOST_INPUTS":
            observer = Observer(io if io is not None else PosixIO())
            before, after = observer.population(), observer.population()
        try:
            decision = w.evaluate(public_raw, raw, before, after, expected_binding, public_schema)
        except w.Refusal as error:
            decision = {"schema": "dg17.claude.d0.receiver-decision.v1", "private_receipt_sha256": w.digest(raw),
                        "public_receipt_sha256": w.digest(public_raw),
                        "operation_binding_sha256": w.digest(w.codec(expected_binding)),
                        "observation": "INCOMPLETE_OR_REFUSED", "eligibility": "UNDETERMINED_INCOMPLETE_OBSERVATION",
                        "reason_codes": [error.code], "source_effect_authority": "NONE", "original_acceptance": False,
                        "historical_before_cut_independently_witnessed": False}
        recut = {"schema": RECUT_SCHEMA_NAME, "binding": expected_binding,
                 "producer_private_sha256": w.digest(raw), "public_sha256": w.digest(public_raw),
                 "producer_carrier": witness, "before": before, "after": after,
                 "source_effect_authority": "NONE", "historical_before_cut_independently_witnessed": False}
        w.validate(recut, RECUT_SCHEMA)
        recut_raw = w.codec(recut)
        w.require(len(recut_raw) <= w.PRIVATE_LIMIT, "RECUT_CARRIER_BYTE_BOUND")
        decision["independent_receipt_sha256"] = w.digest(recut_raw)
        w.validate(decision, DECISION_SCHEMA)
        final_raw, final_witness = carriers.read_producer()
        w.require(final_raw == raw and final_witness == witness, "PRIVATE_CARRIER_CHANGED")
        carriers.check_before_output()
        carriers.write(w.RECUT_NAME, recut_raw, w.PRIVATE_LIMIT)
        carriers.write(w.DECISION_NAME, w.codec(decision), w.PUBLIC_LIMIT)
        carriers.inventory(expected={w.RECEIPT_NAME, w.RECUT_NAME, w.DECISION_NAME})
        final_directory = identity(os.fstat(carriers.fd))
        w.require(final_directory == identity(os.stat("private", dir_fd=episode_fd, follow_symlinks=False)) and
                  all(final_directory[key] == carriers.before[key] for key in ("dev", "ino", "uid", "gid", "mode", "nlink")),
                  "PRIVATE_DIRECTORY_CHANGED")
        return decision
    finally:
        carriers.close()


def main(argv=None):
    parser = argparse.ArgumentParser(description="Independent D0 receiver; requires separate same-job root admission.")
    parser.add_argument("--admitted-fixed-data-operation", action="store_true")
    for name in ("episode", "binding", "public", "schema"):
        parser.add_argument("--" + name + "-fd", type=int, required=True)
    args = parser.parse_args(argv)
    w.require(args.admitted_fixed_data_operation, "ROOT_ADMISSION_REQUIRED")
    w.require(len({args.episode_fd, args.binding_fd, args.public_fd, args.schema_fd}) == 4 and
              min(args.episode_fd, args.binding_fd, args.public_fd, args.schema_fd) >= 3, "CALLER_FD_POPULATION")
    schema_bytes, _ = read_descriptor(args.schema_fd, w.PUBLIC_LIMIT)
    w.require(w.digest(schema_bytes) == w.PINS["public_schema_sha256"], "PUBLIC_SCHEMA_DIGEST")
    binding_raw, _ = read_descriptor(args.binding_fd, w.PUBLIC_LIMIT)
    binding = w.decode(binding_raw, w.PUBLIC_LIMIT)
    public_raw, _ = read_descriptor(args.public_fd, w.PUBLIC_LIMIT)
    result = receive(args.episode_fd, public_raw, binding, schema_bytes)
    # Outputs remain in private carriers. Only closed states/codes go to stdout.
    print(json.dumps({"observation": result["observation"], "eligibility": result["eligibility"],
                      "reason_codes": result["reason_codes"]}, sort_keys=True))
    return 0 if result["observation"] == "RECEIVED_FIXED_HOST_INPUTS" else 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except w.Refusal as error:
        print(json.dumps({"observation": "INCOMPLETE_OR_REFUSED", "eligibility": "UNDETERMINED_INCOMPLETE_OBSERVATION",
                          "reason_codes": [error.code]}, sort_keys=True))
        raise SystemExit(2)
    except OSError as error:
        print(json.dumps({"observation": "INCOMPLETE_OR_REFUSED", "eligibility": "UNDETERMINED_INCOMPLETE_OBSERVATION",
                          "reason_codes": ["RECEIVER_OS_ERROR"], "errno": error.errno}, sort_keys=True))
        raise SystemExit(2)
