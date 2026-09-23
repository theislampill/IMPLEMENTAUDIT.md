"""Bounded command-read evidence policy, independent of host-run orchestration.

Consumes a retained command record and an already-attested host profile; returns
content-read, not-content-read or fail-closed. It does not mint attestations,
launch commands, write custody, select sessions, or import evaluator/controller
implementations. Path canonicalisation still observes realpath; it is intentionally
NOT a claim of a filesystem-free pure function or a general shell interpreter.

The stateless class preserves existing adapter helper dispatch by inheritance.
It is also usable directly without constructing or importing any host adapter.
"""
from __future__ import annotations

import os
import re
import shlex


class HostCommandPolicy:
    """Owner of the bounded shell grammar and command-to-read-evidence decision."""

    @staticmethod
    def _canonical_trace_path(observed, repo):
        if not isinstance(observed, str) or not observed or "\x00" in observed:
            return None
        text = observed.replace("\\", "/")
        if any(part == ".." for part in text.split("/")):
            return None
        root_native = os.path.abspath(repo)
        root = root_native.replace("\\", "/").rstrip("/")
        if os.path.isabs(observed):
            candidate = os.path.abspath(observed).replace("\\", "/")
        else:
            candidate = os.path.abspath(os.path.join(
                repo, *text.split("/"))).replace("\\", "/")
        if candidate != root and not candidate.startswith(root + "/"):
            return None
        # Lexical aliases through a symlink/junction do not establish exact
        # fixture-file identity without host-retained accessed-path evidence.
        real_candidate = os.path.realpath(candidate).replace(
            "\\", "/").rstrip("/")
        real_root = os.path.realpath(root_native).replace(
            "\\", "/").rstrip("/")
        if ((real_candidate != candidate.rstrip("/")) or
                (real_candidate != real_root and
                 not real_candidate.startswith(real_root + "/"))):
            return None
        return candidate.rstrip("/")

    @classmethod
    def _trace_path_match(cls, observed, expected, repo):
        obs = cls._canonical_trace_path(observed, repo)
        exp = cls._canonical_trace_path(expected, repo)
        return bool(obs and exp and obs == exp)

    @staticmethod
    def _command_name(token):
        name = str(token or "").replace("\\", "/").rsplit("/", 1)[-1]
        name = name.lower()
        return name[:-4] if name.endswith(".exe") else name

    @classmethod
    def _resolved_command(cls, stage, profile):
        """Resolve a small, explicitly supported transparent-wrapper set."""
        tokens = list(stage)
        index = 0
        assignment = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
        while index < len(tokens):
            while index < len(tokens) and assignment.match(tokens[index]):
                if tokens[index].split("=", 1)[0] in (
                        "PATH", "CDPATH", "ENV", "BASH_ENV", "SHELL"):
                    return "<unsupported>", tokens[index:]
                index += 1
            if index >= len(tokens):
                return None, []
            executable = tokens[index]
            name = cls._command_name(executable)
            index += 1
            normalized = executable.replace("\\", "/")
            expected_identity = (profile.get("executables") or {}).get(name)
            if expected_identity is None:
                return "<unsupported>", tokens[index:]
            expected_normalized = expected_identity.replace("\\", "/")
            if "/" in normalized and normalized != expected_normalized:
                return "<unsupported>", tokens[index:]
            if "/" in normalized and expected_normalized.startswith("builtin:"):
                return "<unsupported>", tokens[index:]
            if name == "command":
                if index < len(tokens) and tokens[index] in ("-v", "-V"):
                    return None, []
                if index < len(tokens) and tokens[index] == "-p":
                    index += 1
                continue
            if name in ("env", "sudo", "xargs") and index < len(tokens) and \
                    tokens[index] in ("--help", "--version"):
                return None, []
            if name == "exec" and index < len(tokens) and \
                    tokens[index] == "-a":
                if index + 1 >= len(tokens):
                    return "<unsupported>", []
                index += 2
            if name == "env":
                while index < len(tokens):
                    option = tokens[index]
                    if option in ("-i", "--ignore-environment"):
                        index += 1
                    elif option in ("-u", "--unset"):
                        if index + 1 >= len(tokens):
                            return "<unsupported>", []
                        index += 2
                    elif option.startswith("--unset="):
                        index += 1
                    else:
                        break
                while index < len(tokens) and assignment.match(tokens[index]):
                    if tokens[index].split("=", 1)[0] in (
                            "PATH", "CDPATH", "ENV", "BASH_ENV", "SHELL"):
                        return "<unsupported>", tokens[index:]
                    index += 1
                continue
            if name == "sudo":
                while index < len(tokens):
                    option = tokens[index]
                    if option in ("-n", "--non-interactive"):
                        index += 1
                    elif option in ("-u", "--user"):
                        if index + 1 >= len(tokens):
                            return "<unsupported>", []
                        index += 2
                    elif option.startswith("--user="):
                        index += 1
                    else:
                        break
                continue
            if name == "exec":
                continue
            if name == "xargs":
                # Raw aggregate events do not retain expanded child argv or
                # per-child status. Never infer content reads through xargs.
                return "<xargs-unsupported>", tokens[index:]
            return name, tokens[index:]
        return None, []

    @staticmethod
    def _target_mentioned(command, expected):
        text = str(command or "").replace("\\", "/")
        target = str(expected).replace("\\", "/").strip("/")
        return bool(target and target in text)

    @staticmethod
    def _replace_process_substitutions(text):
        """Replace balanced POSIX process substitutions with /dev/null.

        Their generated streams are not reads of path-looking text inside the
        substitution. Unbalanced forms remain untouched and fail parsing.
        """
        result = []
        index = 0
        while index < len(text):
            if index + 1 < len(text) and text[index:index + 2] in ("<(", ">("):
                depth = 1
                quote = None
                escaped = False
                end = index + 2
                while end < len(text) and depth:
                    char = text[end]
                    if escaped:
                        escaped = False
                    elif quote:
                        if char == quote:
                            quote = None
                        elif quote == '"' and char == "\\":
                            escaped = True
                    elif char in ("'", '"'):
                        quote = char
                    elif char == "\\":
                        escaped = True
                    elif char == "(":
                        depth += 1
                    elif char == ")":
                        depth -= 1
                    end += 1
                if depth:
                    return None
                result.append("/dev/null")
                index = end
                continue
            result.append(text[index])
            index += 1
        return "".join(result)

    @staticmethod
    def _unsupported_unquoted_syntax(text):
        quote = None
        escaped = False
        index = 0
        while index < len(text):
            char = text[index]
            if char == "\x00" or char in "\r\n":
                return True
            if escaped:
                escaped = False
                index += 1
                continue
            if quote:
                if char == quote:
                    quote = None
                elif quote == '"' and char == "\\":
                    escaped = True
                elif quote == '"' and char in ("$", "`"):
                    return True
                index += 1
                continue
            if char == "\\":
                escaped = True
            elif char in ("'", '"'):
                quote = char
            elif char == "`" or char in "(){}*?[~":
                return True
            elif char == "$":
                following = text[index + 1:index + 2]
                if following == "(" or following == "{" or \
                        following == "_" or following.isalpha():
                    return True
            index += 1
        return quote is not None

    @staticmethod
    def _has_dynamic_expansion(text):
        """Detect shell expansion outside single-quoted literal data."""
        quote = None
        escaped = False
        for char in str(text or ""):
            if escaped:
                escaped = False
                continue
            if char == "\\" and quote != "'":
                escaped = True
                continue
            if char in ("'", '"'):
                if quote is None:
                    quote = char
                elif quote == char:
                    quote = None
                continue
            if char in ("$", "`", "*", "?", "[", "{", "~") and \
                    quote != "'":
                return True
        return False

    @classmethod
    def _unwrap_host_command(cls, command, source,
                             wrapper_host_owned=False):
        """Unwrap only the frozen, host-owned Codex bash login envelope."""
        text = str(command or "")
        try:
            tokens = shlex.split(text, posix=True)
        except ValueError:
            return text, False
        if (wrapper_host_owned and
                source == "codex-command-completed" and len(tokens) == 3 and
                tokens[0] in ("/bin/bash", "/usr/bin/bash") and
                tokens[1] == "-lc"):
            return tokens[2], True
        return text, False

    @staticmethod
    def _shell_tokens(text, dialect="posix"):
        """Retain word/operator and IO-number identity in the finite grammar.

        This is lexical bookkeeping, not expansion or a general shell parser.
        The existing syntax gate still refuses unsupported constructs. shlex
        decodes each already bounded word; quoted operators remain argv data,
        and only unquoted digits adjacent to a redirection are descriptors.
        """
        tokens = []
        index = 0
        punctuation = ";&|<>"
        while index < len(text):
            if text[index].isspace():
                index += 1
                continue
            if text[index] == "#":
                break  # A comment starts only at the beginning of a word.
            start = index
            if text[index] in punctuation:
                while index < len(text) and text[index] in punctuation:
                    index += 1
                tokens.append((text[start:index], "operator"))
                continue
            quote = None
            while index < len(text):
                char = text[index]
                if quote:
                    if char == quote:
                        quote = None
                    elif quote == '"' and char == "\\":
                        index += 1
                elif char in ("'", '"'):
                    quote = char
                elif char == "\\":
                    index += 1
                elif char.isspace() or char in punctuation:
                    break
                index += 1
            if quote or index > len(text):
                return None
            raw = text[start:index]
            if dialect != "posix":
                # Do not borrow POSIX escape/quote concatenation semantics for
                # native Windows records. Only plain words or one complete
                # quoted word are supported; other spellings require a native
                # grammar/receipt and remain explicit refusals in this leaf.
                if any(char in raw for char in "\\`^$%!"):
                    return None
                if dialect == "cmd" and "'" in raw:
                    return None
                if any(char in raw for char in "\"'"):
                    if (raw[0] not in ("'", '"') or
                            len(raw) < 2 or raw[-1] != raw[0] or
                            raw[0] in raw[1:-1]):
                        return None
            try:
                words = shlex.split(raw, posix=True, comments=False)
            except ValueError:
                return None
            if len(words) != 1:
                return None
            kind = "fd" if (re.fullmatch(r"[0-9]+", raw) and
                            text[index:index + 1] in ("<", ">")) else "word"
            tokens.append((words[0], kind))
        return tokens

    @staticmethod
    def _split_redirections(tokens):
        """Return argv, the effective stdin path, write paths, or an error.

        Shell redirections apply left-to-right. Earlier opens are not content
        reads after fd 0 is replaced. Unsupported fd duplication fails closed.
        """
        argv = []
        inputs = []
        outputs = []
        index = 0
        redirs = {"<", ">", ">>", "<>", ">&", "<&", "<<<", "<<"}
        while index < len(tokens):
            token, kind = tokens[index]
            fd = None
            if kind == "fd":
                if (index + 1 >= len(tokens) or
                        tokens[index + 1][1] != "operator" or
                        tokens[index + 1][0] not in redirs):
                    return None, None, None
                fd = int(token)
                index += 1
                token, kind = tokens[index]
            if kind == "word":
                argv.append(token)
                index += 1
                continue
            if token not in redirs or index + 1 >= len(tokens):
                return None, None, None
            operand, operand_kind = tokens[index + 1]
            if operand_kind != "word":
                return None, None, None
            index += 2
            if token in (">&", "<&"):
                if operand != "-" and not operand.isdigit():
                    return None, None, None
                destination = fd if fd is not None else (0 if token == "<&" else 1)
                if destination == 0:
                    if operand == "-":
                        inputs = []
                    elif operand != "0":
                        return None, None, None  # No model of other fd contents.
                continue
            if token in ("<<<", "<<"):
                # Here strings/documents replace stdin with literal data.
                if fd in (None, 0):
                    inputs = []
                continue
            if token in ("<", "<>"):
                if fd in (None, 0):
                    inputs = [operand]
                if token == "<>" and fd in (None, 0, 1):
                    outputs.append(operand)
            elif token in (">", ">>"):
                outputs.append(operand)
                if fd == 0:
                    inputs = []
        return argv, inputs, outputs

    @classmethod
    def _token_path_state(cls, operand, expected, repo):
        if not isinstance(operand, str):
            return "ambiguous"
        if any(mark in operand for mark in ("$", "`", "*", "?", "[", "]")):
            return "ambiguous" if cls._target_mentioned(operand, expected) \
                else "other"
        # Operands are execution identities, not prose with punctuation.
        observed = cls._canonical_trace_path(operand, repo)
        wanted = cls._canonical_trace_path(expected, repo)
        if observed and wanted and observed == wanted:
            return "exact"
        return "other"

    @classmethod
    def _output_identifies_path(cls, output, expected, repo):
        """Recognize a search-result filename only at the line's source edge."""
        wanted = cls._canonical_trace_path(expected, repo)
        if not wanted:
            return False
        relative = os.path.relpath(wanted, os.path.abspath(repo)).replace(
            "\\", "/")
        absolute = wanted.replace("\\", "/")
        for raw_line in str(output or "").splitlines():
            line = raw_line.strip().replace("\\", "/")
            if (line == relative or line.startswith(relative + ":") or
                    line == absolute or line.startswith(absolute + ":")):
                return True
        return False

    @classmethod
    def _scope_contains_target(cls, scope, expected, repo):
        observed = cls._canonical_trace_path(scope, repo)
        wanted = cls._canonical_trace_path(expected, repo)
        return bool(observed and wanted and
                    (wanted == observed or wanted.startswith(observed + "/")))

    @staticmethod
    def _grep_short_options(token):
        """Expand a finite grep cluster without interpreting option data as flags.

        -e/-f/-m take the rest of the token (or the next argv element). Other
        argument-taking or unknown clustered options remain unsupported.
        """
        options = []
        for index, flag in enumerate(token[1:], 1):
            if flag in "efm":
                options.append("-" + flag)
                if token[index + 1:]:
                    options.append(token[index + 1:])
                return options
            if flag not in "EFGPivwxyznHhbcLlqosIRZaUVur":
                return None
            options.append("-" + flag)
        return options

    @staticmethod
    def _reader_inputs(operands, stdin_paths, implicit=False):
        """Resolve stdin only for a command's supported input-operand role."""
        if implicit and not operands:
            return list(stdin_paths)
        paths = []
        for operand in operands:
            paths.extend(stdin_paths if operand == "-" else [operand])
        return paths

    @staticmethod
    def _sed_consumption(programs, external_program):
        """Finite script effects, not a sed interpreter or script-file reader.

        Empty programmes and unaddressed/numeric-addressed p, d and = drain
        inputs. Literal q/Q can stop on the first nonempty input, so only the
        first operand is guaranteed to be attempted. Everything else is
        unmodelled, including programme files whose bytes are not in the record.
        """
        if external_program:
            return "unknown"
        effect = "all"
        for program in programs:
            for command in program.split(";"):
                command = command.strip()
                if command in ("q", "Q"):
                    effect = "first"
                elif command and re.fullmatch(
                        r"(?:(?:[0-9]+|\$)(?:,(?:[0-9]+|\$))?)?[pd=]",
                        command) is None:
                    return "unknown"
        return effect

    @classmethod
    def _reader_effect(cls, name, args, stdin_paths, expected, repo, output,
                       shell_dialect):
        """Return ``read``, ``not``, or ``ambiguous`` for one shell stage."""
        if name in ("<unsupported>", "<xargs-unsupported>"):
            return "ambiguous" if any(
                cls._target_mentioned(token, expected)
                for token in args) else "not"
        if name in (None, "true", "false", "exit", "printf", "echo",
                    "find", "ls", "stat", "git", "touch", "tee"):
            return "not"
        if name in ("sh", "bash", "cmd", "powershell", "pwsh"):
            return "ambiguous" if any(
                cls._target_mentioned(token, expected)
                for token in args) else "not"

        # A redirected fd is only an open input, not proof of consumption.
        # Each reader below supplies its own file and pattern-input roles.
        direct = []
        scopes = []
        terminal_no_read = False
        uncertain_read = False
        reader = name in ("cat", "sed", "head", "tail", "get-content",
                          "type", "rg", "grep")
        if not reader:
            return "ambiguous" if any(
                cls._target_mentioned(token, expected)
                for token in args) else "not"
        dialect_readers = {
            "posix": {"cat", "sed", "head", "tail", "rg", "grep"},
            "powershell": {"get-content", "rg", "grep"},
            "cmd": {"type", "rg", "grep"},
        }
        if name not in dialect_readers.get(shell_dialect, set()):
            return "ambiguous" if any(
                cls._target_mentioned(token, expected)
                for token in args + stdin_paths) else "not"
        if name == "cat":
            operands = []
            options_ended = False
            for arg in args:
                if not options_ended and arg == "--":
                    options_ended = True
                elif not options_ended and arg in ("--help", "--version"):
                    return "not"
                elif not options_ended and arg.startswith("-") and arg != "-":
                    if arg in ("--show-all", "--number-nonblank", "--show-ends",
                               "--number", "--squeeze-blank", "--show-tabs",
                               "--show-nonprinting"):
                        continue
                    if arg.startswith("--") or any(flag not in "AbeEnstTuv" for flag in arg[1:]):
                        return "ambiguous"
                else:
                    operands.append(arg)
            direct.extend(cls._reader_inputs(operands, stdin_paths, implicit=True))
        elif name == "type":
            # cmd TYPE has no POSIX stdin/option grammar. A help invocation
            # and unmodelled multiple-file/errorlevel behaviour prove no read.
            if any(arg.lower() == "/?" for arg in args):
                return "not"
            if (len(args) != 1 or args[0].startswith("/") or
                    any(mark in args[0] for mark in (",", "+"))):
                return "ambiguous"
            direct.extend(args)  # '-' is a literal filename, not stdin.
        elif name in ("head", "tail"):
            operands = []
            index = 0
            while index < len(args):
                arg = args[index]
                count = None
                if arg == "--":
                    operands.extend(args[index + 1:])
                    break
                if arg in ("--help", "--version"):
                    return "not"
                if arg in ("-n", "--lines", "-c", "--bytes"):
                    if index + 1 >= len(args):
                        return "ambiguous"
                    count = args[index + 1]
                    index += 2
                elif arg.startswith(("--lines=", "--bytes=")):
                    count = arg.split("=", 1)[1]
                    index += 1
                elif arg.startswith(("-n", "-c")) and len(arg) > 2:
                    count = arg[2:]
                    index += 1
                elif re.fullmatch(r"-[0-9]+", arg):
                    count = arg[1:]
                    index += 1
                elif arg in ("-q", "--quiet", "--silent", "-v", "--verbose",
                             "-z", "--zero-terminated"):
                    index += 1
                elif arg.startswith("-") and arg != "-":
                    # Unknown/abbreviated options may select a no-read mode.
                    # Do not infer their semantics from a later filename.
                    return "ambiguous"
                else:
                    operands.append(arg)
                    index += 1
                if count is not None:
                    match = re.fullmatch(r"([+-]?)([0-9]+)(?:[bBkKMGTPEZYRQ](?:i?B)?)?", count)
                    if match is None:
                        return "ambiguous"
                    sign, digits = match.groups()
                    # Options are applied in order. head -n -0 means all but
                    # zero; tail -n +0 means from the start, not zero output.
                    terminal_no_read = (not digits.strip("0") and not (
                        (name == "head" and sign == "-") or
                        (name == "tail" and sign == "+")))
            direct.extend(cls._reader_inputs(operands, stdin_paths, implicit=True))
        elif name == "get-content":
            # Only single literal-path content acquisition is modelled here.
            # Filters, streams, wildcards, parameter abbreviations and arrays
            # can select/skip other inputs; do not silently ignore switches.
            index = 0
            seen = set()
            while index < len(args):
                arg = args[index]
                lower = arg.lower()
                if lower == "-?":
                    return "not"
                if lower in ("-delimiter", "-totalcount", "-tail",
                             "-readcount", "-encoding", "-literalpath", "-path"):
                    if index + 1 >= len(args) or lower in seen:
                        return "ambiguous"
                    seen.add(lower)
                    value = args[index + 1]
                    if lower in ("-totalcount", "-tail", "-readcount"):
                        if re.fullmatch(r"[0-9]+", value) is None:
                            return "ambiguous"
                        if lower != "-readcount":
                            terminal_no_read = not value.strip("0")
                    elif lower in ("-literalpath", "-path"):
                        direct.append(value)
                    index += 2
                elif lower in ("-raw", "-asbytestream", "-force"):
                    if lower in seen:
                        return "ambiguous"
                    seen.add(lower)
                    index += 1
                elif arg.startswith("-"):
                    return "ambiguous"
                else:
                    direct.append(arg)
                    index += 1
            if (("-tail" in seen and "-totalcount" in seen) or
                    len(direct) != 1 or "," in direct[0]):
                return "ambiguous"
        elif name == "sed":
            index = 0
            saw_program = False
            options_ended = False
            programs = []
            external_program = False
            while index < len(args):
                arg = args[index]
                if arg == "--":
                    options_ended = True
                    index += 1
                    break
                if arg in ("--help", "--version"):
                    return "not"
                if arg in ("-e", "--expression"):
                    if index + 1 >= len(args):
                        return "ambiguous"
                    programs.append(args[index + 1])
                    saw_program = True
                    index += 2
                elif arg.startswith("-e") and len(arg) > 2:
                    programs.append(arg[2:])
                    saw_program = True
                    index += 1
                elif arg in ("-f", "--file"):
                    if index + 1 >= len(args):
                        return "ambiguous"
                    direct.extend(cls._reader_inputs([args[index + 1]], stdin_paths))
                    external_program = saw_program = True
                    index += 2
                elif arg.startswith("-f") and len(arg) > 2:
                    direct.extend(cls._reader_inputs([arg[2:]], stdin_paths))
                    external_program = saw_program = True
                    index += 1
                elif arg in ("-n", "--quiet", "--silent", "-E", "-r",
                             "--regexp-extended", "-s", "--separate", "-u",
                             "--unbuffered", "-z", "--null-data", "--posix"):
                    index += 1
                elif arg.startswith("-") and arg != "-":
                    return "ambiguous"
                elif not saw_program:
                    programs.append(arg)
                    saw_program = True
                    index += 1
                else:
                    break
            remaining = args[index:]
            if not saw_program:
                if not remaining:
                    return "not"
                programs.append(remaining[0])
                remaining = remaining[1:]
            if not options_ended and any(arg.startswith("-") and arg != "-" for arg in remaining):
                return "ambiguous"
            operands = remaining or ["-"]
            consumption = cls._sed_consumption(programs, external_program)
            if consumption == "all":
                direct.extend(cls._reader_inputs(operands, stdin_paths))
            else:
                # Preserve operand positions *before* resolving '-' to stdin.
                # An unbound/closed first stdin is not permission to promote a
                # later filename to the guaranteed-first-input position.
                if consumption == "first":
                    direct.extend(cls._reader_inputs(operands[:1], stdin_paths))
                    operands = operands[1:]
                uncertain_read = any(
                    cls._token_path_state(path, expected, repo) != "other"
                    for path in cls._reader_inputs(operands, stdin_paths))
        else:  # grep / rg
            args = list(args)  # Cluster expansion must not mutate caller argv.
            index = 0
            pattern_supplied = False
            pattern_files = []
            external_patterns = False
            literal_patterns = []
            invert_match = False
            zero_matches = False
            quiet = False
            options_ended = False
            output_identity_safe = True
            unsafe_output_modes = {
                "--no-filename", "-I", "--replace", "-r", "--json",
                "--vimgrep", "--count", "--count-matches",
                "--files-with-matches", "-l", "--files-without-match",
                "--only-matching", "-o", "--passthru", "--heading",
                "-h", "--null", "-0", "--null-data", "--stats"}
            unsafe_output_options_with_value = {
                "--label", "--path-separator", "--field-match-separator",
                "--field-context-separator"}
            # The two tools assign different meanings to flags such as -r
            # and -h. Unknown/abbreviated options are not evidence of reads.
            grep_flags = {"-" + flag for flag in "EFGPivwxyznHhbcLlqosIRZaUur"} | {
                "--basic-regexp", "--extended-regexp", "--fixed-strings", "--perl-regexp",
                "--ignore-case", "--word-regexp", "--line-regexp", "--invert-match",
                "--line-number", "--with-filename", "--no-filename", "--byte-offset",
                "--count", "--files-with-matches", "--files-without-match", "--only-matching",
                "--no-messages", "--recursive", "--dereference-recursive", "--text",
                "--binary", "--unix-byte-offsets", "--null", "--null-data", "--line-buffered"}
            rg_flags = {"-F", "-i", "-s", "-S", "-w", "-x", "-v", "-n", "-N",
                        "-H", "-I", "-c", "-l", "-o", "-0", "-a", "-z", "-L",
                        "--fixed-strings", "--ignore-case", "--case-sensitive", "--smart-case",
                        "--word-regexp", "--line-regexp", "--invert-match", "--line-number",
                        "--no-line-number", "--with-filename", "--no-filename", "--text",
                        "--search-zip", "--follow", "--json", "--vimgrep", "--count",
                        "--count-matches", "--files-with-matches", "--files-without-match",
                        "--only-matching", "--passthru", "--heading", "--no-heading",
                        "--null", "--null-data", "--stats"}
            while index < len(args):
                arg = args[index]
                if arg == "--":
                    options_ended = True
                    index += 1
                    break
                if (name == "grep" and arg.startswith("-") and
                        not arg.startswith("--") and len(arg) > 2):
                    expanded = cls._grep_short_options(arg)
                    if expanded is None:
                        return "ambiguous"
                    args[index:index + 1] = expanded
                    arg = args[index]
                if arg in ("--help", "--version", "-V") or (name == "rg" and arg in ("-h", "--files")):
                    return "not"
                if arg in ("-m", "--max-count") or arg.startswith("--max-count=") or (
                        arg.startswith("-m") and len(arg) > 2):
                    if arg in ("-m", "--max-count"):
                        if index + 1 >= len(args):
                            return "ambiguous"
                        count = args[index + 1]
                        index += 2
                    else:
                        count = arg.split("=", 1)[1] if arg.startswith("--") else arg[2:]
                        index += 1
                    if re.fullmatch(r"[0-9]+", count) is None:
                        return "ambiguous"
                    zero_matches = not count.strip("0")
                elif arg in ("-q", "--quiet", "--silent"):
                    quiet = True
                    output_identity_safe = False
                    index += 1
                elif arg.startswith("--max-"):
                    return "ambiguous"  # No abbreviation/unknown limit semantics.
                elif arg in ("-e", "--regexp"):
                    if index + 1 >= len(args):
                        return "ambiguous"
                    literal_patterns.append(args[index + 1])
                    pattern_supplied = True
                    index += 2
                elif arg.startswith("-e") and len(arg) > 2:
                    literal_patterns.append(arg[2:])
                    pattern_supplied = True
                    index += 1
                elif arg in ("-f", "--file"):
                    if index + 1 >= len(args):
                        return "ambiguous"
                    pattern_files.extend(cls._reader_inputs([args[index + 1]], stdin_paths))
                    external_patterns = pattern_supplied = True
                    index += 2
                elif arg.startswith("-f") and len(arg) > 2:
                    pattern_files.extend(cls._reader_inputs([arg[2:]], stdin_paths))
                    external_patterns = pattern_supplied = True
                    index += 1
                elif name == "rg" and arg in ("-g", "--glob", "--type", "--type-add"):
                    if index + 1 >= len(args):
                        return "ambiguous"
                    index += 2
                elif name == "rg" and arg in ("--replace", "-r"):
                    output_identity_safe = False
                    if index + 1 >= len(args):
                        return "ambiguous"
                    index += 2
                elif name == "rg" and (arg.startswith("--replace=") or (
                        arg.startswith("-r") and len(arg) > 2)):
                    output_identity_safe = False
                    index += 1
                elif arg in ({"--label"} if name == "grep" else unsafe_output_options_with_value):
                    output_identity_safe = False
                    if index + 1 >= len(args):
                        return "ambiguous"
                    index += 2
                elif any(arg.startswith(option + "=")
                         for option in ({"--label"} if name == "grep" else unsafe_output_options_with_value)):
                    output_identity_safe = False
                    index += 1
                elif arg in (grep_flags if name == "grep" else rg_flags):
                    if arg in ("-v", "--invert-match"):
                        invert_match = True
                    if arg in unsafe_output_modes:
                        output_identity_safe = False
                    index += 1
                elif arg.startswith("-") and arg != "-":
                    return "ambiguous"
                else:
                    break
            remaining = args[index:]
            if not options_ended and any(arg.startswith("-") and arg != "-" for arg in remaining):
                # GNU option permutation is outside this finite adapter. A
                # later limit must not silently become a filename/read proof.
                return "ambiguous"
            if not pattern_supplied:
                if not remaining:
                    return "not"
                literal_patterns.append(remaining[0])
                remaining = remaining[1:]
            # No named search operands selects stdin; pattern-file stdin is
            # a separate, earlier consumption even when searching is disabled.
            direct = list(pattern_files)
            if not remaining and stdin_paths:
                remaining = ["-"]
            if zero_matches:
                # Pattern files are still opened to compile expressions, but
                # a zero match limit provides no search-input/STDIN read proof.
                direct = pattern_files
                remaining = []
            if not zero_matches and (external_patterns or (
                    name == "grep" and invert_match and "" in literal_patterns)):
                # Empty pattern files can return no-match without even opening
                # the search inputs. GNU grep also short-circuits an inverted
                # empty literal pattern. The record does not bind pattern-file
                # contents, so do not infer consumption from exit 0/1 or output.
                # Pattern-file reads themselves precede this search decision.
                uncertain_read = any(
                    cls._token_path_state(path, expected, repo) != "other" or
                    cls._scope_contains_target(path, expected, repo)
                    for path in cls._reader_inputs(remaining, stdin_paths))
                remaining = []
            if quiet and not zero_matches:
                # A successful quiet search can stop before opening later
                # operands (even after an earlier error). Pattern-file reads
                # remain distinct; they precede the search itself.
                if len(remaining) > 1:
                    uncertain_read = any(
                        cls._token_path_state(operand, expected, repo) != "other"
                        or cls._scope_contains_target(operand, expected, repo)
                        for operand in cls._reader_inputs(remaining, stdin_paths))
                    remaining = []
            for operand in cls._reader_inputs(remaining, stdin_paths):
                state = cls._token_path_state(operand, expected, repo)
                if state == "exact":
                    direct.append(operand)
                elif (state == "other" and
                      output_identity_safe and
                      cls._scope_contains_target(operand, expected, repo) and
                      cls._output_identifies_path(output, expected, repo)):
                    scopes.append(operand)

        if terminal_no_read:
            return "not"
        states = [cls._token_path_state(path, expected, repo)
                  for path in direct]
        if "exact" in states or scopes:
            return "read"
        if "ambiguous" in states or uncertain_read:
            return "ambiguous"
        return "not"

    @classmethod
    def _parse_shell(cls, command, expected, repo, output, source, profile,
                     wrapper_host_owned=False):
        text, _unwrapped = cls._unwrap_host_command(
            command, source, wrapper_host_owned)
        if "\n" in text or "\r" in text:
            heredoc = re.fullmatch(
                r"(?s)(?P<head>.*)<<-?\s*(?P<tag>[A-Za-z_][A-Za-z0-9_]*)"
                r"\r?\n.*\r?\n(?P=tag)\s*", text)
            if heredoc:
                text = heredoc.group("head") + " << " + heredoc.group("tag")
        replaced = cls._replace_process_substitutions(text)
        if replaced is None or cls._unsupported_unquoted_syntax(replaced):
            return None
        tokens = cls._shell_tokens(replaced, profile.get("shell_dialect"))
        if tokens is None:
            return None
        if not tokens:
            return [], []
        separators = {"|", "|&", "&&", "||", ";"}
        unsupported = {"&", ";;", ";&", ";;&"}
        if profile.get("shell_dialect") != "posix" and any(
                kind == "operator" and token in separators | unsupported |
                {"<", ">", ">>", "<>", ">&", "<&", "<<<", "<<"}
                for token, kind in tokens):
            return None
        if ((tokens[0][1] == "operator" and
             tokens[0][0] in separators | unsupported) or
                (tokens[-1][1] == "operator" and
                 tokens[-1][0] in separators | unsupported)):
            return None
        pipelines = []
        connectors = []
        stages = []
        stage = []
        for token, kind in tokens + [(";", "operator")]:
            if kind == "operator" and token in unsupported:
                return None
            if kind == "operator" and token in ("|", "|&"):
                if not stage:
                    return None
                stages.append(stage)
                stage = []
            elif kind == "operator" and token in ("&&", "||", ";"):
                if not stage:
                    return None
                stages.append(stage)
                pipelines.append(stages)
                stages = []
                stage = []
                if token != ";" or len(pipelines) > 0:
                    connectors.append(token)
            else:
                stage.append((token, kind))
        # The synthetic trailing ';' adds one connector too many.
        connectors = connectors[:max(0, len(pipelines) - 1)]
        parsed = []
        for pipeline in pipelines:
            parsed_stages = []
            for raw_stage in pipeline:
                argv, stdin_paths, outputs = cls._split_redirections(raw_stage)
                if argv is None or not argv:
                    return None
                name, args = cls._resolved_command(argv, profile)
                effect = cls._reader_effect(
                    name, args, stdin_paths, expected, repo, output,
                    profile.get("shell_dialect"))
                constant = True if name == "true" else (
                    False if name == "false" else None)
                terminates = False
                if name == "exit":
                    if len(args) > 1 or (args and not args[0].isdigit()):
                        return None
                    constant = (not args or int(args[0]) == 0)
                    terminates = True
                parsed_stages.append({
                    "name": name, "effect": effect, "constant": constant,
                    "terminates": terminates, "outputs": outputs,
                    "args": args})
            parsed.append(parsed_stages)
        return parsed, connectors

    @classmethod
    def classify_command_target(cls, record, expected, repo, profile):
        """Classify one exact target as content-read/not-read/fail-closed."""
        command = record.get("command")
        source = str(record.get("source") or "")
        if not source.startswith(profile["host"] + "-"):
            return ("fail-closed" if cls._target_mentioned(command, expected)
                    else "not-content-read")
        if (not profile.get("attestation_id") or
                record.get("host_read_attestation_id") !=
                profile.get("attestation_id") or
                record.get("shell_dialect") !=
                profile.get("shell_dialect")):
            return "fail-closed"
        parsed = cls._parse_shell(
            command, expected, repo, record.get("output", ""),
            record.get("source"), profile,
            bool(record.get("wrapper_host_owned")))
        if parsed is None:
            return ("fail-closed" if (
                    cls._target_mentioned(command, expected) or
                    cls._has_dynamic_expansion(command))
                    else "not-content-read")
        pipelines, connectors = parsed
        if not pipelines:
            return "not-content-read"
        if cls._target_mentioned(command, expected):
            known = {
                None,
                "cat", "sed", "head", "tail", "get-content", "type",
                "rg", "grep", "true", "false", "exit", "printf", "echo",
                "find", "ls", "stat", "git", "touch", "tee"}
            for pipeline in pipelines:
                for stage in pipeline:
                    if stage["name"] in (
                            "<unsupported>", "<xargs-unsupported>"):
                        stage["effect"] = "ambiguous"
                    elif stage["name"] not in known:
                        stage["effect"] = "ambiguous"
        # A literal empty printf feeding xargs proves that no child argv was
        # executed. This narrow negative control does not infer any expansion.
        for pipeline in pipelines:
            if (len(pipeline) >= 2 and pipeline[0]["name"] == "printf" and
                    pipeline[0]["args"] == [""] and
                    pipeline[1]["name"] == "<xargs-unsupported>"):
                pipeline[1]["effect"] = "not"
        stage_count = sum(len(pipeline) for pipeline in pipelines)
        if stage_count > 12:
            return ("fail-closed" if cls._target_mentioned(command, expected)
                    else "not-content-read")
        variables = []
        for p_index, pipeline in enumerate(pipelines):
            for s_index, stage in enumerate(pipeline):
                if stage["constant"] is None:
                    variables.append((p_index, s_index))
        if len(variables) > 12:
            return ("fail-closed" if cls._target_mentioned(command, expected)
                    else "not-content-read")
        exit_code = record.get("exit_code")
        if type(exit_code) is not int:
            return "fail-closed"
        wanted_status = exit_code == 0
        worlds = []
        for mask in range(1 << len(variables)):
            statuses = {}
            for bit, key in enumerate(variables):
                statuses[key] = bool(mask & (1 << bit))
            executed = []
            current_status = None
            terminated = False
            for p_index, pipeline in enumerate(pipelines):
                if p_index:
                    connector = connectors[p_index - 1]
                    should_run = (connector == ";" or
                                  (connector == "&&" and current_status) or
                                  (connector == "||" and not current_status))
                    if terminated or not should_run:
                        executed.append([])
                        continue
                pipeline_exec = []
                for s_index, stage in enumerate(pipeline):
                    status = (stage["constant"] if
                              stage["constant"] is not None else
                              statuses[(p_index, s_index)])
                    pipeline_exec.append((stage, status, s_index))
                executed.append(pipeline_exec)
                current_status = pipeline_exec[-1][1]
                if len(pipeline) == 1 and pipeline[0]["terminates"]:
                    terminated = True
            if current_status is None or current_status != wanted_status:
                continue
            read = False
            ambiguous = False
            for p_index, pipeline_exec in enumerate(executed):
                for stage, status, s_index in pipeline_exec:
                    if stage["effect"] == "ambiguous":
                        ambiguous = True
                    elif stage["effect"] == "read":
                        no_match_read = (
                            exit_code == 1 and
                            stage["name"] in ("grep", "rg") and
                            p_index == len(executed) - 1 and
                            s_index == len(pipelines[p_index]) - 1)
                        if status or no_match_read:
                            read = True
            worlds.append((read, ambiguous))
        if not worlds:
            return "fail-closed"
        if all(read and not ambiguous for read, ambiguous in worlds):
            return "content-read"
        if any(read or ambiguous for read, ambiguous in worlds):
            return "fail-closed"
        return "not-content-read"

    @classmethod
    def _command_write_paths(cls, record):
        """Return lexically explicit shell output paths for ordering only."""
        command, _unwrapped = cls._unwrap_host_command(
            record.get("command"), record.get("source"),
            bool(record.get("wrapper_host_owned")))
        replaced = cls._replace_process_substitutions(command)
        if replaced is None or cls._unsupported_unquoted_syntax(replaced):
            return []
        tokens = cls._shell_tokens(replaced, record.get("shell_dialect", "posix"))
        if tokens is None:
            return []
        paths = []
        stage = []
        for token, kind in tokens + [(";", "operator")]:
            if kind == "operator" and token in ("|", "|&", "&&", "||", ";"):
                if stage:
                    _argv, _inputs, outputs = cls._split_redirections(stage)
                    if outputs is not None:
                        paths.extend(outputs)
                stage = []
            else:
                stage.append((token, kind))
        return paths
