"""Pure verification of one evidence-bound desktop-generated pipe transition.

No IO, native invocation, configuration write, event production, or authority
grant occurs here. The caller must independently bind the supplied prior record,
native reads, file reads, desktop process, and original observation ancestry.
Raw configuration exists only in arguments and temporary in-memory copies.
"""
from copy import deepcopy
import hashlib
import json
import re
import tomllib

FEATURE = "retain_client_developer_messages"
FIELD = "mcp_servers.node_repl.env.SKY_CUA_NATIVE_PIPE_DIRECTORY"
FIELD_PARTS = tuple(FIELD.split("."))
# Exact shipped main-LM8MUIFp.js: UUID pipe construction feeds the Windows
# node_repl environment, then config/batchWrite replaces the server config.
# This producer binding does not exempt those whole-server edits: the inverse
# checks below still require that only the one measured pipe value changed.
PRODUCER = {'asar_sha256': 'b8aeb817cd1ee6ef50efe8a97985d3be41de89688a5addfe0a444e1e52348096', 'member_sha256': 'c71bf3ffecef5fd390b4cd16d120d39dce30d30bffe3c563c8c74c1b691da018'}
PIPE_PATTERN = re.compile(
    r"\\\\\.\\pipe\\codex-computer-use-"
    r"[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\Z"
)
HASH_PATTERN = re.compile(r"[0-9a-f]{64}\Z")
MAX_CONFIG_BYTES = 2 * 1024 * 1024
_RELATION_PREDICATES = frozenset({"UNKNOWN", "PHYSICAL_INVERSE", "USER_CONFIG_INVERSE",
                                 "RESOLVED_CONFIG_INVERSE", "ORIGIN_BINDING"})


class ConfigTransitionRefusal(ValueError):
    """Safe fixed-message refusal, never containing raw configuration."""
    def __init__(self, message, predicate="UNKNOWN"):
        self.predicate = predicate if predicate in _RELATION_PREDICATES else "UNKNOWN"
        super().__init__(message)


def _require(condition, message, *, predicate="UNKNOWN"):
    if not condition:
        raise ConfigTransitionRefusal(message, predicate)


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def _sha(raw):
    return hashlib.sha256(raw).hexdigest()


def _jsha(value):
    return _sha(_canonical(value))


def _is_hash(value):
    return isinstance(value, str) and HASH_PATTERN.fullmatch(value) is not None


def _feature(config):
    if config is None:
        return None
    _require(isinstance(config, dict), "native config is not an object")
    features = config.get("features", {})
    _require(isinstance(features, dict), "native features are not an object")
    return features.get(FEATURE)


def _field(config):
    value = config
    for part in FIELD_PARTS:
        _require(isinstance(value, dict) and part in value, "exact generated field missing")
        value = value[part]
    return value


def _inverse(config, old, new):
    _require(_field(config) == new, "native generated field does not match witness")
    encoded = _canonical(config)
    old_token, new_token = old.rsplit("\\", 1)[-1], new.rsplit("\\", 1)[-1]
    _require(encoded.count(new_token.encode()) == 1 and old_token.encode() not in encoded,
             "generated value is not unique in native config")
    inverse = deepcopy(config)
    node = inverse
    for part in FIELD_PARTS[:-1]:
        node = node[part]
    node[FIELD_PARTS[-1]] = old
    return inverse


def _metadata_check(metadata, content):
    _require(isinstance(metadata, dict), "physical metadata is not an object")
    _require(isinstance(metadata.get("path"), str) and metadata["path"], "physical path missing")
    if metadata.get("exists") is False:
        _require(set(metadata) == {"exists", "path"} and content is None,
                 "absent file metadata or content invalid")
        return
    _require(metadata.get("exists") is True and set(metadata) == {
        "path", "exists", "bytes", "sha256", "mtime_ns"}, "physical metadata shape invalid")
    _require(type(content) is bytes and len(content) <= MAX_CONFIG_BYTES, "physical content invalid")
    _require(type(metadata["bytes"]) is int and metadata["bytes"] == len(content),
             "physical byte count mismatch")
    _require(_is_hash(metadata["sha256"]) and metadata["sha256"] == _sha(content),
             "physical digest mismatch")
    _require(type(metadata["mtime_ns"]) is int and metadata["mtime_ns"] > 0,
             "physical timestamp invalid")


def _physical_map(entries):
    _require(isinstance(entries, list) and 1 <= len(entries) <= 32, "physical file population invalid")
    result = {}
    for entry in entries:
        _require(isinstance(entry, dict) and set(entry) == {"metadata", "content"},
                 "physical read shape invalid")
        metadata, content = entry["metadata"], entry["content"]
        _metadata_check(metadata, content)
        path = metadata["path"]
        _require(path not in result, "duplicate physical path")
        result[path] = entry
    return result


def _layer_paths(source):
    _require(isinstance(source, dict), "native layer source invalid")
    paths = []
    if source.get("file"):
        paths.append(source["file"])
    if source.get("dotCodexFolder"):
        folder = source["dotCodexFolder"]
        _require(isinstance(folder, str) and folder, "native config folder invalid")
        separator = "\\" if "\\" in folder else "/"
        paths.append(folder.rstrip("/\\") + separator + "config.toml")
    _require(all(isinstance(path, str) and path for path in paths), "native file path invalid")
    return paths


def _filter_native(row, physical):
    _require(isinstance(row, dict) and set(row) == {"cwd", "result"}, "native read row shape invalid")
    _require(isinstance(row["cwd"], str) and row["cwd"], "native cwd missing")
    result = row["result"]
    _require(isinstance(result, dict) and isinstance(result.get("config"), dict),
             "native result shape invalid")
    layers = result.get("layers")
    _require(isinstance(layers, list) and 1 <= len(layers) <= 32, "native layer population invalid")
    filtered = []
    for layer in layers:
        _require(isinstance(layer, dict) and {"name", "version", "config"} <= set(layer),
                 "native layer shape invalid")
        _require(set(layer) <= {"name", "version", "config", "disabledReason"},
                 "unsupported native layer metadata")
        paths = _layer_paths(layer["name"])
        _require(all(path in physical for path in paths), "missing physical layer evidence")
        filtered.append({"source": deepcopy(layer["name"]), "version": layer["version"],
                         "disabledReason": layer.get("disabledReason"),
                         "feature": _feature(layer["config"]),
                         "config_sha256": _jsha(layer["config"]),
                         "files": [deepcopy(physical[path]["metadata"]) for path in paths]})
    origins = result.get("origins", {})
    _require(isinstance(origins, dict), "native origins shape invalid")
    return {"cwd": row["cwd"], "feature": _feature(result["config"]), "layers": filtered,
            "full_config_sha256": _jsha(result["config"]),
            "feature_origin": deepcopy(origins.get("features." + FEATURE)),
            "raw_config_persisted": False}


def validate_config_transition(previous_filtered_configs, current_raw_native_results,
                               current_physical_reads, witness):
    """Return (current_filtered_configs, digest_only_evidence), or refuse.

    current_raw_native_results: [read1, read2], each containing two ordered
    {cwd, result} config/read records. current_physical_reads: [files1, files2],
    each containing {metadata: file_observation, content: bytes|None} per file.
    The caller performs the two reads around its source/custody observations;
    passing duplicated data instead is not independent currentness evidence.
    """
    try:
        return _validate(previous_filtered_configs, current_raw_native_results,
                         current_physical_reads, witness)
    except ConfigTransitionRefusal:
        raise
    except (KeyError, TypeError, ValueError, OverflowError, RecursionError):
        raise ConfigTransitionRefusal("malformed config transition input") from None


def _validate(previous, reads, physical_reads, witness):
    observed_config_material(reads, physical_reads)
    return _validate_relation(previous, reads[0], physical_reads[0], witness,
                              material_kind="observed_pair")


def _validate_relation(previous, native, physical_entries, witness, *, material_kind):
    witness_keys = {"schema", "field", "previous_value", "current_value", "user_config_path",
                    "producer", "previous_filtered_configs_sha256", "current_native_results_sha256",
                    "current_physical_metadata_sha256"}
    _require(isinstance(witness, dict) and set(witness) == witness_keys, "witness shape invalid")
    _require(witness["schema"] == "implementaudit.config-pipe-transition.v1" and
             witness["field"] == FIELD and witness["producer"] == PRODUCER,
             "unsupported transition producer or field")
    old, new, user_path = witness["previous_value"], witness["current_value"], witness["user_config_path"]
    _require(all(isinstance(v, str) and PIPE_PATTERN.fullmatch(v) for v in (old, new)) and old != new,
             "pipe transition identity invalid")
    _require(isinstance(user_path, str) and user_path, "user configuration path missing")
    _require(isinstance(previous, list) and len(previous) == 2, "prior cwd population invalid")
    _require(_jsha(previous) == witness["previous_filtered_configs_sha256"], "prior record digest mismatch")
    current_digest = _jsha(native)
    physical = _physical_map(physical_entries)
    physical_digest = _jsha([e["metadata"] for e in physical_entries])
    _require(current_digest == witness["current_native_results_sha256"], "current native witness differs")
    _require(physical_digest == witness["current_physical_metadata_sha256"], "current physical witness differs")
    _require(user_path in physical and physical[user_path]["metadata"]["exists"] is True,
             "current user configuration missing")
    raw = physical[user_path]["content"]
    _require(_field(tomllib.loads(raw.decode("utf8"))) == new, "physical generated field differs")
    old_token, new_token = old.rsplit("\\", 1)[-1].encode(), new.rsplit("\\", 1)[-1].encode()
    _require(raw.count(new_token) == 1 and old_token not in raw, "generated value is not unique in physical config")
    inverse_raw = raw.replace(new_token, old_token)
    inverse_digest = _sha(inverse_raw)
    current = [_filter_native(row, physical) for row in native]
    _require(len({c["cwd"] for c in current}) == 2, "duplicate native cwd")
    used_paths = set()
    for prior, now, row in zip(previous, current, native):
        _require(set(prior) == set(now) and prior["cwd"] == now["cwd"], "prior shape or cwd changed")
        _require(prior["raw_config_persisted"] is False and prior["feature"] is True and now["feature"] is True,
                 "retained lifecycle feature is not unchanged true")
        _require(len(prior["layers"]) == len(now["layers"]), "layer population changed")
        users = 0
        expected_origin = deepcopy(prior["feature_origin"])
        for old_layer, new_layer, raw_layer in zip(prior["layers"], now["layers"], row["result"]["layers"]):
            _require(set(old_layer) == set(new_layer), "filtered layer shape changed")
            for key in ("source", "disabledReason", "feature"):
                _require(old_layer[key] == new_layer[key], "layer source, status, or feature changed")
            used_paths.update(e["path"] for e in new_layer["files"])
            if old_layer["source"].get("type") != "user":
                _require(old_layer == new_layer, "unrelated layer changed")
                continue
            users += 1
            _require(old_layer["source"].get("file") == user_path and
                     len(old_layer["files"]) == len(new_layer["files"]) == 1 and
                     old_layer["files"][0].get("path") == user_path,
                     "user layer does not own exact physical path")
            old_file, new_file = old_layer["files"][0], new_layer["files"][0]
            _require(set(old_file) == set(new_file) and old_file["exists"] is True and
                     old_file["bytes"] == len(inverse_raw) and old_file["sha256"] == inverse_digest and
                     type(old_file["mtime_ns"]) is int and 0 < old_file["mtime_ns"] <= new_file["mtime_ns"],
                     "physical inverse does not reproduce original record", predicate="PHYSICAL_INVERSE")
            _require(_jsha(_inverse(raw_layer["config"], old, new)) == old_layer["config_sha256"],
                     "native user layer inverse differs", predicate="USER_CONFIG_INVERSE")
            _require(old_layer["version"] == "sha256:" + old_layer["config_sha256"] and
                     new_layer["version"] == "sha256:" + new_layer["config_sha256"],
                     "user version is not bound to its exact config")
            if isinstance(expected_origin, dict) and expected_origin.get("name") == old_layer["source"]:
                _require(expected_origin.get("version") == old_layer["version"], "prior feature origin version differs")
                expected_origin["version"] = new_layer["version"]
        _require(users == 1, "exactly one user layer required")
        _require(now["feature_origin"] == expected_origin, "feature origin changed outside exact user version")
        _require(_jsha(_inverse(row["result"]["config"], old, new)) == prior["full_config_sha256"],
                 "native resolved config inverse differs", predicate="RESOLVED_CONFIG_INVERSE")
    _require(used_paths == set(physical), "unrelated or missing physical evidence")
    return current, {
        "schema": "implementaudit.verified-config-transition-evidence.v1",
        "status": "EXACT_CONFIG_TRANSITION_ONLY_NO_AUTHORITY",
        "field": FIELD, "reads_verified": 2 if material_kind == "observed_pair" else 0,
        "material_kind": material_kind,
        "witness_sha256": _jsha(witness), "previous_filtered_configs_sha256": _jsha(previous),
        "current_filtered_configs_sha256": _jsha(current), "current_native_results_sha256": current_digest,
        "current_physical_metadata_sha256": physical_digest,
        "inverse_physical_sha256": inverse_digest,
        "previous_value_sha256": _sha(old.encode()), "current_value_sha256": _sha(new.encode()),
        "raw_config_persisted": False,
    }


def observed_config_material(reads, physical_reads):
    """Check actual supplied pairs; return only filtered facts and minimal binding.

    Acquisition and the temporal independence of these pairs remain caller-owned.
    No in-memory duplication can establish observation authority.
    """
    _require(isinstance(reads, list) and len(reads) == 2 and
             all(isinstance(r, list) and len(r) == 2 for r in reads), "two native reads required")
    _require(_jsha(reads[0]) == _jsha(reads[1]), "current native reads differ")
    _require(isinstance(physical_reads, list) and len(physical_reads) == 2, "two physical reads required")
    physical = _physical_map(physical_reads[0])
    _require(physical == _physical_map(physical_reads[1]), "current physical reads differ")
    _require(_jsha([e["metadata"] for e in physical_reads[0]]) ==
             _jsha([e["metadata"] for e in physical_reads[1]]), "physical ordering differs")
    current = [_filter_native(row, physical) for row in reads[0]]
    _require(len({c["cwd"] for c in current}) == 2, "duplicate native cwd")
    paths = {f["path"] for c in current for layer in c["layers"] for f in layer["files"]}
    _require(paths == set(physical), "unrelated or missing physical evidence")
    pipe, user_path = None, None
    users = [layer for layer in current[0]["layers"] if layer["source"].get("type") == "user"]
    if len(users) == 1:
        user_path = users[0]["source"].get("file")
        try:
            values = [_field(row["result"]["config"]) for row in reads[0]]
            value = _field(tomllib.loads(physical[user_path]["content"].decode("utf8")))
            if all(v == value for v in values) and isinstance(value, str) and PIPE_PATTERN.fullmatch(value):
                pipe = value
        except (ConfigTransitionRefusal, KeyError, TypeError, ValueError, AttributeError):
            pass
    return current, {"schema": "implementaudit.config-acquisition-binding.v1",
        "native_results_sha256": _jsha(reads[0]),
        "physical_metadata_sha256": _jsha([e["metadata"] for e in physical_reads[0]]),
        "filtered_configs_sha256": _jsha(current), "pipe_value": pipe,
        "user_config_path": user_path}


def derive_previous_material(previous, native, physical_entries, witness):
    """Inverse material only: caller must first establish the exact transition.

    This return is derived, never a native/physical observation and never a pair.
    Every filtered native/layer/version/physical fact is checked against previous.
    """
    # Recheck the exact supplied relation before changing any derived material.
    # This pure check is not a new pair or an observed read.
    _validate_relation(previous, native, physical_entries, witness,
                       material_kind="derived_inverse_not_observed")
    old, new, path = witness["previous_value"], witness["current_value"], witness["user_config_path"]
    rows, files = deepcopy(native), deepcopy(physical_entries)
    for row, prior in zip(rows, previous):
        result = row["result"]
        result["config"] = _inverse(result["config"], old, new)
        origins = result.get("origins", {})
        _require(isinstance(origins, dict), "native origins shape invalid")
        for key, origin in origins.items():
            _require(isinstance(key, str) and bool(key) and isinstance(origin, dict) and
                     isinstance(origin.get("name"), dict) and isinstance(origin.get("version"), str),
                     "origin source/version shape invalid", predicate="ORIGIN_BINDING")
            matches = [(layer, old_layer) for layer, old_layer in zip(result["layers"], prior["layers"])
                       if origin["name"] == layer["name"]]
            _require(len(matches) == 1, "origin does not bind exactly one layer source", predicate="ORIGIN_BINDING")
            layer, old_layer = matches[0]
            _require(origin["version"] == layer["version"], "origin current version differs", predicate="ORIGIN_BINDING")
            if layer["name"].get("type") == "user":
                _require(layer["name"] == old_layer["source"] and layer["name"].get("file") == path,
                         "origin user source does not own exact changed path", predicate="ORIGIN_BINDING")
                origin["version"] = old_layer["version"]
        for layer, old_layer in zip(result["layers"], prior["layers"]):
            if layer["name"].get("type") == "user":
                layer["config"] = _inverse(layer["config"], old, new)
                layer["version"] = old_layer["version"]
    prior_files = {f["path"]: f for c in previous for layer in c["layers"] for f in layer["files"]}
    for entry in files:
        if entry["metadata"]["path"] == path:
            entry["content"] = entry["content"].replace(new.rsplit("\\", 1)[-1].encode(), old.rsplit("\\", 1)[-1].encode())
        entry["metadata"] = deepcopy(prior_files[entry["metadata"]["path"]])
    physical = _physical_map(files)
    _require([_filter_native(row, physical) for row in rows] == previous,
             "derived inverse does not bind every prior filtered fact")
    return rows, files, {"material_kind": "derived_inverse_not_observed",
        "native_results_sha256": _jsha(rows),
        "physical_metadata_sha256": _jsha([e["metadata"] for e in files]),
        "filtered_configs_sha256": _jsha(previous), "witness_sha256": _jsha(witness)}


def validate_derived_transition(previous, derived_native, derived_files, witness, binding):
    """Pure relation on distinctly derived intermediate material; zero observed reads.

    A digest binding is not observation authority. Call only as an explicit chain
    from a separately validated current observed transition.
    """
    _require(isinstance(binding, dict) and set(binding) == {"material_kind", "native_results_sha256",
        "physical_metadata_sha256", "filtered_configs_sha256", "witness_sha256"} and
        binding["material_kind"] == "derived_inverse_not_observed", "derived material label missing")
    _require(binding["native_results_sha256"] == _jsha(derived_native) and
        binding["physical_metadata_sha256"] == _jsha([e["metadata"] for e in derived_files]),
        "derived material binding differs")
    current, evidence = _validate_relation(previous, derived_native, derived_files, witness,
                                           material_kind="derived_inverse_not_observed")
    _require(binding["filtered_configs_sha256"] == _jsha(current), "derived filtered binding differs")
    return current, evidence
