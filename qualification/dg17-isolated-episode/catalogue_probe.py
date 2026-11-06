#!/usr/bin/env python3
"""DG17 hosted-only catalog/cleanup probe. Author preparation; no local execution.

No controller creation, namespace creation, installation, thread, turn, provider
request, hook execution request, publication, or original acceptance is supplied.
The enclosing reviewed hosted episode owns admission and independent receiving.
"""
from __future__ import annotations

import argparse
import errno
import hashlib
import importlib.util
import ipaddress
import json
import os
from pathlib import Path
import re
import selectors
import signal
import stat
import subprocess
import sys
import time

SOURCE_COMMIT = "0d57929be5bd15682b4e9da2c0209d5dff307843"
SOURCE_TREE = "ee316c27250ec422d35a1ea965182ebddf7a5da0"
VERSION = "0.167.0-alpha.4"
BINARY_BYTES = 324012616
BINARY_SHA = "57c94ea520df28beb76955316c5c48f672550fe42c6cff7003badb76e1ee10d8"
SKILLS = ("implementaudit", "audit-state", "audit-assess", "audit-implement", "audit-andon")
SOURCE_PINS = {
    ".claude-plugin/marketplace.json": "baa07799a3061c8b99d286472e43ce1263655f4064447c07141d9503ab24b544",
    ".codex-plugin/plugin.json": "4c527c0d567d74bd6d61294e6ce81db8c7cd8b674141d40ff069d4e3d82d664d",
    "package/implementaudit-package.json": "4d5db5bb9d5d686528d03d50b8ecf949909b753d0e572f25437fb324505ca5a5",
    "skills/implementaudit/SKILL.md": "4c8363c2235ba6c50675c93af7319aeb0caf57f020c4858eba1c28e76de4c6c5",
    "skills/audit-state/SKILL.md": "14caf13c42a49b335197fb24a632a9fb3ebc51b26947f311cde4a7e5b6b05a8d",
    "skills/audit-assess/SKILL.md": "6f5d5738b9efd5fa5d4c35868400220458a2f81179d4081fce508ef65c3f72e4",
    "skills/audit-implement/SKILL.md": "aaeb90c6fcded31064f4731cd19cb0e8dcb9e7a5c82a0db4de2f3eab17d978b2",
    "skills/audit-andon/SKILL.md": "d774154be7940f88e6402b9d7299f36792e0a636c9023f68fe88b062e2604ff9",
    "skills/implementaudit/scripts/claim-run.sh": "9bce5c887cd89c2d2991b84f1bf765787e7a6b75a2eba29a8433c3a6c05f73a3",
}
TRANSPORT_PINS = {
    "owned_resources": "0b7d871aca378dc807bc33211d4b84a1b0baa45939c9c24ca54374c23468e33a",
    "namespace_process_custody": "6d2e049a8ddbc89e6213c4968d44e6e1483254d852d45480b90f01f960453630",
    "native_transport": "20192cf71daca4160b3117d8a61e8e029cf56d220bc0072b91dc2a8e3779a884",
}
METHODS = ("initialize", "plugin/read", "skills/list", "hooks/list")
HOOK_EVENTS = {
    "preModelRequest", "postModelRequest", "preToolUse", "permissionRequest",
    "postToolUse", "preCompact", "postCompact", "sessionStart", "sessionEnd",
    "userPromptSubmit", "subagentStart", "subagentStop", "stop", "interrupt",
}
HOOK_SOURCES = {
    "system", "user", "project", "mdm", "sessionFlags", "plugin",
    "cloudRequirements", "cloudManagedConfig", "legacyManagedConfigFile",
    "legacyManagedConfigMdm", "unknown",
}
EXTRA = (
    "--strict-config",
    "-c", "features.plugins=true",
    "-c", "features.plugin_discovery_prefetch=false",
    "-c", "features.remote_plugin=false",
    "-c", "cli_auth_credentials_store=\"ephemeral\"",
    "-c", "mcp_oauth_credentials_store=\"file\"",
    "-c", "analytics.enabled=false",
    "-c", "feedback.enabled=false",
)
GIT_PROFILE = "LINUX_STANDARD_GIT_EMPTY_OR_SAFE_DIRECTORY_V1"
# Pinned Codex system_commands.rs, fb036d4e..., blob 7e51da40... .
# Native.env PATH is not this resolver: automatic Git replaces its helper PATH.
SYSTEM_DIRECTORY_CANDIDATES = (
    "/opt/homebrew/bin", "/usr/local/bin", "/opt/local/bin",
    "/run/current-system/sw/bin", "/nix/var/nix/profiles/default/bin",
    "/Library/Developer/CommandLineTools/usr/bin",
    "/Applications/Xcode.app/Contents/Developer/usr/bin",
    "/usr/bin", "/bin", "/usr/sbin", "/sbin",
)
INSTALLATION_ROOTS = tuple(Path(p) for p in (
    "/usr/bin", "/bin", "/usr/sbin", "/sbin", "/usr/local",
    "/opt/homebrew", "/opt/local", "/Library/Developer/CommandLineTools",
    "/Applications/Xcode.app/Contents/Developer", "/nix/store",
    "/mnt/c/Windows/System32",
))
ADMITTED_SYSTEM_DIRECTORIES = {"/usr/local/bin", "/usr/bin", "/usr/sbin"}
SYSTEM_GIT_CONFIG = Path("/etc/gitconfig")
GIT_QUERY_LIMIT = 65536
GIT_QUERY_SECONDS = 3


class Refusal(RuntimeError):
    pass


def need(ok, code):
    if not ok:
        raise Refusal(code)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def file_sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        while block := f.read(1024 * 1024):
            h.update(block)
    return h.hexdigest()


def write_json(path, obj):
    with path.open("x", encoding="utf-8") as f:
        json.dump(obj, f, sort_keys=True, indent=2)
        f.write("\n")
        f.flush()
        os.fsync(f.fileno())


def regular(path):
    need(stat.S_ISREG(path.lstat().st_mode) and not path.is_symlink(),
         "NONREGULAR_INPUT")
    return path


def fixed_env(home):
    return {"PATH": "/usr/bin:/bin", "HOME": str(home), "LANG": "C.UTF-8",
            "PYTHONDONTWRITEBYTECODE": "1",
            "IMPLEMENTAUDIT_PYTHON": sys.executable}


def admit_root_fields(uid, mode, executable=False, capability_present=False):
    """Pure predicate, also exercised with explicitly synthetic integer inputs."""
    need(uid == 0, "GIT_INSTALLATION_NOT_ROOT_OWNED")
    if not stat.S_ISLNK(mode):
        need(not mode & 0o022, "GIT_INSTALLATION_WRITABLE")
    if executable:
        need(stat.S_ISREG(mode) and mode & 0o111 and not mode & 0o6000,
             "GIT_EXECUTABLE_MODE_UNADMITTED")
        need(not capability_present, "GIT_EXECUTABLE_CAPABILITY_PRESENT")


def root_path_identity(path, absent_ok=False):
    """Bind lexical and canonical root-controlled ancestry; never follow config includes."""
    path = Path(path)
    need(path.is_absolute() and ".." not in path.parts, "GIT_INSTALLATION_PATH_UNADMITTED")
    rows = {}

    def walk(ending, missing_ok):
        for item in (*reversed(ending.parents), ending):
            try:
                info = item.lstat()
            except FileNotFoundError:
                need(missing_ok, "GIT_INSTALLATION_PATH_MISSING")
                return False
            admit_root_fields(info.st_uid, info.st_mode)
            need(stat.S_ISDIR(info.st_mode) or stat.S_ISLNK(info.st_mode) or item == ending,
                 "GIT_INSTALLATION_ANCESTOR_NOT_DIRECTORY")
            row = {"device": info.st_dev, "inode": info.st_ino, "uid": info.st_uid,
                   "gid": info.st_gid, "mode": info.st_mode}
            if stat.S_ISLNK(info.st_mode):
                row["link_sha256"] = sha(os.fsencode(os.readlink(item)))
                # Bind the target's ancestry as well as the protected link itself.
                walk(item.resolve(strict=True), False)
            rows[str(item)] = row
        return True

    present = walk(path, absent_ok)
    if not present:
        return {"present": False, "path": str(path), "ancestry": rows}
    resolved = path.resolve(strict=True)
    walk(resolved, False)
    return {"present": True, "path": str(path), "resolved": str(resolved),
            "ancestry": rows}


def executable_identity(path):
    row = root_path_identity(path)
    resolved = Path(row["resolved"])
    info = resolved.stat()
    try:
        capability = os.getxattr(resolved, "security.capability")
    except OSError as exc:
        need(exc.errno == errno.ENODATA, "GIT_EXECUTABLE_CAPABILITY_UNREADABLE")
        capability = b""
    admit_root_fields(info.st_uid, info.st_mode, executable=True,
                      capability_present=bool(capability))
    with resolved.open("rb") as stream:
        need(stream.read(4) == b"\x7fELF", "GIT_EXECUTABLE_NOT_ELF")
    need(0 < info.st_size <= 134217728, "GIT_EXECUTABLE_SIZE_UNADMITTED")
    row.update(bytes=info.st_size, sha256=file_sha(resolved),
               mtime_ns=info.st_mtime_ns, ctime_ns=info.st_ctime_ns)
    return row


def select_admitted_git(candidates):
    """Pure selection over upstream-eligible candidates in upstream search order."""
    chosen = next((candidate for candidate in candidates if candidate is not None), None)
    need(chosen == "/usr/bin/git", "CODEX_GIT_RESOLVER_UNADMITTED")
    return chosen


def git_system_paths():
    # A narrower non-WSL conventional Linux profile, not Ubuntu-wide support.
    for path in (Path("/proc/sys/kernel/osrelease"), Path("/proc/version")):
        need("microsoft" not in path.read_text().lower(), "GIT_WSL_PROFILE_UNADMITTED")
    need(not os.path.lexists("/mnt/c/Windows/System32"), "GIT_WSL_PROFILE_UNADMITTED")
    directories, directory_rows, candidates, candidate_rows = [], [], [], []
    for raw in SYSTEM_DIRECTORY_CANDIDATES:
        row = root_path_identity(Path(raw), absent_ok=True)
        directory_rows.append(row)
        if not row["present"]:
            continue
        directory = Path(row["resolved"])
        need(directory.is_dir(), "GIT_SYSTEM_PATH_NOT_DIRECTORY")
        if not any(directory.is_relative_to(root) for root in INSTALLATION_ROOTS):
            # Upstream ignores this path, but this narrow profile declines it.
            raise Refusal("GIT_SYSTEM_PATH_OUTSIDE_INSTALLATION")
        need(str(directory) in ADMITTED_SYSTEM_DIRECTORIES, "GIT_SYSTEM_PATH_UNADMITTED")
        directories.append(str(directory))  # Preserve upstream order and aliases.
        candidate = directory / "git"
        candidate_row = root_path_identity(candidate, absent_ok=True)
        candidate_rows.append(candidate_row)
        selected = None
        if candidate_row["present"]:
            resolved = Path(candidate_row["resolved"])
            info = resolved.stat()
            eligible = (stat.S_ISREG(info.st_mode) and info.st_mode & 0o111 and
                        any(resolved.is_relative_to(root) for root in INSTALLATION_ROOTS))
            if eligible:
                selected = str(resolved)
        candidates.append(selected)
    selected = select_admitted_git(candidates)
    return selected, os.pathsep.join(directories), {
        "directories": directory_rows, "git_candidates": candidate_rows,
        "system_path": directories,
    }


def git_query(binary, arguments, home, helper_path):
    """Bounded read-only Git metadata query; stdout/stderr are never retained or exported."""
    env = {"PATH": helper_path, "HOME": str(home), "LANG": "C"}
    proc = subprocess.Popen([binary, "--no-pager", *arguments], cwd=home, env=env,
                            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    buffers = {"stdout": bytearray(), "stderr": bytearray()}
    selector = selectors.DefaultSelector()
    deadline = time.monotonic() + GIT_QUERY_SECONDS
    try:
        for name in buffers:
            stream = getattr(proc, name)
            os.set_blocking(stream.fileno(), False)
            selector.register(stream, selectors.EVENT_READ, name)
        while selector.get_map():
            left = deadline - time.monotonic()
            need(left > 0, "GIT_METADATA_QUERY_TIMEOUT")
            events = selector.select(left)
            need(bool(events), "GIT_METADATA_QUERY_TIMEOUT")
            for key, _ in events:
                block = os.read(key.fileobj.fileno(), 8192)
                if not block:
                    selector.unregister(key.fileobj)
                else:
                    buffers[key.data].extend(block)
                    need(sum(map(len, buffers.values())) <= GIT_QUERY_LIMIT,
                         "GIT_METADATA_QUERY_OUTPUT_LIMIT")
        left = deadline - time.monotonic()
        need(left > 0, "GIT_METADATA_QUERY_TIMEOUT")
        return proc.wait(timeout=left), bytes(buffers["stdout"]), bytes(buffers["stderr"])
    finally:
        selector.close()
        if proc.poll() is None:
            proc.kill()  # Only this known metadata child, never a discovered PID/group.
            proc.wait(timeout=3)
        for name in buffers:
            getattr(proc, name).close()


def admit_system_config_query(returncode, stdout, stderr, file_present):
    """Only empty or one exact owned-repository-profile trust entry is admitted."""
    if file_present:
        need(returncode == 0 and stderr == b"", "GIT_SYSTEM_CONFIG_QUERY_UNADMITTED")
        if stdout == b"":
            return "EMPTY", 0
        exact = b"file:/etc/gitconfig\0safe.directory\n*\0"
        need(stdout == exact, "GIT_SYSTEM_CONFIG_UNADMITTED")
        return "SAFE_DIRECTORY_WILDCARD", 1
    need(stdout == b"", "GIT_SYSTEM_CONFIG_UNADMITTED")
    expected = b"fatal: unable to read config file '/etc/gitconfig': No such file or directory\n"
    need(returncode == 128 and stderr == expected, "GIT_SYSTEM_CONFIG_ABSENCE_UNBOUND")
    return "ABSENT", 0


def git_home_guard(home, before):
    need(home.is_dir() and not home.is_symlink(), "GIT_HOME_UNADMITTED")
    info = home.stat()
    need(info.st_uid == os.geteuid() and not info.st_mode & 0o077,
         "GIT_HOME_NOT_PRIVATE")
    if before:
        need(not any(home.iterdir()), "GIT_HOME_NOT_EMPTY")
    for ancestor in (home, *home.parents):
        need(not os.path.lexists(ancestor / ".git"), "GIT_METADATA_CWD_HAS_REPOSITORY")
    config_dir = home / ".config"
    if os.path.lexists(config_dir):
        cinfo = config_dir.lstat()
        need(stat.S_ISDIR(cinfo.st_mode) and cinfo.st_uid == os.geteuid() and
             not cinfo.st_mode & 0o022, "GIT_GLOBAL_PARENT_UNADMITTED")
    for path in (home / ".gitconfig", home / ".config/git/config"):
        need(not os.path.lexists(path), "GIT_GLOBAL_CONFIG_PRESENT")
    # A .config/git symlink could mask absence or redirect a subsequent lookup.
    git_dir = config_dir / "git"
    if os.path.lexists(git_dir):
        ginfo = git_dir.lstat()
        need(stat.S_ISDIR(ginfo.st_mode) and ginfo.st_uid == os.geteuid() and
             not ginfo.st_mode & 0o022, "GIT_GLOBAL_PARENT_UNADMITTED")
    return {"device": info.st_dev, "inode": info.st_ino, "uid": info.st_uid,
            "gid": info.st_gid, "mode": info.st_mode, "global_paths_absent": True}


def admit_source_git_config(data):
    """Pure narrow parser for an ordinary owned checkout; never interpret imports."""
    need(len(data) <= 16384, "GIT_SOURCE_CONFIG_SIZE_UNADMITTED")
    try:
        lines = data.decode("ascii").splitlines()
    except UnicodeDecodeError:
        raise Refusal("GIT_SOURCE_CONFIG_UNADMITTED")
    section = None
    seen_sections = set()
    values = {"core": {}, "origin": {}}
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith(("#", ";")):
            continue
        if line in {"[core]", '[remote "origin"]'}:
            section = "core" if line == "[core]" else "origin"
            need(section not in seen_sections, "GIT_SOURCE_CONFIG_UNADMITTED")
            seen_sections.add(section)
            continue
        match = re.fullmatch(r"([A-Za-z][A-Za-z0-9]*)\s*=\s*([^\r\n]*)", line)
        need(section is not None and match is not None, "GIT_SOURCE_CONFIG_UNADMITTED")
        key, value = match.group(1).lower(), match.group(2)
        need(key not in values[section], "GIT_SOURCE_CONFIG_UNADMITTED")
        values[section][key] = value
    required = {"repositoryformatversion": "0", "filemode": "true",
                "bare": "false", "logallrefupdates": "true"}
    origin = {"url": "https://github.com/theislampill/IMPLEMENTAUDIT.md.git",
              "fetch": "+refs/heads/*:refs/remotes/origin/*"}
    need(values["origin"] == origin and
         (values["core"] == required or
          values["core"] == {**required, "hookspath": "/dev/null"}),
         "GIT_SOURCE_CONFIG_UNADMITTED")
    return len(values["core"]) + len(values["origin"])


def source_store_guard(source):
    """Read-only physical ownership/config census; live controller refs are permitted."""
    need(os.geteuid() != 0 and source.is_absolute() and
         source.resolve(strict=True) == source, "GIT_SOURCE_NOT_PHYSICAL_ORDINARY_USER")
    git_dir = source / ".git"
    roots = {}
    for label, path in (("source", source), ("git_dir", git_dir),
                        ("objects", git_dir / "objects"), ("refs", git_dir / "refs")):
        info = path.lstat()
        need(stat.S_ISDIR(info.st_mode) and info.st_uid == os.geteuid() and
             not info.st_mode & 0o022 and path.resolve(strict=True) == path,
             "GIT_SOURCE_STORE_OWNERSHIP_UNADMITTED")
        roots[label] = {"device": info.st_dev, "inode": info.st_ino, "uid": info.st_uid,
                        "gid": info.st_gid, "mode": info.st_mode}
    for name in ("commondir", "gitdir", "objects/info/alternates", "objects/info/http-alternates",
                 "config.worktree", "worktrees"):
        need(not os.path.lexists(git_dir / name), "GIT_SOURCE_STORE_REDIRECTION_PRESENT")
    config = git_dir / "config"
    info = regular(config).stat()
    need(info.st_uid == os.geteuid() and info.st_nlink == 1 and
         not info.st_mode & 0o022 and info.st_size <= 16384,
         "GIT_SOURCE_CONFIG_FILE_UNADMITTED")
    with config.open("rb") as stream:
        config_data = stream.read(16385)
    need(len(config_data) == info.st_size, "GIT_SOURCE_CONFIG_CHANGED_DURING_READ")
    config_entries = admit_source_git_config(config_data)
    entries = 0
    def unreadable(error):
        raise Refusal("GIT_SOURCE_STORE_CENSUS_UNREADABLE")
    for parent, directories, files in os.walk(git_dir, followlinks=False, onerror=unreadable):
        for name in (*directories, *files):
            path = Path(parent) / name
            info = path.lstat()
            entries += 1
            need(entries <= 65536, "GIT_SOURCE_STORE_CENSUS_LIMIT")
            need(info.st_uid == os.geteuid() and not info.st_mode & 0o022 and
                 (stat.S_ISDIR(info.st_mode) or
                  (stat.S_ISREG(info.st_mode) and info.st_nlink == 1)),
                 "GIT_SOURCE_STORE_ALIAS_OR_MODE_UNADMITTED")
    hooks = git_dir / "hooks"
    if hooks.exists():
        need(hooks.is_dir() and not hooks.is_symlink(), "GIT_SOURCE_HOOKS_UNADMITTED")
        for path in hooks.iterdir():
            need(path.is_file() and not path.is_symlink() and path.name.endswith(".sample"),
                 "GIT_SOURCE_ACTIVE_HOOK_PRESENT")
    return {"profile": "OWNED_CHECKOUT_CORE_ORIGIN_V1", "roots": roots,
            "config_entries": config_entries, "config_sha256": sha(config_data),
            "entries_checked": entries, "active_hook_count": 0,
            "redirections_absent": True, "live_controller_refs_permitted": True}


def git_startup_guard(home, before, source):
    home_row = git_home_guard(home, before)
    source_store = source_store_guard(source)
    binary, helper_path, resolution = git_system_paths()
    git_row = executable_identity(Path(binary))
    need(git_row["resolved"] == "/usr/bin/git", "GIT_BINARY_PATH_UNADMITTED")
    libexec = root_path_identity(Path("/usr/lib/git-core"))
    need(libexec["resolved"] == "/usr/lib/git-core" and Path(libexec["resolved"]).is_dir(),
         "GIT_LIBEXEC_PATH_UNADMITTED")
    helpers = {}
    for name in ("git", "git-remote-http", "git-remote-https"):
        helpers[name] = executable_identity(Path("/usr/lib/git-core") / name)
    need(helpers["git"]["sha256"] == git_row["sha256"] and
         helpers["git"]["bytes"] == git_row["bytes"], "GIT_LIBEXEC_MAIN_DIFFERS")
    need(helpers["git-remote-http"]["resolved"] == "/usr/lib/git-core/git-remote-http" and
         helpers["git-remote-https"]["resolved"] in
         {"/usr/lib/git-core/git-remote-http", "/usr/lib/git-core/git-remote-https"},
         "GIT_HTTPS_HELPER_PATH_UNADMITTED")
    system = root_path_identity(SYSTEM_GIT_CONFIG, absent_ok=True)
    if system["present"]:
        need(system["resolved"] == str(SYSTEM_GIT_CONFIG) and
             not SYSTEM_GIT_CONFIG.is_symlink(), "GIT_SYSTEM_CONFIG_PATH_UNADMITTED")
        info = SYSTEM_GIT_CONFIG.stat()
        need(stat.S_ISREG(info.st_mode) and info.st_nlink == 1 and
             info.st_size <= GIT_QUERY_LIMIT,
             "GIT_SYSTEM_CONFIG_FILE_UNADMITTED")
        system.update(bytes=info.st_size, sha256=file_sha(SYSTEM_GIT_CONFIG),
                      mtime_ns=info.st_mtime_ns, ctime_ns=info.st_ctime_ns)
    rc, out, err = git_query(binary, ["--exec-path"], home, helper_path)
    need(rc == 0 and out == b"/usr/lib/git-core\n" and err == b"",
         "GIT_COMPILED_LIBEXEC_UNADMITTED")
    # This query disables include expansion and never applies any config value.
    # Only no entries or the exact sole safe.directory='*' record may reach `git var`.
    # The wildcard disables Git's foreign-owner check; our owned-repository
    # boundaries remain required and no transport/helper-selection key is allowed.
    rc, out, err = git_query(binary, ["config", "--system", "--list", "--null",
                                    "--show-origin", "--no-includes"], home, helper_path)
    config_state, config_entries = admit_system_config_query(rc, out, err, system["present"])
    rc, out, err = git_query(binary, ["var", "GIT_CONFIG_SYSTEM"], home, helper_path)
    need(rc == 0 and out == b"/etc/gitconfig\n" and err == b"",
         "GIT_COMPILED_CONFIG_ORIGIN_UNADMITTED")
    rc, out, err = git_query(binary, ["var", "GIT_CONFIG_GLOBAL"], home, helper_path)
    expected_globals = {os.fsencode(home / ".gitconfig"),
                        os.fsencode(home / ".config/git/config")}
    need(rc == 0 and err == b"" and out.endswith(b"\n") and
         len(out.splitlines()) == 2 and set(out.splitlines()) == expected_globals,
         "GIT_GLOBAL_CONFIG_ORIGINS_UNADMITTED")
    rc, out, err = git_query(binary, ["-C", str(source), "rev-parse", "--path-format=absolute",
                                    "--git-dir", "--git-common-dir"], home, helper_path)
    expected_store = os.fsencode(source / ".git") + b"\n"
    need(rc == 0 and out == expected_store * 2 and err == b"",
         "GIT_ACTUAL_COMMON_STORE_DIFFERS")
    # Detect replacement during the metadata queries, before app-server startup.
    need(executable_identity(Path(binary)) == git_row and
         root_path_identity(SYSTEM_GIT_CONFIG, absent_ok=True) ==
         {key: value for key, value in system.items()
          if key not in {"bytes", "sha256", "mtime_ns", "ctime_ns"}},
         "GIT_ADMISSION_IDENTITY_CHANGED")
    if system["present"]:
        info = SYSTEM_GIT_CONFIG.stat()
        need(info.st_nlink == 1 and info.st_size == system["bytes"] and
             file_sha(SYSTEM_GIT_CONFIG) == system["sha256"]
             and info.st_mtime_ns == system["mtime_ns"] and info.st_ctime_ns == system["ctime_ns"],
             "GIT_ADMISSION_CONFIG_CHANGED")
    need(git_home_guard(home, False) == home_row, "GIT_ADMISSION_HOME_CHANGED")
    need(source_store_guard(source) == source_store, "GIT_ADMISSION_SOURCE_STORE_CHANGED")
    snapshot = {"resolver": resolution, "git": git_row, "libexec": libexec,
                "helpers": helpers, "system_config": system, "home": home_row,
                "source_store": source_store}
    encoded = json.dumps(snapshot, sort_keys=True, separators=(",", ":")).encode()
    public = {"profile": GIT_PROFILE, "before_passed": True, "after_passed": False,
              "identities_unchanged": False, "git_sha256": git_row["sha256"],
              "git_bytes": git_row["bytes"], "system_config_state": config_state,
              "system_config_entries": config_entries, "system_config_bytes": system.get("bytes", 0),
              "system_config_sha256": system.get("sha256"),
              "global_config_paths_absent": True, "includes_expanded": False,
              "source_store_owned_physical": True, "source_common_dir_matches": True,
              "source_config_profile": source_store["profile"],
              "source_git_config_entries": source_store["config_entries"],
              "source_git_config_sha256": source_store["config_sha256"],
              "source_active_hook_count": 0, "source_redirections_absent": True,
              "selected_helper_count": len(helpers),
              "system_path_directory_count": len(resolution["system_path"]),
              "before_identity_sha256": sha(encoded), "after_identity_sha256": None}
    return snapshot, public


def offline_guard(args):
    need(sys.platform == "linux", "LINUX_REQUIRED")
    need(sys.flags.isolated and sys.flags.no_site and sys.flags.dont_write_bytecode,
         "ISOLATED_PYTHON_FLAGS_REQUIRED")
    need(os.getuid() == os.geteuid() == args.expected_uid and
         os.getgid() == os.getegid() == args.expected_gid,
         "HOST_IDENTITY_DIFFERS")
    need(not os.getgroups(), "SUPPLEMENTARY_GROUPS_PRESENT")
    fields = {}
    for line in Path("/proc/self/status").read_text().splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            fields[key] = val.strip()
    need(all(int(fields[k], 16) == 0 for k in ("CapEff", "CapPrm", "CapAmb"))
         and fields["NoNewPrivs"] == "1", "PRIVILEGE_ENVELOPE_DIFFERS")
    current_netns = os.readlink("/proc/self/ns/net")
    need(re.fullmatch(r"net:\[(\d+)\]", args.parent_netns) is not None and
         current_netns != args.parent_netns,
         "OFFLINE_NAMESPACE_NOT_DISTINCT")
    interfaces = [line.split(":", 1)[0].strip()
                  for line in Path("/proc/net/dev").read_text().splitlines()[2:]
                  if ":" in line]
    need(interfaces == ["lo"], "NONLOOPBACK_INTERFACE_PRESENT")
    route4 = Path("/proc/net/route").read_text().splitlines()[1:]
    for line in route4:
        row = line.split()
        dest = ipaddress.IPv4Address(bytes.fromhex(row[1])[::-1])
        need(row[0] == "lo" and dest.is_loopback, "EXTERNAL_IPV4_ROUTE")
    route6 = Path("/proc/net/ipv6_route").read_text().splitlines()
    for line in route6:
        row = line.split()
        reject = bool(int(row[8], 16) & 0x200)
        loopback = int(row[1], 16) == 128 and ipaddress.IPv6Address(int(row[0], 16)).is_loopback
        need(row[-1] == "lo" and (reject or loopback), "EXTERNAL_IPV6_ROUTE")
    return {"verified": True, "uid": os.geteuid(), "gid": os.getegid(),
            "namespace_differs_from_parent": True, "only_loopback": True,
            "effective_permitted_ambient_capabilities_zero": True,
            "no_new_privileges": True, "external_routes": 0}


def currentness(args, source, home, private, label):
    owner = source / "skills/implementaudit/scripts/claim-run.sh"
    result = subprocess.run(
        ["/usr/bin/bash", str(owner), "--require-current-continuity", args.controller],
        cwd=source, env=fixed_env(home),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20, check=False)
    (private / (label + ".stdout")).write_bytes(result.stdout)
    (private / (label + ".stderr")).write_bytes(result.stderr)
    need(result.returncode == 0 and result.stdout == (args.receipt + "\n").encode(),
         "CURRENTNESS_GATE_REFUSED")
    return sha(result.stdout)


def source_guard(source, home):
    for name, expected in SOURCE_PINS.items():
        need(file_sha(regular(source / name)) == expected, "SOURCE_INPUT_DIFFERS")
    env = fixed_env(home)
    env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null")
    for query, expected in (("HEAD", SOURCE_COMMIT), ("HEAD^{tree}", SOURCE_TREE)):
        r = subprocess.run(["/usr/bin/git", "-C", str(source), "rev-parse", query],
                           env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           timeout=5, check=False)
        need(r.returncode == 0 and r.stdout.decode("ascii").strip() == expected,
             "SOURCE_GIT_IDENTITY_DIFFERS")
    manifest = json.loads((source / ".claude-plugin/marketplace.json").read_text())
    need(manifest["plugins"] == [{
        "name": "implementaudit",
        "description": "Audit-closure governance skill for bounded, verified repository changes.",
        "source": "./"}], "LOCAL_SELECTOR_DIFFERS")
    # Refuse unexpected startup layers instead of reading or overriding their contents.
    for parent in (source, *source.parents):
        for name in ("config.toml", "hooks.json"):
            need(not os.path.lexists(parent / ".codex" / name),
                 "UNREVIEWED_PROJECT_STARTUP_LAYER")
    for name in ("config.toml", "managed_config.toml", "requirements.toml", "hooks.json"):
        need(not os.path.lexists(Path("/etc/codex") / name),
             "UNREVIEWED_SYSTEM_STARTUP_LAYER")


def load_transports(root):
    loaded = {}
    for name, expected in TRANSPORT_PINS.items():
        path = regular(root / (name + ".py"))
        need(file_sha(path) == expected, "TRANSPORT_INPUT_DIFFERS")
        need(name not in sys.modules, "TRANSPORT_MODULE_ALREADY_LOADED")
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        loaded[name] = module
    return loaded


def selected_skill(row, source, plugin_id=None):
    name = row.get("name")
    if name not in SKILLS:
        return None
    expected = source / "skills" / name / "SKILL.md"
    raw = row.get("path")
    path_matches = isinstance(raw, str) and Path(raw).is_absolute() and Path(raw) == expected
    enabled = row.get("enabled")
    need(type(enabled) is bool, "INVALID_SKILL_METADATA")
    return {"name": name, "path": "skills/" + name + "/SKILL.md",
            "path_matches_frozen_source": path_matches, "enabled": enabled,
            "plugin_attribution_matches": plugin_id is not None and row.get("pluginId") == plugin_id}


def plugin_projection(result, source):
    detail = result["plugin"]
    summary = detail["summary"]
    origin = summary["source"]
    need(summary["name"] == "implementaudit" and origin["type"] == "local"
         and Path(origin["path"]) == source, "PLUGIN_SELECTED_ANOTHER_SOURCE")
    need(Path(detail["marketplacePath"]) == source / ".claude-plugin/marketplace.json",
         "PLUGIN_MARKETPLACE_DIFFERS")
    need(type(summary["installed"]) is bool and type(summary["enabled"]) is bool,
         "INVALID_PLUGIN_METADATA")
    rows = [selected_skill(row, source) for row in detail["skills"]]
    known = [row for row in rows if row is not None]
    need(len(known) <= 32, "PLUGIN_CATALOG_EXPORT_LIMIT")
    names = [row["name"] for row in known]
    complete = (len(rows) == len(SKILLS) and sorted(names) == sorted(SKILLS)
                and all(row["path_matches_frozen_source"] for row in known))
    return {"status": "CATALOG_OBSERVED", "source_matches": True,
            "installed": summary["installed"], "enabled": summary["enabled"],
            "five_exact_skill_paths": complete, "skills": known,
            "other_skill_count": len(rows) - len(known),
            "declared_hook_count": len(detail["hooks"])}, summary["id"]


def skills_projection(result, source, plugin_id):
    data = result["data"]
    need(len(data) == 1 and Path(data[0]["cwd"]) == source, "SKILLS_SCOPE_DIFFERS")
    rows = [selected_skill(row, source, plugin_id) for row in data[0]["skills"]]
    need(sum(row is not None for row in rows) <= 32, "SKILL_CATALOG_EXPORT_LIMIT")
    return {"status": "CONFIGURED_SKILL_CATALOG_OBSERVED",
            "skills": [row for row in rows if row is not None],
            "other_skill_count": sum(row is None for row in rows),
            "error_count": len(data[0]["errors"]), "thread_content_loaded": False}


def hooks_projection(result, source, plugin_id):
    data = result["data"]
    need(len(data) == 1 and Path(data[0]["cwd"]) == source, "HOOKS_SCOPE_DIFFERS")
    rows = []
    need(len(data[0]["hooks"]) <= 128, "HOOK_CATALOG_EXPORT_LIMIT")
    for hook in data[0]["hooks"]:
        need(hook["eventName"] in HOOK_EVENTS and hook["source"] in HOOK_SOURCES
             and hook["trustStatus"] in {"managed", "untrusted", "trusted", "modified"}
             and re.fullmatch("[0-9a-f]{64}", hook["currentHash"]) is not None
             and type(hook["enabled"]) is bool and type(hook["isManaged"]) is bool,
             "INVALID_HOOK_METADATA")
        rows.append({"event": hook["eventName"], "source": hook["source"],
                     "trust": hook["trustStatus"], "sha256": hook["currentHash"],
                     "enabled": hook["enabled"], "managed": hook["isManaged"],
                     "candidate_plugin": plugin_id is not None and hook.get("pluginId") == plugin_id})
    return {"status": "CONFIGURED_HOOK_CATALOG_OBSERVED", "hooks": rows,
            "error_count": len(data[0]["errors"]), "warning_count": len(data[0]["warnings"]),
            "loaded_thread_hooks_observed": False, "hook_delivery_exercised": False}


def contain_known_parent(native):
    # Used only after an exception. Never signal a discovered PID or a process group.
    proc = getattr(native, "proc", None)
    if proc is None or proc.poll() is not None:
        return {"status": "NO_LIVE_KNOWN_PARENT", "signals_sent": 0}
    fd = os.pidfd_open(proc.pid, 0)
    sent = 0
    try:
        for sig in (signal.SIGTERM, signal.SIGKILL):
            try:
                signal.pidfd_send_signal(fd, sig, None, 0)
                sent += 1
            except ProcessLookupError:
                pass
            try:
                proc.wait(timeout=3)
                return {"status": "KNOWN_PARENT_REAPED", "signals_sent": sent}
            except subprocess.TimeoutExpired:
                continue
        return {"status": "KNOWN_PARENT_NOT_REAPED", "signals_sent": sent}
    finally:
        os.close(fd)


def independent_readback(native, modules):
    launch = getattr(native, "launch_dir", None)
    identity = getattr(native, "process_identity", None)
    custody = getattr(native, "custody", None)
    live, zombies, uncertain = 0, 0, 0
    for row in modules["owned_resources"].processes():
        by_exe = launch is not None and (row.get("exe") or "").startswith(str(launch) + "/")
        by_session = False
        try:
            seen = modules["namespace_process_custody"].observe("/proc/" + str(row["pid"]))
            if identity is not None and custody is not None:
                by_session = (seen["namespace_sessions"][:custody.depth] ==
                              identity["namespace_sessions"][:custody.depth]
                              and seen["start_ticks"] >= identity["start_ticks"])
        except (FileNotFoundError, ProcessLookupError):
            continue
        except (OSError, modules["namespace_process_custody"].CustodyError):
            if by_exe or (identity is not None and
                          row["session"] == identity["namespace_sessions"][0] and
                          row["start_ticks"] >= identity["start_ticks"]):
                uncertain += 1
        if by_exe or by_session:
            if row["state"] == "Z":
                zombies += 1
            else:
                live += 1
    empty = launch is not None and launch.is_dir() and not launch.is_symlink() and not any(launch.iterdir())
    return {"full_session_scope_available": identity is not None,
            "living_owned_processes": live, "owned_zombies": zombies,
            "uncertain_owned_candidates": uncertain, "launch_directory_empty": empty}


def private_seal_rows(root):
    rows = []
    for path in sorted(root.rglob("*")):
        if path == root / "PRIVATE_EVIDENCE_SEAL.json":
            continue
        mode = path.lstat().st_mode
        if stat.S_ISREG(mode):
            rows.append({"path": path.relative_to(root).as_posix(),
                         "bytes": path.stat().st_size, "sha256": file_sha(path)})
        elif not stat.S_ISDIR(mode):
            rows.append({"path": path.relative_to(root).as_posix(), "kind": "NONREGULAR"})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for arg in ("source", "episode", "binary", "controller", "receipt", "parent-netns"):
        parser.add_argument("--" + arg, required=True)
    parser.add_argument("--expected-uid", type=int, required=True)
    parser.add_argument("--expected-gid", type=int, required=True)
    args = parser.parse_args()
    def interrupted(signum, frame):
        raise Refusal("HOST_INTERRUPTED")
    signal.signal(signal.SIGTERM, interrupted)
    result = {
        "schema": "dg17.t12.model-free-catalog-cleanup.v2",
        "status": "NOT_EXECUTED", "source_commit": SOURCE_COMMIT, "source_tree": SOURCE_TREE,
        "runtime_version": VERSION, "runtime_sha256": BINARY_SHA, "runtime_bytes": BINARY_BYTES,
        "source_identity_verified": False, "runtime_identity_verified": False,
        "runtime_reported_version_matches": False,
        "selector": ".claude-plugin/marketplace.json:implementaudit:./",
        "original_acceptance_awarded": False, "independent_receiving": "NOT_PERFORMED",
        "model_inference_proven": False, "prompt_independent_routing_proven": False,
        "native_process_started": False, "startup_configuration": list(EXTRA),
        "offline": None, "git_startup_admission": None,
        "currentness_before": False, "currentness_after": False,
        "unexpected_lifecycle_notification_count": 0,
        "unexpected_server_request_count": 0, "nonmetadata_outbound_count": 0,
        "calls": [], "catalog": None, "configured_skills": None, "configured_hooks": None,
        "cleanup": {"close_returned": False, "parent_returncode": None,
                    "reader_joined": False, "transport_remaining_owned_count": None,
                    "close_error_type": None,
                    "after_close": None, "after_seal": None, "private_seal_unchanged": False,
                    "containment": None},
        "private_evidence_seal_sha256": None, "failure": None,
    }
    native = None
    modules = None
    git_before = None
    private = None
    result_path = None
    phase = "PRECONDITIONS"
    primary_error = None
    try:
        result["offline"] = offline_guard(args)
        source_argument = Path(args.source)
        source = source_argument.resolve(strict=True)
        need(source_argument == source, "GIT_SOURCE_NOT_PHYSICAL_ORDINARY_USER")
        transport_root = Path(__file__).resolve(strict=True).parent
        episode = Path(args.episode).resolve(strict=True)
        need(re.fullmatch(r"[a-z0-9][a-z0-9-]{0,95}", args.controller) is not None and
             re.fullmatch(r"refs/implementaudit/continuity-receipts/" +
                          re.escape(args.controller) + r"/G[0-9]{4}@[0-9a-f]{40}",
                          args.receipt) is not None, "CONTINUITY_ARGUMENTS_DIFFERS")
        envelope_private = episode / "private"
        gate_home = episode / "home"
        need(envelope_private.is_dir() and not envelope_private.is_symlink() and
             gate_home.is_dir() and not gate_home.is_symlink() and
             envelope_private.stat().st_uid == os.geteuid(), "EPISODE_PATHS_DIFFER")
        root = envelope_private / "native-catalogue"
        need(not os.path.lexists(root), "WORK_ROOT_NOT_FRESH")
        need(not root.is_relative_to(source) and not source.is_relative_to(root),
             "WORK_SOURCE_OVERLAP")
        root.mkdir(mode=0o700)
        private = root
        result_path = envelope_private / "CATALOGUE_RESULT.json"
        need(not os.path.lexists(result_path), "RESULT_ALREADY_EXISTS")
        home = private / "home"
        home.mkdir(mode=0o700)
        need(signal.getsignal(signal.SIGCHLD) == signal.SIG_DFL,
             "CHILD_REAP_POLICY_UNREVIEWED")
        source_store_guard(source)
        source_guard(source, gate_home)
        result["source_identity_verified"] = True
        binary = regular(Path(args.binary).resolve(strict=True))
        need(binary.stat().st_size == BINARY_BYTES and file_sha(binary) == BINARY_SHA,
             "BINARY_IDENTITY_DIFFERS")
        modules = load_transports(transport_root)
        phase = "CURRENTNESS_BEFORE"
        currentness(args, source, gate_home, private, "gate-before")
        result["currentness_before"] = True
        phase = "GIT_ADMISSION_BEFORE"
        git_before, result["git_startup_admission"] = git_startup_guard(home, True, source)
        write_json(private / "GIT_ADMISSION_BEFORE.json", git_before)
        phase = "NATIVE_CONSTRUCTOR"
        native_type = modules["native_transport"].Native
        native = native_type.__new__(native_type)
        native_type.__init__(native, binary, home, source, private / "transport", extra=EXTRA)
        result["native_process_started"] = True
        need(native.binary_sha256 == BINARY_SHA, "LAUNCH_COPY_DIFFERS")
        result["runtime_identity_verified"] = True
        plugin_id = None
        for method in METHODS:
            phase = method
            if method == "initialize":
                params = {"clientInfo": {"name": "dg17_t12_probe", "version": "1.0.0"},
                          "capabilities": {"experimentalApi": True}}
            elif method == "plugin/read":
                params = {"pluginName": "implementaudit",
                          "marketplacePath": str(source / ".claude-plugin/marketplace.json")}
            else:
                params = {"cwds": [str(source)]}
                if method == "skills/list":
                    params["forceReload"] = True
            response = native.rpc(method, params, timeout=20)
            if method == "initialize":
                need(VERSION in response.get("userAgent", ""), "RUNTIME_VERSION_DIFFERS")
                result["runtime_reported_version_matches"] = True
                native.send({"method": "initialized"})
            elif method == "plugin/read":
                result["catalog"], plugin_id = plugin_projection(response, source)
            elif method == "skills/list":
                result["configured_skills"] = skills_projection(response, source, plugin_id)
            else:
                result["configured_hooks"] = hooks_projection(response, source, plugin_id)
            result["calls"].append({"method": method, "status": "OBSERVED"})
        phase = "COMPLETE"
    except BaseException as exc:
        primary_error = exc
        result["failure"] = {"phase": phase,
                             "code": str(exc) if isinstance(exc, Refusal) else "OPERATION_EXCEPTION",
                             "exception_type": type(exc).__name__ if type(exc).__name__ in
                             {"Refusal", "RuntimeError", "TimeoutError", "OSError", "ValueError",
                              "KeyError", "TypeError", "EOFError", "PermissionError", "Empty",
                              "KeyboardInterrupt", "SystemExit", "FileNotFoundError"} else "Exception"}
    finally:
        if native is not None:
            result["native_process_started"] = hasattr(native, "proc")
            try:
                if hasattr(native, "reader") and hasattr(native, "process_identity"):
                    closed = native.close()
                    result["cleanup"].update(
                        close_returned=True, parent_returncode=closed["returncode"],
                        reader_joined=closed["reader_joined"],
                        transport_remaining_owned_count=len(closed["remaining_owned_processes"]))
                else:
                    result["cleanup"]["containment"] = contain_known_parent(native)
            except BaseException as close_error:
                result["cleanup"]["close_returned"] = False
                result["cleanup"]["close_error_type"] = (
                    type(close_error).__name__ if type(close_error).__name__ in
                    {"RuntimeError", "TimeoutExpired", "OSError", "CustodyError",
                     "PermissionError", "FileNotFoundError", "ProcessLookupError",
                     "ValueError", "Refusal", "KeyboardInterrupt"} else "Exception")
                try:
                    result["cleanup"]["containment"] = contain_known_parent(native)
                except BaseException:
                    result["cleanup"]["containment"] = {"status": "CONTAINMENT_REFUSED", "signals_sent": 0}
            if not result["cleanup"]["close_returned"]:
                reader = getattr(native, "reader", None)
                if reader is not None:
                    try:
                        reader.join(timeout=3)
                    except BaseException:
                        pass
                for name in ("capture", "stderr"):
                    stream = getattr(native, name, None)
                    if stream is not None and not stream.closed:
                        try:
                            stream.close()
                        except BaseException:
                            pass
            for event in getattr(native, "events", []):
                if event["direction"] == "send":
                    if event["value"].get("method") not in (*METHODS, "initialized"):
                        result["nonmetadata_outbound_count"] += 1
                elif event["direction"] == "recv_raw":
                    try:
                        obj = json.loads(event["value"])
                        method = obj.get("method", "")
                        if method.startswith(("thread/", "turn/", "hook/")):
                            result["unexpected_lifecycle_notification_count"] += 1
                        if "method" in obj and "id" in obj:
                            result["unexpected_server_request_count"] += 1
                    except (ValueError, TypeError, AttributeError):
                        result["unexpected_server_request_count"] += 1
            try:
                result["cleanup"]["after_close"] = independent_readback(native, modules)
            except BaseException:
                result["cleanup"]["after_close"] = None
        if git_before is not None:
            try:
                git_after, after_public = git_startup_guard(home, False, source)
                write_json(private / "GIT_ADMISSION_AFTER.json", git_after)
                result["git_startup_admission"].update(
                    after_passed=True, identities_unchanged=git_after == git_before,
                    after_identity_sha256=after_public["before_identity_sha256"])
                need(git_after == git_before, "GIT_ADMISSION_READBACK_CHANGED")
            except BaseException as git_error:
                if primary_error is None:
                    primary_error = git_error
                    result["failure"] = {
                        "phase": "GIT_ADMISSION_AFTER",
                        "code": str(git_error) if isinstance(git_error, Refusal)
                                else "GIT_ADMISSION_READBACK_EXCEPTION",
                        "exception_type": "Refusal" if isinstance(git_error, Refusal)
                                          else "Exception"}
        if private is not None and result["currentness_before"]:
            try:
                currentness(args, source, gate_home, private, "gate-after")
                result["currentness_after"] = True
            except BaseException:
                result["currentness_after"] = False
        if private is not None:
            try:
                seal = private_seal_rows(private)
                seal_path = private / "PRIVATE_EVIDENCE_SEAL.json"
                write_json(seal_path, {"schema": "dg17.t12.private-byte-seal.v1", "files": seal})
                result["private_evidence_seal_sha256"] = file_sha(seal_path)
                if native is not None:
                    result["cleanup"]["after_seal"] = independent_readback(native, modules)
                result["cleanup"]["private_seal_unchanged"] = (
                    private_seal_rows(private) == seal and
                    file_sha(seal_path) == result["private_evidence_seal_sha256"])
            except BaseException:
                result["cleanup"]["private_seal_unchanged"] = False
        snapshots = [result["cleanup"]["after_close"], result["cleanup"]["after_seal"]]
        clean = (result["cleanup"]["close_returned"] and
                 result["cleanup"]["parent_returncode"] == 0 and
                 result["cleanup"]["reader_joined"] and
                 result["cleanup"]["transport_remaining_owned_count"] == 0 and
                 result["cleanup"]["private_seal_unchanged"] and
                 all(s is not None and s["full_session_scope_available"] and
                     s["living_owned_processes"] == s["owned_zombies"] ==
                     s["uncertain_owned_candidates"] == 0 and
                     s["launch_directory_empty"] for s in snapshots))
        catalog_ok = result["catalog"] is not None and result["catalog"]["five_exact_skill_paths"]
        git_ok = (result["git_startup_admission"] is not None and
                  result["git_startup_admission"]["before_passed"] and
                  result["git_startup_admission"]["after_passed"] and
                  result["git_startup_admission"]["identities_unchanged"] and
                  result["git_startup_admission"]["before_identity_sha256"] ==
                  result["git_startup_admission"]["after_identity_sha256"])
        result["status"] = ("OBSERVED_CATALOG_AND_PRESENT_CLEANUP"
                            if primary_error is None and catalog_ok and clean and git_ok and
                            result["currentness_before"] and result["currentness_after"] and
                            result["nonmetadata_outbound_count"] == 0 and
                            result["unexpected_lifecycle_notification_count"] == 0 and
                            result["unexpected_server_request_count"] == 0
                            else "INCOMPLETE_OR_FAILED")
        if result_path is not None:
            need(len(json.dumps(result, sort_keys=True, indent=2).encode()) + 1 <= 65536,
                 "PUBLIC_EXPORT_LIMIT")
            write_json(result_path, result)
        print(json.dumps(result, sort_keys=True))
    return 0 if result["status"] == "OBSERVED_CATALOG_AND_PRESENT_CLEANUP" else 1


if __name__ == "__main__":
    raise SystemExit(main())

