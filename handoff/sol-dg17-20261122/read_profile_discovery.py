"""Read a five-frame offline discovery capture. Starts no process or transport."""
import hashlib
import json
from pathlib import Path, PureWindowsPath
import sys
import tomllib

CAPTURE_LIMIT = 128 * 1024
GUEST_HOME = PureWindowsPath(r"C:\DG17\run\home")
GUEST_WORK = PureWindowsPath(r"C:\DG17\run\work")
PROFILE = Path(__file__).with_name("PROFILE_DISCOVERY.toml")
INIT = {"id": 1, "method": "initialize", "params": {
    "clientInfo": {"name": "implementaudit-stop-discovery", "version": "1"},
    "capabilities": {"experimentalApi": True},
}}
INITIALIZED = {"method": "initialized"}
LIST = {"id": 2, "method": "hooks/list", "params": {"cwds": [str(GUEST_WORK)]}}


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def unique_object(items):
    result = {}
    for key, value in items:
        require(key not in result, "duplicate message member")
        result[key] = value
    return result


def reply(packet, expected_id):
    require(isinstance(packet, dict) and set(packet) == {"id", "result"}
            and type(packet["id"]) is int and packet["id"] == expected_id
            and isinstance(packet["result"], dict), "missing or foreign response")
    return packet["result"]


def matches_path(value, expected):
    return isinstance(value, str) and PureWindowsPath(value) == expected


def examine(payload, command):
    require(len(payload) <= CAPTURE_LIMIT, "capture exceeds the bound")
    rows = [json.loads(raw, object_pairs_hook=unique_object) for raw in payload.splitlines()]
    require(len(rows) == 5, "expected only five discovery messages")
    expected = ("client", "server", "client", "client", "server")
    require(all(isinstance(row, dict) and set(row) == {"direction", "message"}
                and row["direction"] == direction
                for row, direction in zip(rows, expected, strict=True)), "unexpected frame")
    init, initialized, request = (rows[index]["message"] for index in (0, 2, 3))
    require(init == INIT and initialized == INITIALIZED and request == LIST,
            "unexpected discovery request")
    fresh = reply(rows[1]["message"], 1)
    require(matches_path(fresh.get("codexHome"), GUEST_HOME)
            and fresh.get("platformOs") == fresh.get("platformFamily") == "windows"
            and isinstance(fresh.get("userAgent"), str) and bool(fresh["userAgent"]),
            "wrong discovery platform or home")
    result = reply(rows[4]["message"], 2)
    data = result.get("data")
    require(isinstance(data, list) and len(data) == 1 and isinstance(data[0], dict),
            "wrong lookup population")
    entry = data[0]
    require(matches_path(entry.get("cwd"), GUEST_WORK)
            and entry.get("errors") == [] and isinstance(entry.get("warnings"), list),
            "foreign or errored lookup")
    hooks = entry.get("hooks")
    require(isinstance(hooks, list) and len(hooks) <= 1, "competing hook population")
    observed = {"classification": "MISSING", "warning_count": len(entry["warnings"])}
    if hooks:
        hook = hooks[0]
        require(isinstance(hook, dict) and hook.get("source") == "user"
                and matches_path(hook.get("sourcePath"), GUEST_HOME / "config.toml")
                and hook.get("eventName") == "stop" and hook.get("handlerType") == "command"
                and hook.get("command") == command and hook.get("async", False) is False
                and hook.get("timeoutSec") == 10 and hook.get("isManaged") is False
                and type(hook.get("enabled")) is bool
                and all(isinstance(hook.get(key), str) and hook[key] for key in ("key", "currentHash")),
                "unexpected effective hook")
        require(hook.get("trustStatus") == "untrusted", "unexpected trust state")
        observed.update(classification="UNTRUSTED", enabled=hook["enabled"],
                        key=hook["key"], current_hash=hook["currentHash"])
    return observed


def main():
    try:
        require(len(sys.argv) == 2, "expected one private capture file")
        with Path(sys.argv[1]).open("rb") as stream:
            data = stream.read(CAPTURE_LIMIT + 1)
        command = tomllib.loads(PROFILE.read_text(encoding="utf-8"))["hooks"]["Stop"][0]["hooks"][0]["command"]
        result = examine(data, command)
    except (ValueError, OSError, RecursionError, KeyError, TypeError) as error:
        reason = str(error) if type(error) is ValueError else type(error).__name__
        print(json.dumps({"observation": "NONVERDICT", "reason": reason, "y06_award": False}))
        return 1
    print(json.dumps({"observation": "DECLARED_CAPTURE_SHAPE_MATCH", "finding": result,
                      "capture_sha256": hashlib.sha256(data).hexdigest(),
                      "runtime_provenance_verified": False, "y06_award": False}, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
