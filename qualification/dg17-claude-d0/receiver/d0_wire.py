"""Independent Claude D0 wire and relation implementation. No filesystem I/O.

This module consumes data. It grants no effect, execution, or acceptance authority.
The unchanged public schema is supplemented by strict full-string semantics.
"""
from __future__ import annotations
import copy
import errno
import hashlib
import json
import re
import stat

PER_FILE = 8 * 1024 * 1024
TOTAL_FILES = 32 * 1024 * 1024
PUBLIC_LIMIT = 16 * 1024
PRIVATE_LIMIT = PER_FILE
MAX_DEPTH = 16
MAX_ALIASES = 8
MAX_WALK = (MAX_ALIASES + 1) * (MAX_DEPTH + 1)
MAX_READS = PER_FILE // 65536 + 1
MAX_ENTRIES = 64
RECEIPT_NAME = "D0_PRIVATE_RECEIPT.json"
RECUT_NAME = "D0_INDEPENDENT_RECEIVER_RECEIPT.json"
DECISION_NAME = "D0_ELIGIBILITY.json"
FIXED = (
    ("USR_BIN_BASH", "/usr/bin/bash", "BASH"),
    ("BIN_BASH", "/bin/bash", "BASH_ALIAS"),
    ("USR_BIN_PYTHON3", "/usr/bin/python3", "PYTHON"),
    ("BIN_PYTHON3", "/bin/python3", "PYTHON_ALIAS"),
    ("ETC_PROFILE", "/etc/profile", "STARTUP"),
    ("ETC_BASH_BASHRC", "/etc/bash.bashrc", "STARTUP"),
    ("ETC_BASH_BASH_LOGOUT", "/etc/bash.bash_logout", "STARTUP"),
    ("ETC_PROFILE_D", "/etc/profile.d", "METADATA"),
    ("USR_BIN_ZSH", "/usr/bin/zsh", "INFORMATIONAL"),
    ("BIN_ZSH", "/bin/zsh", "INFORMATIONAL"),
    ("USR_LOCAL_BIN_BASH", "/usr/local/bin/bash", "INFORMATIONAL"),
    ("USR_LOCAL_BIN_ZSH", "/usr/local/bin/zsh", "INFORMATIONAL"),
    ("OPT_HOMEBREW_BIN_BASH", "/opt/homebrew/bin/bash", "INFORMATIONAL"),
    ("OPT_HOMEBREW_BIN_ZSH", "/opt/homebrew/bin/zsh", "INFORMATIONAL"),
)
FIXED_MAP = {row[0]: row[1:] for row in FIXED}
HELPERS = {"BASH", "BASH_ALIAS", "PYTHON", "PYTHON_ALIAS"}
PUBLIC_SCHEMA_NAME = "dg17.claude.routing.fixed-host-census.v1"
PRIVATE_SCHEMA_NAME = "dg17.claude.d0.private-receipt.v1"
BINDING_SCHEMA_NAME = "dg17.claude.d0.operation-binding.v1"
PINS = {
    "contract_sha256": "65a6f7cf464e7edf86073ac9522fdb789e421f0f2de7128b044f19f63cd4a997",
    "addendum_sha256": "2492fc4850704a6d0e5a7051a26cc3e97765a5cc70961eede6c93e942820d773",
    "public_schema_sha256": "183ffd10eec823f93f15a62641fb545130540fa06927b513f49e4c60c650e44d",
    "wire_clarification_sha256": "d7dc6aec2439be84ffe902094a1900c8c416099ac4f54e7b1740e22cfd005205",
}

class Refusal(ValueError):
    """Closed, nonsecret failure code only."""
    def __init__(self, code):
        super().__init__(code)
        self.code = code

def require(value, code):
    if not value:
        raise Refusal(code)

def digest(raw):
    return hashlib.sha256(raw).hexdigest()

def codec(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode("ascii")

def _pairs(pairs):
    result = {}
    for k, v in pairs:
        require(k not in result, "DUPLICATE_JSON_KEY")
        result[k] = v
    return result

def _integer(text):
    require(len(text.lstrip("-")) <= 20, "JSON_INTEGER_BOUND")
    return int(text)

def _number(_):
    raise Refusal("NONINTEGER_JSON_NUMBER")

def decode(raw, limit):
    require(type(raw) is bytes and 0 < len(raw) <= limit, "CARRIER_BYTE_BOUND")
    # Bound nesting before allocating JSON containers; braces inside strings do not count.
    depth = 0
    quoted = escaped = False
    for char in raw:
        if quoted:
            if escaped:
                escaped = False
            elif char == 92:
                escaped = True
            elif char == 34:
                quoted = False
        elif char == 34:
            quoted = True
        elif char in (91, 123):
            depth += 1
            require(depth <= 20, "JSON_NESTING_BOUND")
        elif char in (93, 125):
            depth -= 1
            require(depth >= 0, "JSON_NESTING_INVALID")
    try:
        result = json.loads(raw.decode("ascii"), object_pairs_hook=_pairs,
                            parse_int=_integer, parse_float=_number,
                            parse_constant=_number)
    except Refusal:
        raise
    except (UnicodeError, ValueError, RecursionError):
        raise Refusal("JSON_INVALID") from None
    require(codec(result) == raw, "NONCANONICAL_JSON")
    return result

def obj(properties):
    return {"type": "object", "additionalProperties": False,
            "properties": properties, "required": list(properties)}

def integer(low, high):
    return {"type": "integer", "minimum": low, "maximum": high}

def nullable(spec):
    return {"anyOf": [spec, {"type": "null"}]}

def array(spec, maximum):
    return {"type": "array", "items": spec, "maxItems": maximum}

HASH = {"type": "string", "minLength": 64, "maxLength": 64,
        "pattern": "[0-9a-f]{64}"}
CODE = {"type": "string", "minLength": 1, "maxLength": 96,
        "pattern": "[A-Z][A-Z0-9_]{0,95}"}
PATH = {"type": "string", "minLength": 1, "maxLength": 4096,
        "pattern": "[\\x20-\\x7e]+"}
U64 = integer(0, 2**64 - 1)
U32 = integer(0, 2**32 - 1)
ERRNO = integer(1, 4095)
BOOL = {"type": "boolean"}
IDENTITY = obj({"dev": U64, "ino": U64, "uid": U32, "gid": U32,
                "mode": integer(0, 65535), "nlink": U64,
                "size": integer(0, 2**63 - 1),
                "mtime_ns": integer(-(2**63), 2**63 - 1),
                "ctime_ns": integer(-(2**63), 2**63 - 1)})
PROBE = obj({"identity": nullable(IDENTITY), "errno": nullable(ERRNO)})
ERROR = obj({"code": CODE, "errno": nullable(ERRNO)})
NODE = obj({"path": PATH, "before": PROBE, "after": nullable(PROBE),
            "directory_before": nullable(PROBE), "directory_after": nullable(PROBE)})
LINK_PROBE = obj({"value": nullable(PATH), "errno": nullable(ERRNO)})
ALIAS = obj({"walk_index": integer(0, MAX_WALK - 1),
             "before": LINK_PROBE, "after": nullable(LINK_PROBE)})
CAPABILITY = obj({"state": {"enum": ["EMPTY", "NONEMPTY", "NO_DATA", "UNSUPPORTED", "ERROR"]},
                  "length": nullable(integer(0, 65536)), "sha256": nullable(HASH),
                  "errno": nullable(ERRNO)})
BODY = obj({"fd_before": nullable(PROBE), "fd_after": nullable(PROBE),
            "read_lengths": array(integer(0, 65536), MAX_READS),
            "read_errno": nullable(ERRNO), "bytes_read": integer(0, PER_FILE + 1),
            "eof": BOOL, "sha256": nullable(HASH),
            "prefix_hex": {"type": "string", "maxLength": 40, "pattern": "(?:[0-9a-f]{2})*"},
            "x_ok": nullable(BOOL), "access_errno": nullable(ERRNO),
            "capability": nullable(CAPABILITY), "error": nullable(ERROR)})
CUT = obj({"walk": array(NODE, MAX_WALK), "aliases": array(ALIAS, MAX_ALIASES),
           "body": nullable(BODY), "terminal": nullable(ERROR)})
BINDING = obj({
    "schema": {"const": BINDING_SCHEMA_NAME},
    "operation_id": CODE,
    "run_id": {"type": "string", "minLength": 1, "maxLength": 20, "pattern": "[0-9]+"},
    "run_attempt": integer(1, 2**31 - 1),
    "job_id": {"type": "string", "minLength": 1, "maxLength": 96, "pattern": "[A-Za-z0-9_.-]+"},
    "host_instance_sha256": HASH,
    "host_image": {"type": "string", "minLength": 1, "maxLength": 128, "pattern": "[\\x20-\\x7e]+"},
    "platform": {"const": "linux"},
    "source_commit": {"type": "string", "minLength": 40, "maxLength": 40, "pattern": "[0-9a-f]{40}"},
    "receiver_bundle_sha256": HASH,
    "evidence_uid": U32, "evidence_gid": U32,
    "execution_uid": U32, "execution_gid": U32,
    "host_arch": obj({"elf_class": {"enum": [32, 64]},
                      "elf_endian": {"enum": ["LITTLE", "BIG"]},
                      "elf_machine": integer(0, 65535)}),
    **{key: {"const": value} for key, value in PINS.items()},
})
RECORD = obj({"fixed_id": {"enum": list(FIXED_MAP)},
              "before": nullable(CUT), "after": nullable(CUT)})
RECUT_RECORD = obj({"fixed_id": {"enum": list(FIXED_MAP)}, "cut": CUT})
RECUT_RECORDS = array(RECUT_RECORD, 14)
PRIVATE_SCHEMA = {"$schema": "https://json-schema.org/draft/2020-12/schema",
                  "$comment": "All patterns require full-string matching in d0_wire.validate; encoded carrier <=8388608 bytes.",
                  **obj({"schema": {"const": PRIVATE_SCHEMA_NAME}, "binding": BINDING,
                         "records": array(RECORD, 14),
                         "retained_evidence_files": {"const": [RECEIPT_NAME]},
                         "root_failure": nullable(CODE)})}

PUBLIC_ROW_KEYS = ("fixed_id", "present", "kind", "uid", "gid", "mode", "nlink", "dev", "ino",
                   "bytes", "sha256", "elf_class", "elf_endian", "elf_machine",
                   "file_capabilities_absent", "physical_ancestry_received", "canonical_identity_sha256",
                   "alias_hops", "before_after_equal", "error_code", "errno")

def validate(value, spec):
    """Small closed-schema evaluator: exact Python JSON types and full matches."""
    if "anyOf" in spec:
        for choice in spec["anyOf"]:
            try:
                validate(value, choice)
                return
            except Refusal:
                pass
        raise Refusal("WIRE_TYPE_OR_VALUE")
    if "const" in spec:
        # type-sensitive recursively; Python False == 0 must never satisfy const.
        require(codec(value) == codec(spec["const"]), "WIRE_CONSTANT")
    if "enum" in spec:
        require(any(codec(value) == codec(v) for v in spec["enum"]), "WIRE_ENUM")
    typ = spec.get("type")
    types = {"object": dict, "array": list, "string": str, "integer": int,
             "boolean": bool, "null": type(None)}
    if typ:
        require(type(value) is types[typ], "WIRE_TYPE")
    if typ == "object":
        require(set(value) == set(spec["properties"]), "WIRE_FIELDS")
        for key, child in spec["properties"].items():
            validate(value[key], child)
    elif typ == "array":
        require(len(value) <= spec["maxItems"], "WIRE_ARRAY_BOUND")
        for item in value:
            validate(item, spec["items"])
    elif typ == "string":
        require(spec.get("minLength", 0) <= len(value) <= spec.get("maxLength", 2**31), "WIRE_STRING_BOUND")
        if "pattern" in spec:
            require(re.fullmatch(spec["pattern"], value, flags=re.ASCII) is not None, "WIRE_STRING_LANGUAGE")
    elif typ == "integer":
        require(spec["minimum"] <= value <= spec["maximum"], "WIRE_INTEGER_BOUND")

def kind(identity):
    mode = identity["mode"]
    if stat.S_ISREG(mode): return "REGULAR"
    if stat.S_ISDIR(mode): return "DIRECTORY"
    if stat.S_ISLNK(mode): return "SYMLINK"
    return "OTHER"

def protected(identity):
    return identity["uid"] == 0 and not (identity["mode"] & 0o022)

def clean_path(path):
    require(type(path) is str and path.startswith("/") and len(path) <= 4096,
            "PATH_LANGUAGE")
    require(all(32 <= ord(c) <= 126 for c in path), "PATH_LANGUAGE")
    parts = path.split("/")[1:]
    if path == "/": return []
    require(all(p and p not in (".", "..") and len(p) <= 255 for p in parts), "PATH_LANGUAGE")
    require(len(parts) <= MAX_DEPTH, "ANCESTOR_BOUND")
    return parts

def alias_destination(link_path, target, suffix):
    require(type(target) is str and 0 < len(target) <= 4096 and
            all(32 <= ord(c) <= 126 for c in target), "ALIAS_LANGUAGE")
    # Do not lexically collapse an unresolved component followed by ..: that
    # can change POSIX symlink resolution. Unsupported spellings stop before
    # opening a target; they are not authority to substitute a lexical path.
    target_parts = target.split("/")[1:] if target.startswith("/") else target.split("/")
    require(all(p and p not in (".", "..") for p in target_parts), "ALIAS_SPELLING_UNSUPPORTED")
    parts = [] if target.startswith("/") else clean_path(link_path)[:-1]
    for p in target_parts:
        if p in ("", "."): continue
        if p == "..":
            if parts: parts.pop()
        else:
            require(len(p) <= 255, "PATH_LANGUAGE")
            parts.append(p)
    parts.extend(suffix)
    result = "/" + "/".join(parts)
    clean_path(result)
    return result

def _probe(probe):
    require(type(probe) is dict and ((probe["identity"] is None) != (probe["errno"] is None)),
            "PROBE_RELATION")
    return probe["identity"]

def _stable(node, needs_directory):
    before = _probe(node["before"])
    require(node["after"] is not None, "MISSING_NODE_BOOKEND")
    _probe(node["after"])
    require(node["before"] == node["after"], "NODE_CHANGED")
    if needs_directory:
        require(before is not None and kind(before) == "DIRECTORY", "ANCESTOR_NOT_DIRECTORY")
        require(node["directory_before"] is not None and node["directory_after"] is not None,
                "DIRECTORY_DESCRIPTOR_MISSING")
        require(_probe(node["directory_before"]) == before and
                _probe(node["directory_after"]) == before, "DIRECTORY_DESCRIPTOR_CHANGED")
    else:
        require(node["directory_before"] is None and node["directory_after"] is None,
                "UNEXPECTED_DIRECTORY_OPEN")
    return before

def elf(prefix_hex):
    prefix = bytes.fromhex(prefix_hex)
    if len(prefix) < 4 or prefix[:4] != b"\x7fELF":
        return {"status": "NOT_ELF", "elf_class": None, "elf_endian": None, "elf_machine": None}
    if len(prefix) < 20 or prefix[4] not in (1, 2) or prefix[5] not in (1, 2) or prefix[6] != 1:
        return {"status": "MALFORMED_ELF", "elf_class": None, "elf_endian": None, "elf_machine": None}
    order = "little" if prefix[5] == 1 else "big"
    return {"status": "ELF", "elf_class": 32 if prefix[4] == 1 else 64,
            "elf_endian": "LITTLE" if prefix[5] == 1 else "BIG",
            "elf_machine": int.from_bytes(prefix[18:20], order)}

def capability_absent(cap):
    require(cap is not None, "CAPABILITY_MISSING")
    state = cap["state"]
    if state in ("EMPTY", "NONEMPTY"):
        require(cap["errno"] is None and cap["length"] is not None and cap["sha256"] is not None,
                "CAPABILITY_RELATION")
        if state == "EMPTY":
            require(cap["length"] == 0 and cap["sha256"] == digest(b""), "CAPABILITY_RELATION")
            return True
        require(cap["length"] > 0, "CAPABILITY_RELATION")
        return False
    if state in ("NO_DATA", "UNSUPPORTED"):
        expected = errno.ENODATA if state == "NO_DATA" else errno.ENOTSUP
        require(cap["errno"] == expected and cap["length"] == 0 and cap["sha256"] is None,
                "CAPABILITY_RELATION")
        return True
    raise Refusal("CAPABILITY_UNKNOWN")

def complete_body(body, target, helper):
    require(body is not None, "BODY_MISSING")
    if body["error"] is not None: raise Refusal(body["error"]["code"])
    require(body["fd_before"] is not None and body["fd_after"] is not None,
            "BODY_DESCRIPTOR_MISSING")
    require(_probe(body["fd_before"]) == target and _probe(body["fd_after"]) == target,
            "BODY_DESCRIPTOR_CHANGED")
    lengths = body["read_lengths"]
    require(lengths and lengths[-1] == 0 and all(n > 0 for n in lengths[:-1]), "EOF_MISSING")
    require(body["eof"] and body["read_errno"] is None and
            sum(lengths) == body["bytes_read"] == target["size"] <= PER_FILE and
            body["sha256"] is not None, "BODY_NOT_COMPLETE")
    require(len(body["prefix_hex"]) == 2 * min(20, body["bytes_read"]), "PREFIX_LENGTH")
    if helper:
        require(type(body["x_ok"]) is bool and body["access_errno"] is None, "EXEC_ACCESS_UNKNOWN")
        capabilities = capability_absent(body["capability"])
    else:
        require(body["x_ok"] is None and body["access_errno"] is None and body["capability"] is None,
                "UNREQUESTED_HELPER_OBSERVATION")
        capabilities = None
    return {"bytes": body["bytes_read"], "sha256": body["sha256"],
            "elf": elf(body["prefix_hex"]) if helper else None,
            "prefix_hex": body["prefix_hex"] if helper else None,
            "x_ok": body["x_ok"], "capability": body["capability"],
            "file_capabilities_absent": capabilities}

def derive_cut(fixed_id, cut):
    """Consume the exact walk as a state machine; no claimed leaf/canonical index is trusted."""
    require(cut is not None, "CUT_MISSING")
    validate(cut, CUT)
    if cut["terminal"] is not None: raise Refusal(cut["terminal"]["code"])
    requested, role = FIXED_MAP[fixed_id]
    helper = role in HELPERS
    nodes, aliases = cut["walk"], cut["aliases"]
    alias_by_node = {}
    for a in aliases:
        require(a["walk_index"] not in alias_by_node, "DUPLICATE_ALIAS")
        alias_by_node[a["walk_index"]] = a
    pending = clean_path(requested)
    position = 0
    seen_aliases = set()
    requested_leaf = None
    all_protected = True
    final_ancestors = []
    final_target = None
    missing = None
    # Each reset consumes one alias; loops cannot consume an unbounded path population.
    for hop in range(MAX_ALIASES + 1):
        require(position < len(nodes), "WALK_TRUNCATED")
        require(nodes[position]["path"] == "/", "WALK_ROOT")
        root = _stable(nodes[position], True)
        all_protected = all_protected and protected(root)
        ancestors = [{"path": "/", "identity": root}]
        position += 1
        require(pending, "HELPER_TARGET_IS_ROOT")
        restart = False
        for i, component in enumerate(pending):
            path = "/" + "/".join(pending[:i + 1])
            require(position < len(nodes) and nodes[position]["path"] == path, "WALK_PATH")
            index = position
            node = nodes[index]
            identity = _probe(node["before"])
            leaf = i == len(pending) - 1
            is_link = identity is not None and kind(identity) == "SYMLINK"
            follow = is_link and (helper or (not leaf and path == "/bin" and requested.startswith("/bin/")))
            stable = _stable(node, identity is not None and not leaf and not is_link)
            position += 1
            if stable is None:
                require(node["before"]["errno"] == errno.ENOENT, "OBSERVATION_OS_ERROR")
                require(index not in alias_by_node, "ALIAS_ON_ABSENCE")
                missing = {"path": path, "errno": errno.ENOENT,
                           "parent": copy.deepcopy(ancestors[-1]), "chain": copy.deepcopy(ancestors)}
                final_ancestors = ancestors
                break
            if leaf and requested_leaf is None:
                requested_leaf = {"path": path, "identity": stable}
            if follow:
                require(hop < MAX_ALIASES and index in alias_by_node, "ALIAS_BOUND_OR_MISSING")
                a = alias_by_node[index]
                require(a["after"] is not None and a["before"] == a["after"] and
                        a["before"]["errno"] is None and a["before"]["value"] is not None,
                        "READLINK_CHANGED_OR_ERROR")
                destination = alias_destination(path, a["before"]["value"], pending[i + 1:])
                if not helper:
                    # Only /bin itself may be resolved for metadata roles; no leaf target is read.
                    require(path == "/bin" and alias_destination(path, a["before"]["value"], []) == "/usr/bin",
                            "UNSELECTED_ANCESTOR_ALIAS")
                    require(len(seen_aliases) == 0, "UNSELECTED_ANCESTOR_ALIAS")
                # Symlink mode bits are not Linux write permission. Custody is
                # the bookended protected parent plus the link owner.
                all_protected = all_protected and stable["uid"] == 0
                seen_aliases.add(index)
                pending = clean_path(destination)
                restart = True
                break
            require(index not in alias_by_node, "UNAUTHORIZED_READLINK")
            if not leaf:
                require(not is_link, "UNSELECTED_ANCESTOR_ALIAS")
                require(kind(stable) == "DIRECTORY", "ANCESTOR_NOT_DIRECTORY")
                all_protected = all_protected and protected(stable)
                ancestors.append({"path": path, "identity": stable})
            else:
                final_target = {"path": path, "identity": stable}
                final_ancestors = ancestors
        if restart: continue
        break
    require(position == len(nodes) and set(alias_by_node) == seen_aliases, "EXTRA_WALK_OBSERVATION")
    require(len(final_ancestors) <= MAX_DEPTH, "ANCESTOR_BOUND")
    require(requested_leaf is not None or missing is not None, "LEAF_UNOBSERVED")
    present = requested_leaf is not None
    identity = requested_leaf["identity"] if present else None
    target = final_target
    body_needed = (helper or role == "STARTUP") and target is not None and kind(target["identity"]) == "REGULAR"
    body = complete_body(cut["body"], target["identity"], helper) if body_needed else None
    if not body_needed: require(cut["body"] is None, "UNREQUESTED_BODY_READ")
    canonical = None
    if helper and body is not None:
        canonical = {"path": target["path"], "physical_ancestors": final_ancestors,
                     "identity": target["identity"], "bytes": body["bytes"], "sha256": body["sha256"],
                     "elf": body["elf"], "prefix_hex": body["prefix_hex"],
                     "capability": body["capability"], "x_ok": body["x_ok"]}
    return {"present": present, "identity": identity, "target": target,
            "missing": missing, "ancestors": final_ancestors,
            "protected_ancestry": bool(all_protected), "alias_hops": len(seen_aliases),
            "body": body, "canonical": canonical,
            "canonical_identity_sha256": digest(codec(canonical)) if canonical is not None else None}

def semantic_cut(cut):
    """Ignore syscall chunk partition only; all observations and errors still have to validate."""
    value = copy.deepcopy(cut)
    if value is not None and value["body"] is not None:
        value["body"].pop("read_lengths")
    return value

def _base_row(fixed_id):
    row = {key: None for key in PUBLIC_ROW_KEYS}
    row.update(fixed_id=fixed_id, kind="UNKNOWN", alias_hops=0,
               physical_ancestry_received=False, before_after_equal=False)
    return row

def _error_errno(cut):
    if cut is None: return None
    if cut["terminal"] is not None: return cut["terminal"]["errno"]
    if cut["body"] is not None and cut["body"]["error"] is not None:
        return cut["body"]["error"]["errno"]
    for node in cut["walk"]:
        for p in (node["before"], node["after"], node["directory_before"], node["directory_after"]):
            if p is not None and p["errno"] not in (None, errno.ENOENT): return p["errno"]
    return None

def project_record(record):
    fixed_id = record["fixed_id"]
    row = _base_row(fixed_id)
    try:
        before = derive_cut(fixed_id, record["before"])
        after = derive_cut(fixed_id, record["after"])
        equal = semantic_cut(record["before"]) == semantic_cut(record["after"])
        require(equal, "OBSERVATION_CHANGED")
        row.update(present=after["present"], kind=kind(after["identity"]) if after["present"] else "ABSENT",
                   before_after_equal=True, physical_ancestry_received=after["protected_ancestry"],
                   # The immutable absence relation explicitly projects zero. Traversal remains private.
                   alias_hops=after["alias_hops"] if after["present"] else 0)
        if after["present"]:
            for key in ("uid", "gid", "mode", "nlink", "dev", "ino"):
                row[key] = after["identity"][key]
            if after["body"] is not None:
                row["bytes"] = after["body"]["bytes"]
                row["sha256"] = after["body"]["sha256"]
                row["canonical_identity_sha256"] = after["canonical_identity_sha256"]
                if after["body"]["elf"] is not None:
                    for key in ("elf_class", "elf_endian", "elf_machine"):
                        row[key] = after["body"]["elf"][key]
                    row["file_capabilities_absent"] = after["body"]["file_capabilities_absent"]
        return row, after, None
    except Refusal as exc:
        row["error_code"] = exc.code
        row["errno"] = _error_errno(record.get("after")) or _error_errno(record.get("before"))
        return row, None, exc.code

def population_budget(records):
    for which in ("before", "after"):
        unique = {}
        for record in records:
            cut = record[which]
            if cut is None or cut["body"] is None or cut["body"]["fd_before"] is None: continue
            p = cut["body"]["fd_before"]
            identity = p["identity"]
            if identity is None: continue
            key = (identity["dev"], identity["ino"])
            unique[key] = max(unique.get(key, 0), identity["size"])
        require(sum(unique.values()) <= TOTAL_FILES, "REGULAR_POPULATION_BOUND")

def derive_public(receipt, private_digest):
    validate(receipt, PRIVATE_SCHEMA)
    validate(private_digest, HASH)
    ids = [r["fixed_id"] for r in receipt["records"]]
    failure = receipt["root_failure"]
    if len(ids) != 14 or set(ids) != set(FIXED_MAP): failure = failure or "FIXED_POPULATION_INCOMPLETE"
    if len(ids) != len(set(ids)): failure = failure or "FIXED_POPULATION_DUPLICATE"
    try: population_budget(receipt["records"])
    except Refusal as exc: failure = failure or exc.code
    rows, facts = [], {}
    # Preserve duplicate nonpass records; never deduplicate them into an alleged success.
    for record in sorted(receipt["records"], key=lambda r: list(FIXED_MAP).index(r["fixed_id"])):
        row, fact, issue = project_record(record)
        rows.append(row)
        if issue: failure = failure or issue
        if fact is not None: facts[record["fixed_id"]] = fact
    result = {"schema": PUBLIC_SCHEMA_NAME,
              "status": "RECEIVED_FIXED_HOST_INPUTS" if failure is None else "INCOMPLETE_OR_REFUSED",
              "rows": rows, "private_receipt_sha256": private_digest,
              "body_content_published": False, "startup_semantics_accepted": False,
              "native_processes_started": 0, "target_commands_started": 0,
              "source_effect_authority": "NONE", "failure": failure}
    require(len(codec(result)) <= PUBLIC_LIMIT, "PUBLIC_BYTE_BOUND")
    return result, facts

def public_projection_matches(observed, derived):
    """Public rows are received by ID; array ordering confers no authority."""
    if {k: v for k, v in observed.items() if k != "rows"} != {k: v for k, v in derived.items() if k != "rows"}:
        return False
    first, second = observed["rows"], derived["rows"]
    if len(first) != len(second): return False
    a = {row["fixed_id"]: row for row in first}
    b = {row["fixed_id"]: row for row in second}
    if len(a) != len(first) or len(b) != len(second):
        # Preserve contradictory duplicate rows as nonpass evidence; never deduplicate.
        return first == second
    return a == b

def validate_public(value, schema):
    validate(value, schema)
    # json-schema patterns in the immutable schema are supplementary to full strings.
    for code in [value["failure"]] + [r["error_code"] for r in value["rows"]]:
        if code is not None: validate(code, CODE)
    for h in [value["private_receipt_sha256"]] + [r[k] for r in value["rows"] for k in ("sha256", "canonical_identity_sha256")]:
        if h is not None: validate(h, HASH)

def eligibility(public, facts, binding):
    if public["status"] != "RECEIVED_FIXED_HOST_INPUTS":
        return "UNDETERMINED_INCOMPLETE_OBSERVATION", ["OBSERVATION_INCOMPLETE"]
    reasons = []
    for fixed_id in ("USR_BIN_BASH", "USR_BIN_PYTHON3"):
        f = facts[fixed_id]
        c = f["canonical"]
        if not f["present"] or c is None:
            reasons.append(fixed_id + "_TARGET_UNAVAILABLE")
            continue
        t = c["identity"]
        if not (protected(t) and f["protected_ancestry"] and not (t["mode"] & 0o6000)
                and c["x_ok"] and f["body"]["file_capabilities_absent"]):
            reasons.append(fixed_id + "_TRUST_PREDICATE")
        if fixed_id == "USR_BIN_BASH":
            e = c["elf"]
            if c["bytes"] == 0 or e["status"] != "ELF" or any(e[k] != binding["host_arch"][k] for k in binding["host_arch"]):
                reasons.append("USR_BIN_BASH_ELF_ARCHITECTURE")
    for alias_id, selected in (("BIN_BASH", "USR_BIN_BASH"), ("BIN_PYTHON3", "USR_BIN_PYTHON3")):
        f = facts[alias_id]
        if f["present"] and (not f["protected_ancestry"] or f["canonical"] is None or f["canonical"] != facts[selected]["canonical"]):
            reasons.append(alias_id + "_TARGET_MISMATCH")
    for fixed_id in ("ETC_PROFILE", "ETC_BASH_BASHRC", "ETC_BASH_BASH_LOGOUT"):
        f = facts[fixed_id]
        if not f["present"]: continue
        t = f["identity"]
        if not (kind(t) == "REGULAR" and f["alias_hops"] == 0 and f["body"] is not None and
                t["uid"] == t["gid"] == 0 and t["nlink"] == 1 and
                not (t["mode"] & 0o7022) and f["protected_ancestry"]):
            reasons.append(fixed_id + "_STARTUP_PREDICATE")
    return ("NOT_ELIGIBLE" if reasons else "ELIGIBLE_FOR_SEPARATELY_REVIEWED_FIXED_VIEW"), reasons

def evaluate(public_raw, private_raw, recut_before, recut_after, expected_binding, public_schema):
    """Pure relation for tests and the admitted receiver, not host observation authority."""
    validate(expected_binding, BINDING)
    receipt = decode(private_raw, PRIVATE_LIMIT)
    validate(receipt, PRIVATE_SCHEMA)
    require(receipt["binding"] == expected_binding, "OPERATION_HOST_BINDING_MISMATCH")
    public = decode(public_raw, PUBLIC_LIMIT)
    validate_public(public, public_schema)
    rebuilt, facts = derive_public(receipt, digest(private_raw))
    require(public_projection_matches(public, rebuilt), "PUBLIC_PROJECTION_MISMATCH")
    independently_complete = rebuilt["status"] == "RECEIVED_FIXED_HOST_INPUTS"
    recut_reason = None
    # Recut population and every role observation are checked, not a caller boolean.
    if independently_complete:
        for recut in (recut_before, recut_after):
            validate(recut, RECUT_RECORDS)
            require(type(recut) is list and len(recut) == 14, "RECUT_POPULATION")
            require([r["fixed_id"] for r in recut] == list(FIXED_MAP), "RECUT_POPULATION")
            for record in recut:
                require(set(record) == {"fixed_id", "cut"}, "RECUT_FIELDS")
                derive_cut(record["fixed_id"], record["cut"])
        by_id = {r["fixed_id"]: r for r in receipt["records"]}
        for first, second in zip(recut_before, recut_after):
            fixed_id = first["fixed_id"]
            if not (semantic_cut(first["cut"]) == semantic_cut(second["cut"]) == semantic_cut(by_id[fixed_id]["after"])):
                independently_complete = False
                recut_reason = "INDEPENDENT_RECUT_MISMATCH"
                break
    if independently_complete:
        state, reasons = eligibility(rebuilt, facts, expected_binding)
    else:
        state, reasons = "UNDETERMINED_INCOMPLETE_OBSERVATION", [recut_reason or "OBSERVATION_INCOMPLETE"]
    decision = {"schema": "dg17.claude.d0.receiver-decision.v1",
                "private_receipt_sha256": digest(private_raw), "public_receipt_sha256": digest(public_raw),
                "operation_binding_sha256": digest(codec(expected_binding)),
                "observation": "RECEIVED_FIXED_HOST_INPUTS" if independently_complete else "INCOMPLETE_OR_REFUSED",
                "eligibility": state, "reason_codes": reasons,
                "source_effect_authority": "NONE", "original_acceptance": False,
                "historical_before_cut_independently_witnessed": False}
    return decision
