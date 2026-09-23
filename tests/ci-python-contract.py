#!/usr/bin/env python3
"""Static guard for the maintained release-validation workflow, not a YAML engine."""
import argparse
import hashlib
from pathlib import Path
import re


def check(workflow: str, verifier: str) -> None:
    # This deliberately requires the maintained job/step layout. A layout change
    # must update the guard consciously, rather than accepting unrelated text.
    active = '\n'.join(line for line in workflow.splitlines() if not line.lstrip().startswith('#'))
    # Freeze the maintained workflow form after dropping inert comments/blank
    # lines. Any new YAML structure needs explicit review, not regex guesswork.
    normal = '\n'.join(line.rstrip() for line in active.splitlines() if line.strip()) + '\n'
    if hashlib.sha256(normal.encode('utf-8')).hexdigest() != 'c0e8e608d4b4ea98c1760c0300ba04b2cf2fc769746c2dd9259bde36d77a79a1':
        raise ValueError('workflow layout changed; review and rebind the maintained contract')
    package = re.search(r'^  package:\n(?P<body>(?:^(?:    .*|)\n?)+)', active, re.M)
    if package is None:
        raise ValueError('package validation job not found')
    body = package.group('body')
    if len(re.findall(r'^  package\s*:', active, re.M)) != 1:
        raise ValueError('duplicate package job is not a maintained layout')
    if re.search(r'^\s*<<\s*:|(?:^|\s)[&*][A-Za-z_]', active, re.M):
        raise ValueError('YAML aliases and merges require an explicit guard update')
    # The release verifier remains unconditional and fail-fast. Only the two
    # evidence steps after it may run conditionally after a verifier failure.
    if re.search(r'^[ \t]*(?:continue-on-error|shell|needs|container)\s*:', active, re.M):
        raise ValueError('failure-swallowing release configuration')
    capture_if = "        if: ${{ always() && steps.verify_package.outcome != 'skipped' }}"
    upload_if = "        if: ${{ always() && steps.capture_package.outcome != 'skipped' }}"
    if re.findall(r'(?m)^[ \t]*if\s*:[^\n]*$', active) != [capture_if, upload_if]:
        raise ValueError('only maintained post-verifier evidence conditions are allowed')
    if len(re.findall(r'^        run: bash scripts/verify-package\.sh$', body, re.M)) != 1:
        raise ValueError('release verifier must be the exact unswallowed command')
    setup = '      - name: Set up release Python\n        uses: actions/setup-python@v5\n        with:\n          python-version: "3.11"'
    install = '      - name: Install validation dependencies\n'
    verify = '      - name: Verify package contract\n        id: verify_package\n        run: bash scripts/verify-package.sh'
    capture = ('      - name: Capture package evidence\n        id: capture_package\n'
               + capture_if + '\n'
               + '        run: python scripts/capture-ci-package-evidence.py --output-dir "$RUNNER_TEMP/package-evidence"')
    upload = ('      - name: Upload package evidence\n' + upload_if + '\n'
              + '        uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02 # v4.6.2')
    if any(body.count(step) != 1 for step in (setup, install, verify, capture, upload)):
        raise ValueError('one explicit release Python setup/install/verify/capture/upload sequence required')
    if not body.index(setup) < body.index(install) < body.index(verify) < body.index(capture) < body.index(upload):
        raise ValueError('Python setup, verification and evidence steps must retain order')
    dependencies = body[body.index(install):body.index('      - name:', body.index(install)+len(install))]
    expected_install = '- name: Install validation dependencies\n        run: |\n          sudo apt-get update\n          sudo apt-get install --yes ripgrep\n          release_python="$(python -c \'import sys; print(sys.executable)\')"\n          printf \'PYTHON_BIN=%s\\n\' "$release_python" >> "$GITHUB_ENV"\n          "$release_python" -m pip install --disable-pip-version-check --no-deps --requirement requirements-release.txt\n          rg --version'
    if dependencies.strip() != expected_install:
        raise ValueError('dependency installation must use the maintained unconditional command block')
    required = [
        'release_python="$(python -c \'import sys; print(sys.executable)\')"',
        'printf \'PYTHON_BIN=%s\\n\' "$release_python" >> "$GITHUB_ENV"',
        '"$release_python" -m pip install --disable-pip-version-check --no-deps --requirement requirements-release.txt',
    ]
    if any(dependencies.count(line) != 1 for line in required):
        raise ValueError('dependencies and PYTHON_BIN must use the selected python executable')
    # Closed interpreter-affecting lines for this maintained layout. Extra setup,
    # environment or PATH overrides must be reviewed rather than silently accepted.
    expected_python_lines = [
        '      - name: Set up release Python',
        '        uses: actions/setup-python@v5',
        '          python-version: "3.11"',
        *('          '+line for line in required),
        '          python -m json.tool .codex-plugin/plugin.json >/dev/null',
        '          python -m json.tool .claude-plugin/plugin.json >/dev/null',
        '          python -m json.tool .claude-plugin/marketplace.json >/dev/null',
        '          python -m json.tool package/implementaudit-package.json >/dev/null',
        '        run: python scripts/capture-ci-package-evidence.py --output-dir "$RUNNER_TEMP/package-evidence"',
        '          path: ${{ runner.temp }}/package-evidence/',
    ]
    affecting = [line for line in body.splitlines()
                 if re.search(r'python|github_env|github_path|\benv:|\bdefaults:|\bpath[=:]', line, re.I)]
    if affecting != expected_python_lines:
        raise ValueError('unreviewed interpreter/environment override')
    prefix = active[:package.start()]
    if re.search(r'^\s*(?:env|defaults):', prefix, re.M):
        raise ValueError('unreviewed global interpreter environment')
    guard = '\n'.join([
        '\"$native_a_g_python\" -c \'import sys; raise SystemExit(0 if sys.version_info[:2] == (3, 11) else 1)\' \\',
        '  || fail \"native A-G fixture controls require an explicit Python 3.11 executable\"',
    ])
    if verifier.count(guard) != 1 or ('# '+guard) in verifier:
        raise ValueError('operative release verifier Python3.11 refusal must remain intact')
    # Binding the actual prefix also detects an outer conditional or early exit
    # around an otherwise byte-identical selection/guard. This is intentionally
    # conservative: earlier verifier edits require explicit contract rebinding.
    prefix = verifier[:verifier.index(guard) + len(guard)]
    if hashlib.sha256(prefix.encode('utf-8')).hexdigest() != '5f9f4a80d5b265c8c642ef160aa4c47fbf2b93b81b46532f71edb4eae8bcd382':
        raise ValueError('verifier prefix changed; guard execution must be re-reviewed')
    # Keep the known top-level selection/guard adjacency. This is a finite
    # maintained-shell-layout check, not a general Bash execution proof.
    selection_start = 'native_a_g_python="${PYTHON_BIN:-}"'
    selection = verifier.split(selection_start)
    if len(selection) != 2:
        raise ValueError('one release interpreter selection is required')
    expected_selection_tail = "\n".join([
        '',
        'if [ -z "$native_a_g_python" ]; then',
        '  native_a_g_python="$("${py_cmd[@]}" -c \'import pathlib, sys; print(pathlib.Path(sys.executable).as_posix())\')"',
        'fi', guard, '',
    ])
    if not selection[1].startswith(expected_selection_tail):
        raise ValueError('release interpreter guard must follow its selection unconditionally')


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument('--repo-root', type=Path, required=True)
    args = parser.parse_args()
    workflow = (args.repo_root / '.github/workflows/validate.yml').read_text(encoding='utf-8')
    verifier = (args.repo_root / 'scripts/verify-package.sh').read_text(encoding='utf-8')
    check(workflow, verifier)
    mutations = [
        workflow.replace('python-version: "3.11"', 'python-version: "3.12"'),
        workflow.replace('          python-version: "3.11"', '          python-version: "3.11"\n        "if": false'),
        workflow.replace('uses: actions/setup-python@v5', 'uses: actions/checkout@v4'),
        workflow.replace('"$release_python" -m pip', 'python3 -m pip'),
        workflow.replace('>> "$GITHUB_ENV"', '> /dev/null'),
        workflow.replace('          python-version: "3.11"', '          python-version: "3.11"\n        if: false'),
        workflow.replace('    runs-on:', '    if: false\n    runs-on:'),
        workflow.replace('run: bash scripts/verify-package.sh', 'run: bash scripts/verify-package.sh || true'),
        workflow + '        continue-on-error: true\n',
        workflow + '        shell: bash {0}\n',
        workflow.replace('          python-version: "3.11"', '          python-version: "3.11"\n        if : false'),
        workflow.replace('          sudo apt-get update', '          exit 0\n          sudo apt-get update'),
        workflow.replace('name: validate', 'name: validate\nx: &skip {if: false}').replace('          python-version: "3.11"', '          python-version: "3.11"\n        <<: *skip'),
    ]
    for value in mutations:
        try:
            check(value, verifier)
        except ValueError:
            continue
        raise AssertionError('CI mismatch mutation escaped the static guard')
    disabled_guard = verifier.replace('"$native_a_g_python" -c', 'if false; then\n"$native_a_g_python" -c', 1).replace(
        '  || fail "native A-G fixture controls require an explicit Python 3.11 executable"',
        '  || fail "native A-G fixture controls require an explicit Python 3.11 executable"\nfi', 1)
    try:
        check(workflow, disabled_guard)
    except ValueError:
        pass
    else:
        raise AssertionError('conditional verifier guard escaped the static guard')
    outer = verifier.replace('native_a_g_python="${PYTHON_BIN:-}"', 'if false; then\nnative_a_g_python="${PYTHON_BIN:-}"', 1).replace('  || fail "native A-G fixture controls require an explicit Python 3.11 executable"', '  || fail "native A-G fixture controls require an explicit Python 3.11 executable"\nfi', 1)
    try:
        check(workflow, outer)
    except ValueError:
        pass
    else:
        raise AssertionError('outer conditional escaped the maintained prefix guard')
    print('CI Python3.11 binding: valid control and 15 negative controls passed')


if __name__ == '__main__':
    main()
