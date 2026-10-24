#!/usr/bin/env python3
"""R0037 TY records through the real run-root owner; no host-Stop claim."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import shlex
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / "skills/implementaudit/scripts/validate-run-root.sh"


def inventory(root):
    return {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob("*") if p.is_file() and not p.is_symlink()}


def write_case(root, changes=None, *, omit=(), suffix="", phase=True, legacy_andon=False):
    shutil.copytree(ROOT / "fixtures/run-root-example", root)
    values = {
        "Run root": str(root), "Phase": "1", "Status": "IN_PHASE",
        "Audit object state": "open", "Owner/source": "issue207/211 governor",
        "Last check": "Focused input validation completed at checkpoint C1",
        "Next action": "Run the remaining evidence-consumption control",
        "Authorization state": "Portable read-only qualification authorized by task grant",
        "Re-entry condition": "Re-read checkpoint C1 and verify current inputs before continuation",
        "Current checkpoint": "C1 input-validation boundary",
        "Last completed step": "Smoke A input validation",
    }
    values.update(changes or {})
    rows = [f"| {key} | {value} |" for key, value in values.items() if key not in omit]
    (root / "STATE.md").write_text(
        "# State\n\n## Current phase\n\n| Field | Value |\n|---|---|\n"
        + "\n".join(rows)
        + "\n\n## Andon log\n\n"
          "| # | Occ | Phase | Class | Abnormality | Countermeasure | Rerun evidence | Outcome |\n"
          "|---|---|---|---|---|---|---|---|\n"
        + suffix, encoding="utf-8")
    if legacy_andon:
        state = root / "STATE.md"
        state.write_text(state.read_text().replace("| # | Occ | Phase | Class |", "| # | Phase | Class |"))
    if not phase:
        shutil.rmtree(root / "phases")
        (root / "ROADMAP.md").write_text("# Roadmap\nIntake decision remains open.\n")
    return root


def consumed_read_set_controls(parent, *, selected=None):
    """Changing an actually consumed dependency must revoke the yield result."""
    controls = []
    for name in ('PROTOCOL.md', 'THINKING.md', 'sidecars.md', 'tools.md', 'context.md'):
        controls.append((name, False, name, '', None))
    controls.extend([
        ('new-claim', False, '.claimed', 'mode=invalid\n', None),
        ('noncurrent-phase', False, 'phases/phase-2.md', '# Phase 99\n', 'phase'),
        ('done-phase-capture', False, 'evidence/completed.log', '', 'capture'),
        ('large-done-capture', False, 'evidence/completed.log', '', 'large-capture'),
        ('binary-done-capture', False, 'evidence/completed.log', '', 'binary-capture'),
        ('new-direct-record', False, 'late-steer.md', 'successor-review: invalid\n', None),
        ('unread-log', True, 'evidence/live-output.log', 'independent output changed\n', 'unread'),
        ('legacy-sibling', False, '../sibling/STATE.md', 'No sibling disposition remains.\n', 'sibling'),
        ('respec-replacement', False, 'evidence/replacement.txt', 'required marker removed\n', 'respec'),
        ('respec-trailing-yes', False, 'evidence/replacement.txt', 'required marker removed\n', 'respec-trailing-yes'),
        ('respec-trailing-path', False, 'evidence/replacement.txt', 'required marker removed\n', 'respec-trailing-path'),
    ])
    if selected is not None:
        assert selected <= {control[0] for control in controls}, 'unknown consumed-input selector'
        controls = [control for control in controls if control[0] in selected]
    for index, (name, want, target, replacement, setup) in enumerate(controls):
        respec = setup in {'respec', 'respec-trailing-yes', 'respec-trailing-path'}
        family = parent / ('consumed-' + str(index)); family.mkdir()
        root = write_case(family / 'root')
        if respec or setup in {'capture', 'large-capture', 'binary-capture', 'unread'}:
            (root / 'evidence').mkdir()
        if setup in {'phase', 'capture', 'large-capture', 'binary-capture'}:
            phase = (root / 'phases/phase-1.md').read_text().replace('Phase 1', 'Phase 2').replace('Phase: 1', 'Phase: 2')
            if setup in {'capture', 'large-capture', 'binary-capture'}:
                phase = phase.replace('Status recorded here.', 'Status: done').replace(
                    '## Mandatory commands\n', '## Mandatory commands\n- `true`; capture: evidence/completed.log; expected: exit 0\n')
                (root / 'evidence/completed.log').write_bytes(
                    b'x' * 1_000_017 if setup == 'large-capture' else b'\xffverified output\n' if setup == 'binary-capture' else b'verified completed output\n')
            (root / 'phases/phase-2.md').write_text(phase)
        if setup == 'unread':
            (root / target).write_text('independent output initial\n')
        if setup == 'sibling':
            (root / '.claimed').write_text('mode=full\ntemplates=STATE.md PROTOCOL.md ROADMAP.md THINKING.md sidecars.md tools.md context.md\n')
            sibling = family / 'sibling'; sibling.mkdir()
            (sibling / 'STATE.md').write_text('PARALLEL: independent accepted lane\n')
        if respec:
            (root / target).write_text('retained-marker\n')
            (root / 'respec-impact-set.md').write_text(
                'IMPLEMENTAUDIT_RESPEC_IMPACT_SET\nChange: bounded correction\nDeclared by: owner-17\n'
                'Population size: 1\nLiteral count: 1\nStem/dirname additional count: 0\n'
                'Enumeration method: literal + stem/dirname\nLiteral carriers: old-record\n'
                'Stem/dirname additional carriers: none\nReplacement: yes\nReplacement path: evidence/replacement.txt\n'
                '| # | Carrier | Kind | Status | Evidence |\n|---|---|---|---|---|\n'
                '| 1 | old-record | source | applied | deciding check-17 |\n'
                '## Invariants carried forward\n'
                '| # | Invariant | Enforced by | Present in replacement? | Evidence |\n|---|---|---|---|---|\n'
                '| 1 | retained marker | existing checker | yes | contains:retained-marker |\n')
        if setup in {'respec-trailing-yes', 'respec-trailing-path'}:
            impact = root / 'respec-impact-set.md'
            field = 'Replacement: yes' if setup == 'respec-trailing-yes' else 'Replacement path: evidence/replacement.txt'
            impact.write_text(impact.read_text().replace(field + '\n', field + '   \n'))
        command = ['bash', str(HELPER), '--nonterminal-yield', str(root)]
        baseline = subprocess.run(command, text=True, capture_output=True)
        assert baseline.returncode == 0, name + ': baseline failed: ' + baseline.stdout + baseline.stderr
        schedule = family / 'schedule.bash'; trigger = family / 'trigger'
        mutation = 'from pathlib import Path; Path(' + repr(str(root / target)) + ').write_text(' + repr(replacement) + ')'
        schedule.write_text('python() {\n'
            '  if [ "$#" -eq 4 ] && [ "$1" = -B ] && [ "$2" = - ] && [ "$3" = ' + shlex.quote(str(root / 'STATE.md')) + ' ]; then\n'
            '    command python -B -c ' + shlex.quote(mutation) + '\n'
            '    printf triggered > ' + shlex.quote(str(trigger)) + '\n'
            '  fi\n  command python "$@"\n}\nexport -f python\n')
        if respec:
            schedule.write_text('python() {\n'
                '  if [ "$#" -eq 2 ] && [ "$1" = - ] && [ "$2" = ' + shlex.quote(str(root / 'respec-impact-set.md')) + ' ]; then\n'
                '    command python "$@"; result=$?\n'
                '    command python -B -c ' + shlex.quote(mutation) + '\n'
                '    printf triggered > ' + shlex.quote(str(trigger)) + '\n'
                '    return "$result"\n'
                '  fi\n  command python "$@"\n}\nexport -f python\n')
        result = subprocess.run(command, text=True, capture_output=True,
            env=os.environ | {'BASH_ENV': str(schedule), 'PYTHONDONTWRITEBYTECODE': '1'})
        assert trigger.exists(), name + ': scheduled actual read boundary was not reached'
        assert (result.returncode == 0) == want, name + ': expected ' + str(want) + '\n' + result.stdout + result.stderr
        if not want:
            assert 'yield read-set' in result.stderr, name + ': wrong refusal: ' + result.stderr
        print('PASS consumed-read-set-' + name)
    return len(controls)


def dependency_profile_controls(parent):
    # Boundaries are portable input limits, never a native-host capability claim.
    root = write_case(parent / 'successor-profile')
    (root / 'current-review.md').write_text('successor-review: pending original owner validation\n')
    result = subprocess.run(['bash', str(HELPER), '--nonterminal-yield', str(root)], text=True, capture_output=True)
    assert result.returncode == 1 and 'live successor/non-verdict contract failed' in result.stderr, result.stdout + result.stderr
    print('PASS malformed-repository-review-record-refused')
    root = write_case(parent / 'direct-record-alias')
    target = parent / 'aliased-record.md'; target.write_text('Current ordinary record.\n')
    (root / 'live-review.md').symlink_to(target)
    result = subprocess.run(['bash', str(HELPER), '--nonterminal-yield', str(root)], text=True, capture_output=True)
    assert result.returncode != 0 and 'aliased yield read-set' in result.stderr, result.stdout + result.stderr
    print('PASS direct-scanned-record-alias-refused')
    return 2




def successor_review_controls(parent, *, selected=None):
    """A repository review may yield only through its unchanged semantic owner."""
    checker = ROOT / 'scripts/check-cold-review-contract.sh'
    def fixture(name):
        root = write_case(parent/('review-' + name), {
            'Status': 'INTERRUPTED', 'Stop source': 'owner-event-17',
            'Interruption point': 'Smoke A input validation', 'Interruption log': '1',
            'Next action': 'Wait for owner-event-17 continuation authorization'}, suffix=
            '| 1 | o1 | 1 | transport-infrastructure | owner-event-17 at Smoke A input validation | Hold affected review | checkpoint C1 | open (rerun pending) |\n')
        inputs = root/'review-inputs'; inputs.mkdir()
        prior = inputs/'predecessor.md'; current = inputs/'successor.md'
        prior.write_text('review-packet-scope: scope: alpha,beta | technique: bounded-read | evidence_mode: inline\n')
        current.write_text('review-packet-scope: scope: alpha | technique: bounded-read | evidence_mode: reference\n')
        (inputs/'findings.md').write_text('# finding-a\n\nfinding-record: id: finding-a | status: provisional\n\nOne concrete input remains to be checked.\n')
        digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
        record = root/'review-record.md'
        record.write_text(
            'lane-status: status: REVIEWER_RUNTIME_NON_VERDICT | predecessor_failure_origin: transport-infrastructure | failure_determinism: content-deterministic | origin_detail: receiver-interruption | predecessor_occurrence: o1 | provisional_findings: review-inputs/findings.md#finding-a | substantive_verdict_consumed: no\n'
            'successor-review: attempt: 1 | predecessor_failure_origin: transport-infrastructure | failure_determinism: content-deterministic | origin_detail: receiver-interruption | predecessor_occurrence: o1 | predecessor_packet_scope_file: review-inputs/predecessor.md | predecessor_packet_scope_sha256: ' + digest(prior) +
            ' | packet_scope_file: review-inputs/successor.md | packet_scope_sha256: ' + digest(current) +
            ' | packet_alteration: scope-narrowed+evidence-by-reference | andon_class: transport-infrastructure | provisional_findings_carried: review-inputs/findings.md#finding-a\n')
        return root, record, prior, current

    def run(root, mode='direct', environment=None):
        arguments = {'owner': ['bash', str(checker), '--run-root'], 'structural': ['bash', str(HELPER)],
                     'direct': ['bash', str(HELPER), '--nonterminal-yield'],
                     'composed': ['bash', str(HELPER), '--turn-disposition', 'NONTERMINAL_YIELD']}[mode]
        command = arguments + [str(root)]
        process = subprocess.Popen(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            start_new_session=True, env=os.environ | {'PYTHONDONTWRITEBYTECODE': '1'} | (environment or {}))
        try: stdout, stderr = process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL); process.communicate()
            raise AssertionError(root.name + ': review consumer blocked')
        return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)

    def accepted(result, name, code=0, reason=''):
        assert result.returncode == code and reason in result.stderr, name + ': ' + result.stdout + result.stderr
    def wanted(name): return selected is None or name in selected
    count = 0
    stable = [
        ('interrupted-resumed', 0, ''), ('transient-unchanged', 0, ''), ('fenced-example', 0, ''),
        ('bad-digest', 1, 'packet_scope_sha256 does not match'),
        ('dropped-finding', 1, 'replacement packet did not carry'),
        ('unaltered-deterministic', 1, 'materially unaltered packet'),
        ('foreign-occurrence', 1, 'predecessor_occurrence must resolve'),
        ('invalid-finding', 1, 'exact finding-record'),
    ]
    for name, code, reason in stable:
        if not wanted(name): continue
        root, record, prior, current = fixture(name)
        if name == 'bad-digest':
            record.write_text(record.read_text().replace(hashlib.sha256(current.read_bytes()).hexdigest(), '0'*64))
        elif name == 'dropped-finding':
            record.write_text(record.read_text().replace('provisional_findings_carried: review-inputs/findings.md#finding-a', 'provisional_findings_carried: none'))
        elif name in {'transient-unchanged', 'unaltered-deterministic'}:
            previous = hashlib.sha256(current.read_bytes()).hexdigest(); current.write_bytes(prior.read_bytes())
            record.write_text(record.read_text().replace(previous, hashlib.sha256(current.read_bytes()).hexdigest()).replace('packet_alteration: scope-narrowed+evidence-by-reference', 'packet_alteration: none'))
            if name == 'transient-unchanged': record.write_text(record.read_text().replace('content-deterministic', 'transient'))
        elif name == 'foreign-occurrence':
            record.write_text(record.read_text().replace('predecessor_occurrence: o1', 'predecessor_occurrence: o2'))
        elif name == 'invalid-finding':
            path = root/'review-inputs/findings.md'; path.write_text(path.read_text().replace('status: provisional', 'status: resolved'))
        elif name == 'fenced-example':
            (root/'example.md').write_text('```text\nsuccessor-review: packet_scope_file: absent-example.md\n```\n')
        before = inventory(root)
        for mode in ('owner', 'structural', 'direct', 'composed'):
            accepted(run(root, mode), name + ' ' + mode, code, reason)
        assert inventory(root) == before, name + ': reader changed source inputs'
        if name == 'interrupted-resumed':
            state = root/'STATE.md'
            state.write_text(state.read_text().replace('| Status | INTERRUPTED |', '| Status | IN_PHASE |').replace(
                'Wait for owner-event-17 continuation authorization', 'Validate the carried provisional finding before redispatch'))
            before = inventory(root)
            for mode in ('owner', 'structural', 'direct', 'composed'): accepted(run(root, mode), name + ' resumed ' + mode)
            assert inventory(root) == before, name + ': resumed reader changed source inputs'
        count += 1; print('PASS successor-review-' + name)

    drift = [
        ('prior-packet-drift', 'review-inputs/predecessor.md', 'altered prior packet\n', 1),
        ('current-packet-drift', 'review-inputs/successor.md', 'altered current packet\n', 1),
        ('finding-drift', 'review-inputs/findings.md', 'finding no longer provisional\n', 1),
        ('direct-record-created', 'new-review.md', 'successor-review: invalid\n', 1),
        ('unread-log-drift', 'logs/live.log', 'independent output changed\n', 0),
    ]
    for name, target, replacement, code in drift:
        if not wanted(name): continue
        root, _, _, _ = fixture(name)
        if name == 'unread-log-drift':
            (root/'logs').mkdir(); (root/target).write_text('independent output\n')
        accepted(run(root), name + ' baseline')
        trigger = parent/(name + '-trigger'); schedule = parent/(name + '-schedule.bash')
        mutation = 'from pathlib import Path;Path(' + repr(str(root/target)) + ').write_text(' + repr(replacement) + ')'
        schedule.write_text('bash() {\n  case "$1" in */check-cold-review-contract.sh)\n'
            '    command bash "$@"; result=$?\n    command python -B -c ' + shlex.quote(mutation) + '\n'
            '    printf triggered > ' + shlex.quote(str(trigger)) + '\n    return "$result";;\n  esac\n  command bash "$@"\n}\nexport -f bash\n')
        result = run(root, environment={'BASH_ENV': str(schedule)})
        assert trigger.exists(), name + ': actual semantic checker did not return'
        accepted(result, name, code, 'yield read-set' if code else '')
        count += 1; print('PASS successor-review-' + name)

    for name, shape in (('packet-symlink', 'symlink'), ('packet-hardlink', 'hardlink'), ('finding-fifo', 'fifo')):
        if not wanted(name): continue
        if shape == 'fifo' and not hasattr(os, 'mkfifo'): continue
        root, _, _, current = fixture(name)
        target = root/'review-inputs/findings.md' if shape == 'fifo' else current
        retained = target.with_suffix('.retained'); target.rename(retained)
        if shape == 'symlink': target.symlink_to(retained)
        elif shape == 'hardlink': os.link(retained, target)
        else: os.mkfifo(target)
        accepted(run(root), name, 1, 'yield read-set')
        count += 1; print('PASS successor-review-' + name)

    # The private records are a distinct consumed surface. Exercise both the
    # original-to-copy binding and the final currentness check through the owner.
    snapshots = [
        ('private-finding-substitution-direct', 'direct', 'before',
         'p=s/"review-inputs/findings.md";p.write_text(p.read_text().replace("status: resolved","status: provisional"))', 1),
        ('private-finding-substitution-composed', 'composed', 'before',
         'p=s/"review-inputs/findings.md";p.write_text(p.read_text().replace("status: resolved","status: provisional"))', 1),
        ('private-redirected-dependency', 'direct', 'before',
         'p=s/"review-inputs/findings.md";(s/"review-inputs/redirected.md").write_bytes(p.read_bytes());p.unlink();p=s/"review-record.md";p.write_text(p.read_text().replace("review-inputs/findings.md#finding-a","review-inputs/redirected.md#finding-a"))', 1),
        ('private-direct-created', 'direct', 'after',
         '(s/"later.md").write_text("# Later direct record"+chr(10))', 1),
        ('private-state-missing', 'composed', 'after', '(s/"STATE.md").unlink()', 1),
        ('private-finding-replaced', 'composed', 'after',
         'p=s/"review-inputs/findings.md";q=p.with_name("replacement.pending");q.write_bytes(p.read_bytes());q.replace(p)', 1),
        ('private-finding-changed', 'direct', 'after',
         'p=s/"review-inputs/findings.md";p.write_text(p.read_text()+chr(10)+"# Changed private finding"+chr(10))', 1),
        ('private-finding-fifo', 'direct', 'after',
         'p=s/"review-inputs/findings.md";p.unlink();os.mkfifo(p)', 1),
        ('private-unread-log', 'direct', 'after',
         '(s/"logs").mkdir();(s/"logs/live.log").write_text("unread private output"+chr(10))', 0),
    ]
    for name, mode, boundary, mutation, code in snapshots:
        if not wanted(name): continue
        if name == 'private-finding-fifo' and not hasattr(os, 'mkfifo'): continue
        root, _, _, _ = fixture(name)
        if name.startswith('private-finding-substitution'):
            path = root/'review-inputs/findings.md'; path.write_text(path.read_text().replace('status: provisional', 'status: resolved'))
        before = inventory(root)
        trigger = parent/(name + '-trigger'); schedule = parent/(name + '-schedule.bash')
        source = 'from pathlib import Path;import os,sys;s=Path(sys.argv[1]).parent/"records";' + mutation
        mutate = '    command python -B -c ' + shlex.quote(source) + ' "$1" || return $?\n'
        schedule.write_text('bash() {\n  case "$1" in "${TMPDIR}/"*/check-cold-review-contract.sh)\n' +
            (mutate if boundary == 'before' else '') + '    command bash "$@"; result=$?\n' +
            (mutate if boundary == 'after' else '') + '    printf "%s\\n" "$result" > ' + shlex.quote(str(trigger)) +
            '\n    return "$result";;\n  esac\n  command bash "$@"\n}\nexport -f bash\n')
        result = run(root, mode, {'BASH_ENV': str(schedule)})
        assert trigger.exists() and trigger.read_text().strip() == '0', name + ': actual semantic checker did not accept its consumed snapshot'
        accepted(result, name, code, 'yield read-set' if code else '')
        assert inventory(root) == before, name + ': private mutation changed original inputs'
        count += 1; print('PASS successor-review-' + name)

    name = 'private-finding-before-binding'
    if wanted(name):
        root, _, _, _ = fixture(name)
        finding = root/'review-inputs/findings.md'
        finding.write_text(finding.read_text().replace('status: provisional', 'status: resolved'))
        before = inventory(root)
        wrapper = parent/(name + '-python'); wrapper.mkdir()
        trigger = parent/(name + '-trigger'); owner_trigger = parent/(name + '-owner-trigger')
        python = wrapper/'python'
        python.write_text('\n'.join([
            '#!' + sys.executable, 'from pathlib import Path', 'import os,sys',
            'args=[a for a in sys.argv[1:] if a != "-B"]',
            'if "--successor-review" in args:',
            '    source=sys.stdin.read();prior_lstat=Path.lstat;trigger=Path(' + repr(str(trigger)) + ')',
            '    def scheduled_lstat(path,*rest,**kw):',
            '        p=Path(path)',
            '        if p.parts[-3:]==("records","review-inputs","findings.md") and str(p).startswith(os.environ["TMPDIR"]+os.sep) and not trigger.exists():',
            '            assert "status: resolved" in p.read_text()',
            '            p.write_text(p.read_text().replace("status: resolved","status: provisional"))',
            '            trigger.write_text("substituted before first private read")',
            '        return prior_lstat(p,*rest,**kw)',
            '    Path.lstat=scheduled_lstat;sys.argv=args',
            '    exec(compile(source,"<unchanged-private-capture>","exec"),{"__name__":"__main__"})',
            'else:', '    os.execv(sys.executable,[sys.executable]+sys.argv[1:])', '']))
        python.chmod(0o700)
        schedule = parent/(name + '-schedule.bash')
        schedule.write_text('bash() {\n  case "$1" in "${TMPDIR}/"*/check-cold-review-contract.sh)\n'
            '    printf reached > ' + shlex.quote(str(owner_trigger)) + ';;\n  esac\n  command bash "$@"\n}\nexport -f bash\n')
        result = run(root, environment={'PATH': str(wrapper) + os.pathsep + os.environ['PATH'], 'BASH_ENV': str(schedule)})
        assert trigger.exists(), name + ': first private-file read was not reached'
        assert not owner_trigger.exists(), name + ': substituted input reached the semantic owner'
        accepted(result, name, 1, 'successor snapshot bytes differ from source capture')
        assert inventory(root) == before, name + ': original inputs changed'
        count += 1; print('PASS successor-review-' + name)

    # Reject unqualified private owner bytes before Bash can execute them.
    for name, mode, mutation in (
        ('unqualified-owner-before-execution', 'direct', 'p.write_text("#!/usr/bin/env bash\\nprintf UNQUALIFIED_CODE_EXECUTED >&2\\n")'),
        ('missing-owner-before-execution', 'composed', 'p.unlink()'),
    ):
        if not wanted(name): continue
        root, _, _, _ = fixture(name)
        trigger = parent/(name + '-trigger'); schedule = parent/(name + '-schedule.bash')
        source = 'from pathlib import Path;import sys;p=Path(sys.argv[1]);' + mutation
        schedule.write_text('python() {\n  if [ "$#" -eq 7 ] && [ "$6" = --successor-owner ] && [ ! -f ' + shlex.quote(str(trigger)) + ' ]; then\n'
            '    case "$7" in "${TMPDIR}/"*/check-cold-review-contract.sh)\n'
            '      command python -B -c ' + shlex.quote(source) + ' "$7"\n'
            '      printf triggered > ' + shlex.quote(str(trigger)) + ';;\n    esac\n  fi\n  command python "$@"\n}\nexport -f python\n')
        result = run(root, mode, {'BASH_ENV': str(schedule)})
        assert trigger.exists(), name + ': private owner qualification boundary was not reached'
        accepted(result, name, 3, 'OUT_OF_PROFILE')
        assert 'UNQUALIFIED_CODE_EXECUTED' not in result.stdout + result.stderr, name + ': unqualified code executed'
        count += 1; print('PASS successor-review-' + name)

    # Mutate only private executed-owner copies, never the repository checker.
    # The semantic checker first returns a genuine result; changed/missing code
    # at the final boundary must revoke the qualified profile in both routes.
    for name, mode, mutation in (('executed-owner-changed', 'direct', 'p.write_text(p.read_text()+"\\n# changed after execution\\n")'),
                                 ('executed-owner-missing', 'composed', 'p.unlink()')):
        if not wanted(name): continue
        root, _, _, _ = fixture(name)
        trigger = parent/(name + '-trigger'); schedule = parent/(name + '-schedule.bash')
        source = 'from pathlib import Path;import sys;p=Path(sys.argv[1]);' + mutation
        schedule.write_text('bash() {\n  case "$1" in "${TMPDIR}/"*/check-cold-review-contract.sh)\n'
            '    command bash "$@"; result=$?\n    command python -B -c ' + shlex.quote(source) + ' "$1"\n'
            '    printf triggered > ' + shlex.quote(str(trigger)) + '\n    return "$result";;\n  esac\n  command bash "$@"\n}\nexport -f bash\n')
        result = run(root, mode, {'BASH_ENV': str(schedule)})
        assert trigger.exists(), name + ': qualified private owner was not consumed'
        accepted(result, name, 3, 'OUT_OF_PROFILE')
        count += 1; print('PASS successor-review-' + name)
    if selected is not None: assert count == len(selected), 'unknown or unavailable successor-review selector'
    return count


def background_read_set_controls(parent, *, selected=None):
    """Actual background consumers select bytes; ignored logs cannot revoke yield."""
    def fixture(name, kind):
        root = write_case(parent / ('background-' + name))
        chain = root / 'background/chain-17'
        if kind == 'absent':
            return root, chain
        chain.mkdir(parents=True)
        intent = 'command: legacy-owned-job\n'
        if kind in {'no-status', 'modern', 'owned'}:
            intent += ('poll_budget: 3\nterminal_signal: chain.done\n'
                       'expected_duration: 90m\ntransport_timeout: 10m\nlaunch_mode: detached\n')
        if kind == 'closed':
            intent += ('verification_window:\n  - surfaces: [bounded-input]\n'
                       '    closed_at: 0123456789abcdef0123456789abcdef01234567\n    state: closed\n')
            (chain / 'chain.done').touch()
        (chain / 'launch-intent.md').write_text(intent)
        (chain / 'logs').mkdir()
        (chain / 'logs/output.log').write_text('task-owned output\n')
        if kind in {'modern', 'owned'}:
            (chain / 'chain-status.txt').write_text('checkpoint: C1\nwait: blocking | signal=chain.done\n')
        if kind == 'owned':
            (chain / 'chain-status.txt').write_text(
                'kill: pid=123 | host_boot_id=boot-1 | process_creation_time=2026-08-06T01:02:03Z\n')
            (chain / 'process-started.json').write_text(json.dumps({
                'lane_id': 'chain-17', 'host_os': 'windows', 'host_boot_id': 'boot-1',
                'pid': 123, 'process_creation_time': '2026-08-06T01:02:03Z'}))
        return root, chain

    def run(root, arguments=('--nonterminal-yield',), environment=None):
        command = ['bash', str(HELPER), *arguments, str(root)]
        process = subprocess.Popen(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            start_new_session=True, env=os.environ | {'PYTHONDONTWRITEBYTECODE': '1'} | (environment or {}))
        try:
            stdout, stderr = process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.communicate()
            raise AssertionError(root.name + ': background read blocked instead of returning a disposition')
        return subprocess.CompletedProcess(command, process.returncode, stdout, stderr)

    count = 0
    def wanted(name):
        return selected is None or name in selected
    def accepted(result, name, code=0, reason=''):
        assert result.returncode == code and reason in result.stderr, name + ': ' + result.stdout + result.stderr

    # Admission must preserve the original structural owner, including its
    # closed-window, broad-kill and process-identity negatives.
    stable = [
        ('legacy', 'legacy', '', 0, ''),
        ('closed', 'closed', '', 0, ''),
        ('no-status', 'no-status', '', 0, ''),
        ('modern', 'modern', '', 0, ''),
        ('owned-kill', 'owned', '', 0, ''),
        ('missing-completion', 'closed', "(chain/'chain.done').unlink()", 1, 'closed verification window lacks chain.done'),
        ('nested-broad-kill', 'modern', "(chain/'logs/output.log').write_text('pkill -f unsafe-name\\n')", 1, 'broad kill authority'),
        ('foreign-process', 'owned', "(chain/'process-started.json').write_text('{}')", 1, 'kill identity not ledger-owned'),
        ('owned-process-selector', 'modern', "(chain/'logs/output.log').write_text('Get-Process -Id 123\\n')", 0, ''),
        ('snapshot-prefix-command', 'modern', "(chain/'logs/output.log').write_text('Get-Process unsafe-name\\n')", 1, 'broad Get-Process'),
        ('large-binary-log', 'modern', "(chain/'logs/output.log').write_bytes(b'\\xff' + b'x'*1_000_017)", 0, ''),
    ]
    for name, kind, setup, code, reason in stable:
        if not wanted(name): continue
        root, chain = fixture(name, kind)
        exec(setup)
        environment = {}
        if name == 'snapshot-prefix-command':
            temporary = parent / 'Get-Process -Id 123'; temporary.mkdir()
            environment['TMPDIR'] = str(temporary)
        before = inventory(root)
        accepted(run(root, (), environment), name + ' structural', code, reason)
        accepted(run(root, environment=environment), name, code, reason)
        if name in {'legacy', 'modern'}:
            accepted(run(root, ('--turn-disposition', 'NONTERMINAL_YIELD')), name + ' composed')
        assert inventory(root) == before, name + ': background validator mutated its inputs'
        count += 1; print('PASS background-' + name)

    # Distinct source names can share the original owner's display ID because
    # command substitution strips trailing newlines. Copies must remain private
    # to each source chain; completion/status presence cannot cross between them.
    for name, kind, second_name, code in (
        ('multi-chain-complete', 'closed', 'lane-a\n', 0),
        ('distinct-chain-missing-completion', 'closed', 'lane-b', 1),
        ('colliding-name-missing-completion', 'closed', 'lane-a\n', 1),
        ('colliding-name-no-status', 'modern', 'lane-a\n', 0),
    ):
        if not wanted(name): continue
        root, chain = fixture(name, kind)
        first = chain.with_name('lane-a'); chain.rename(first)
        second = first.with_name(second_name); shutil.copytree(first, second)
        if name == 'multi-chain-complete':
            shutil.copytree(first, first.with_name('lane-a\n\n'))
        elif kind == 'closed':
            (second/'chain.done').unlink()
        else:
            (second/'chain-status.txt').unlink()
            (second/'logs/output.log').write_text('pkill -f intentionally-unread\n')
        before = inventory(root)
        results = [run(root, arguments) for arguments in
                   ((), ('--nonterminal-yield',), ('--turn-disposition', 'NONTERMINAL_YIELD'))]
        observed = [{'code': r.returncode, 'stdout': r.stdout, 'stderr': r.stderr} for r in results]
        assert [r.returncode for r in results] == [code]*3, name + ': ' + json.dumps(observed)
        if code:
            assert all('closed verification window lacks chain.done' in r.stderr for r in results), observed
        assert inventory(root) == before, name + ': validator mutated a source chain'
        count += 1; print('PASS background-' + name)

    # Schedule changes after the actual background function has returned, at
    # the existing late predicate boundary. Every relevant byte/presence/name
    # change must revoke admission; irrelevant output changes must not.
    drift = [
        ('intent-drift', 'legacy', "(chain/'launch-intent.md').write_text('command: changed-job\\n')", 1),
        ('completion-removed', 'closed', "(chain/'chain.done').unlink()", 1),
        ('completion-bytes-unread', 'closed', "(chain/'chain.done').write_text('presence-only change\\n')", 0),
        ('status-created', 'no-status', "(chain/'chain-status.txt').write_text('running\\n')", 1),
        ('status-drift', 'modern', "(chain/'chain-status.txt').write_text('probe: 1\\n')", 1),
        ('nested-bytes-drift', 'modern', "(chain/'logs/output.log').write_text('changed output\\n')", 1),
        ('nested-member-created', 'modern', "(chain/'logs/late.log').write_text('late output\\n')", 1),
        ('process-identity-drift', 'owned', "(chain/'process-started.json').write_text('{}')", 1),
        ('legacy-log-unread', 'legacy', "(chain/'logs/output.log').write_text('pkill -f ignored-log\\n')", 0),
        ('no-status-log-unread', 'no-status', "(chain/'logs/output.log').write_text('pkill -f ignored-log\\n')", 0),
        ('chain-created', 'legacy', "p=root/'background/chain-18';p.mkdir();(p/'launch-intent.md').write_text('command: new-job\\n')", 1),
        ('chain-removed', 'legacy', "chain.rename(root/'background/.retired-chain')", 1),
        ('background-created', 'absent', "(root/'background').mkdir()", 1),
    ]
    for name, kind, mutation, code in drift:
        if not wanted(name): continue
        root, chain = fixture(name, kind)
        accepted(run(root), name + ' baseline')
        trigger = parent / (name + '-trigger')
        schedule = parent / (name + '-schedule.bash')
        source = 'from pathlib import Path;root=Path(' + repr(str(root)) + ');chain=Path(' + repr(str(chain)) + ');' + mutation
        schedule.write_text('python() {\n'
            '  if [ "$#" -eq 4 ] && [ "$1" = -B ] && [ "$2" = - ] && [ "$3" = ' + shlex.quote(str(root/'STATE.md')) + ' ]; then\n'
            '    command python -B -c ' + shlex.quote(source) + '\n'
            '    printf triggered > ' + shlex.quote(str(trigger)) + '\n'
            '  fi\n  command python "$@"\n}\nexport -f python\n')
        result = run(root, environment={'BASH_ENV': str(schedule)})
        assert trigger.exists(), name + ': real post-consumption boundary was not reached'
        accepted(result, name, code, 'yield read-set' if code else '')
        count += 1; print('PASS background-' + name)

    unsafe = [
        ('intent-symlink', 'legacy', 'launch-intent.md', 'symlink'),
        ('intent-hardlink', 'legacy', 'launch-intent.md', 'hardlink'),
        ('completion-symlink', 'closed', 'chain.done', 'symlink'),
        ('completion-hardlink', 'closed', 'chain.done', 'hardlink'),
        ('nested-symlink', 'modern', 'logs/output.log', 'symlink'),
        ('chain-symlink', 'modern', '.', 'symlink'),
    ]
    if hasattr(os, 'mkfifo'):
        unsafe += [('status-fifo', 'modern', 'chain-status.txt', 'fifo'),
                   ('nested-fifo', 'modern', 'logs/output.log', 'fifo')]
    for name, kind, raw, shape in unsafe:
        if not wanted(name): continue
        root, chain = fixture(name, kind)
        target = chain / raw
        retained = parent / (name + '-original')
        target.rename(retained)
        if shape == 'symlink': target.symlink_to(retained, target_is_directory=retained.is_dir())
        elif shape == 'hardlink': os.link(retained, target)
        else: os.mkfifo(target)
        result = run(root)
        accepted(result, name, 1, 'yield read-set')
        count += 1; print('PASS background-' + name)

    if hasattr(os, 'mkfifo'):
        for kind in ('legacy', 'no-status'):
            name = kind + '-fifo-unread'
            if not wanted(name): continue
            root, chain = fixture(name, kind)
            (chain/'logs/output.log').unlink(); os.mkfifo(chain/'logs/output.log')
            accepted(run(root), name)
            count += 1; print('PASS background-' + name)
        # Replace original source with a FIFO precisely before real grep would
        # consume it. The safely captured bytes may be read; final recheck must
        # refuse the changed source without entering the FIFO.
        for name, kind, target, condition in (
            ('intent-consumer-fifo', 'legacy', 'launch-intent.md', '[[ "${@: -1}" = */launch-intent.md ]]'),
            ('recursive-consumer-fifo', 'modern', 'logs/output.log', '[ "${1:-}" = -R ]'),
        ):
            if not wanted(name): continue
            root, chain = fixture(name, kind)
            trigger = parent / (name + '-trigger')
            schedule = parent / (name + '-schedule.bash')
            mutation = ('from pathlib import Path;import os;p=Path(' + repr(str(chain/target)) +
                        ');p.rename(p.with_name(p.name+".original"));os.mkfifo(p)')
            schedule.write_text('grep() {\n  if ' + condition + ' && [ ! -f ' + shlex.quote(str(trigger)) + ' ]; then\n'
                '    command python -B -c ' + shlex.quote(mutation) + '\n'
                '    printf triggered > ' + shlex.quote(str(trigger)) + '\n'
                '  fi\n  command grep "$@"\n}\nexport -f grep\n')
            result = run(root, environment={'BASH_ENV': str(schedule)})
            assert trigger.exists(), name + ': real grep boundary was not reached'
            accepted(result, name, 1, 'yield read-set')
            count += 1; print('PASS background-' + name)
    if selected is not None:
        assert count == len(selected), 'unknown or unavailable background selector'
    return count


def main():
    cases = []
    # A valid current progress record must pass; missing mode is an explicit
    # feature-gap assertion on the old owner, never an accidental import error.
    cases.append(("TY5-progress", True, {}, {}, ""))
    pause = {"Status": "PAUSED", "Pause reason": "Clarification of target dataset is required",
             "Resume point": "Input selection before processing",
             "Pause trigger": "clarification", "Next action": "Ask the owner which dataset is intended"}
    cases.append(("TY1-required-clarification", True, pause, {}, ""))
    cases.append(("TY2-owner-authority-wait", True, pause | {
        "Pause trigger": "owner-authority", "Pause reason": "Publication authority is absent",
        "Authorization state": "Publication not authorized; no effect performed",
        "Next action": "Request the exact publication grant from the owner"}, {}, ""))
    blocked = {"Status": "BLOCKED", "Blocker": "external-job-27 has no terminal output",
               "Containment": "No dependent effect or completion claim is admitted",
               "Next probe": "Read external-job-27 terminal status after its owner update",
               "Next action": "Inspect external-job-27 after the owner update"}
    cases.append(("TY3-external-dependency", True, blocked, {}, ""))
    cases.append(("suffixed-probe-template", False, blocked | {"Next probe": "Read <path>/external-job-27.json"}, {}, ""))
    pause_record = ("\nIMPLEMENTAUDIT_PAUSE\nPhase: 1\nStatus: paused at boundary\n"
                    "Last completed step: Smoke A input validation\nSTATE.md: updated\n")
    cases.append(("TY4-user-pause", True, pause | {"Pause trigger": "user-interruption", "Pause phase context": "IN_PROGRESS"}, {}, pause_record))
    interruption = {"Status": "INTERRUPTED", "Stop source": "owner-event-17",
                    "Interruption point": "Smoke A input validation", "Interruption log": "1",
                    "Next action": "Wait for owner-event-17 continuation authorization"}
    log = "| 1 | i17 | 1 | input-contract | owner-event-17 at Smoke A input validation | Hold affected work | checkpoint C1 | open (rerun pending) |\n"
    cases.append(("TY4-owner-interruption", True, interruption, {}, log))
    intake = {"Phase": "intake", "Status": "open", "Pending decision": "Which of two input datasets is intended",
              "Last check": "not-yet-run: input dataset identity needs the owner answer",
              "Next action": "Ask the owner to select the input dataset"}
    cases.append(("TY5-open-intake", True, intake, {"phase": False}, ""))
    cases.append(("TY5-ready-dispatch", True, {"Status": "READY_TO_DISPATCH", "Pending decision": "Dispatch the reviewed phase1 verifier"}, {}, ""))
    for field in ("Last check", "Next action", "Owner/source", "Authorization state", "Re-entry condition",
                  "Current checkpoint", "Last completed step", "Audit object state", "Phase"):
        cases.append(("TY6-missing-" + field, False, {}, {"omit": (field,)}, ""))
    for value in ("", "none", "pending", "TODO", "run it", "continue", "wait for it"):
        cases.append(("TY6-vague-next-" + repr(value), False, {"Next action": value}, {}, ""))
    cases.extend([
        ("terminal-object-not-yield", False, {"Audit object state": "terminal verified closure"}, {}, ""),
        ("done-is-not-yield", False, {"Status": "DONE"}, {}, ""),
        ("bare-paused", False, {"Status": "PAUSED"}, {}, ""),
        ("bare-blocked", False, {"Status": "BLOCKED"}, {}, ""),
        ("bare-interrupted", False, {"Status": "INTERRUPTED"}, {}, ""),
        ("open-without-decision", False, {"Status": "open"}, {}, ""),
        ("ready-without-decision", False, {"Status": "READY_TO_DISPATCH"}, {}, ""),
        ("user-pause-record-missing", False, pause | {"Pause trigger": "user-interruption", "Pause phase context": "IN_PROGRESS"}, {}, ""),
        ("user-pause-foreign-phase", False, pause | {"Pause trigger": "user-interruption", "Pause phase context": "IN_PROGRESS"}, {}, pause_record.replace("Phase: 1", "Phase: 2")),
        ("user-pause-state-not-updated", False, pause | {"Pause trigger": "user-interruption", "Pause phase context": "IN_PROGRESS"}, {}, pause_record.replace("STATE.md: updated", "STATE.md: not updated")),
        ("interruption-log-absent", False, interruption, {}, ""),
        ("interruption-log-foreign", False, interruption, {}, log.replace("owner-event-17", "owner-event-18")),
        ("blocker-no-containment", False, blocked, {"omit": ("Containment",)}, ""),
        ("blocker-no-probe", False, blocked, {"omit": ("Next probe",)}, ""),
        ("missing-phase-spec", False, {}, {"phase": False}, ""),
    ])
    # Independent review found these counterexamples after the first 45 passed.
    cases.extend([
        ("interruption-prefix-is-foreign", False, interruption | {"Stop source": "owner-event-1"}, {}, log),
        ("interruption-suffix-is-foreign", False, interruption | {"Stop source": "event-17"}, {}, log),
        ("interruption-phase-is-foreign", False, interruption, {}, log.replace("| i17 | 1 |", "| i17 | 2 |")),
        ("interruption-duplicate-row", False, interruption, {}, log + log),
        ("interruption-legacy-row", True, interruption, {"legacy_andon": True}, log.replace("| 1 | i17 |", "| 1 |")),
        ("concrete-check-action", True, {"Next action": "Check external-job-27 terminal status"}, {}, ""),
        ("concrete-execute-action", True, {"Next action": "Execute tests/run-root-validation.test.sh and inspect its exit status"}, {}, ""),
        ("concrete-unfamiliar-action", True, {"Next action": "Recalculate case-27 checksum from its retained bytes"}, {}, ""),
        ("unresolved-command-template", False, {"Next action": "Run <command>"}, {}, ""),
        ("unresolved-target-template", False, {"Next action": "Check [target]"}, {}, ""),
        ("concrete-indexed-action", True, {"Next action": "Inspect external-job-27 JSON field records[0].id before resuming phase 1"}, {}, ""),
        ("concrete-parametrized-test-action", True, {"Next action": "Run pytest tests/test_config.py::test_load[linux] and inspect its exit status"}, {}, ""),
        ("concrete-braced-shell-action", True, {"Next action": "Inspect the output from printf '%s' {a,b} in case 27"}, {}, ""),
        ("unresolved-braced-command-template", False, {"Next action": "Run {command}"}, {}, ""),
        ("suffixed-command-template", False, {"Next action": "Run <command>.sh"}, {}, ""),
        ("suffixed-target-template", False, {"Next action": "Check [target]/status"}, {}, ""),
        ("embedded-path-template", False, {"Next action": "Read evidence/<path>/status.json"}, {}, ""),
        ("concrete-comparator", True, {"Next action": "Check that sample_count < expected_count for case-27"}, {}, ""),
        ("concrete-keyed-index", True, {"Next action": "Inspect records[path].id for case-27"}, {}, ""),
        ("concrete-shell-variable", True, {"Next action": "Inspect ${path}/case-27.json before resuming"}, {}, ""),
        ("quoted-phase-identity", True, {"Phase": "`1`"}, {}, ""),
        ("pause-conflicting-last-step", False, pause | {"Pause trigger": "user-interruption", "Pause phase context": "IN_PROGRESS"}, {},
         pause_record.replace("Last completed step: Smoke A input validation", "Last completed step: Step 11 phase verification")),
        ("pause-without-redundant-table-step", True, pause | {"Pause trigger": "user-interruption", "Pause phase context": "IN_PROGRESS"},
         {"omit": ("Last completed step",)}, pause_record),
    ])
    outside = pause | {"Pause trigger": "user-interruption", "Pause phase context": "OUTSIDE_PHASE",
                       "Phase": "intake", "Last check": "not-yet-run: owner paused before dispatch",
                       "Pause reason": "Owner paused intake before selecting the target",
                       "Resume point": "Resume input selection after the owner returns"}
    cases.extend([
        ("user-pause-before-intake-dispatch", True, outside,
         {"phase": False, "omit": ("Current checkpoint", "Last completed step")}, ""),
        ("user-pause-planned-numbered-phase", True, outside | {"Phase": "1"},
         {"omit": ("Current checkpoint", "Last completed step")}, ""),
        ("user-pause-outside-phase-rejects-fabricated-marker", False, outside,
         {"phase": False}, pause_record.replace("Phase: 1", "Phase: intake")),
        ("user-pause-context-missing", False, pause | {"Pause trigger": "user-interruption"}, {}, pause_record),
        ("user-pause-context-unknown", False, pause | {"Pause trigger": "user-interruption", "Pause phase context": "UNKNOWN"}, {}, pause_record),
        ("user-pause-active-context-requires-numbered-phase", False, outside | {"Pause phase context": "IN_PROGRESS"},
         {"phase": False}, pause_record.replace("Phase: 1", "Phase: intake")),
    ])
    external = pause | {"Pause trigger": "external-wait", "Pause reason": "external-job-27 terminal output is missing",
                        "Blocker": blocked["Blocker"], "Containment": blocked["Containment"],
                        "Next probe": blocked["Next probe"]}
    cases.append(("external-pause-complete", True, external, {}, ""))
    for missing in ("Blocker", "Containment", "Next probe"):
        cases.append(("external-pause-missing-" + missing, False, external, {"omit": (missing,)}, ""))
    for marker in ("AUDIT_COMPLETE", "IMPLEMENTAUDIT_RUN_COMPLETE", "AUDIT_HANDOFF", "ANDON_HANDOFF"):
        cases.append(("marker-cannot-use-yield-" + marker, False, {}, {}, "\n" + marker + "\n"))
    fifo_count = 0
    dependency_count = 0
    with tempfile.TemporaryDirectory(prefix="r37-yield-") as temporary:
        parent = Path(temporary)
        dependency_count = (consumed_read_set_controls(parent) + dependency_profile_controls(parent)
                            + background_read_set_controls(parent) + successor_review_controls(parent))
        for index, (name, want, changes, kwargs, suffix) in enumerate(cases):
            root = write_case(parent / str(index), changes, suffix=suffix, **kwargs)
            before = inventory(root)
            result = subprocess.run(["bash", str(HELPER), "--nonterminal-yield", str(root)],
                                    text=True, capture_output=True, env=os.environ | {"PYTHONDONTWRITEBYTECODE": "1"})
            if (result.returncode == 0) != want:
                raise AssertionError(f"{name}: expected {'accept' if want else 'refuse'}, exit={result.returncode}\n{result.stdout}{result.stderr}")
            assert inventory(root) == before, f"{name}: read-only validator mutated run artifacts"
            if want:
                assert "nonterminal yield record ok" in result.stdout, f"{name}: generic structural success substituted for yield validation"
            print(f"PASS {name}")
        root = write_case(parent / "duplicate")
        state = root / "STATE.md"
        state.write_text(state.read_text().replace("| Status | IN_PHASE |", "| Status | IN_PHASE |\n| Status | PAUSED |"))
        result = subprocess.run(["bash", str(HELPER), "--nonterminal-yield", str(root)], capture_output=True)
        assert result.returncode != 0, "duplicate current status admitted"
        print("PASS duplicate-current-status")
        root = write_case(parent / "symlink")
        state = root / "STATE.md"
        target = parent / "aliased-state.md"
        state.rename(target)
        state.symlink_to(target)
        result = subprocess.run(["bash", str(HELPER), "--nonterminal-yield", str(root)], capture_output=True)
        assert result.returncode != 0, "symlink STATE admitted"
        print("PASS symlink-state")
        # Schedule a real temporary-record mutation between the two consumer
        # stages. The wrapper selects only the late predicate's argv shape;
        # it grants no authority and is never installed into a user environment.
        race = write_case(parent / "legacy-read-drift")
        wrapper = parent / "bin"
        wrapper.mkdir()
        trigger = parent / "mutation-triggered"
        python = wrapper / "python"
        python.write_text("\n".join([
            "#!" + sys.executable, "from pathlib import Path", "import os,sys",
            "args=[a for a in sys.argv[1:] if a != '-B']",
            "if len(args)==3 and args[0]=='-' and args[1].endswith('/STATE.md'):",
            "    state=Path(args[1])",
            "    state.write_text(state.read_text().replace('## Andon log','## Removed Andon log'))",
            "    Path(" + repr(str(trigger)) + ").write_text('observed')",
            "os.execv(" + repr(sys.executable) + ", [" + repr(sys.executable) + "] + sys.argv[1:])", ""
        ]))
        python.chmod(0o700)
        environment = os.environ | {"PATH": str(wrapper) + os.pathsep + os.environ["PATH"]}
        result = subprocess.run(["bash", str(HELPER), "--nonterminal-yield", str(race)],
                                text=True, capture_output=True, env=environment)
        assert trigger.exists(), "mutation schedule did not reach the late consumer"
        assert result.returncode != 0 and "yield read-set changed" in result.stderr, result.stdout + result.stderr
        print("PASS legacy-structural-yield-read-drift")
        # Both spellings accepted by the actual table consumer must select the
        # same phase member for the before/after read-set comparison.
        phase_wrapper = parent / "phase-bin"
        phase_wrapper.mkdir()
        python = phase_wrapper / "python"
        python.write_text("\n".join([
            "#!" + sys.executable, "from pathlib import Path", "import os,sys,subprocess",
            "args=[a for a in sys.argv[1:] if a != '-B']",
            "if len(args)==3 and args[0]=='-' and args[1].endswith('/STATE.md'):",
            "    result=subprocess.run([sys.executable]+sys.argv[1:])",
            "    phase=Path(args[2])/'phases/phase-1.md'",
            "    phase.write_text(phase.read_text()+'\\nPhase: 99\\n')",
            "    (Path(args[2])/'schedule-triggered').write_text(str(result.returncode))",
            "    raise SystemExit(result.returncode)",
            "os.execv(sys.executable,[sys.executable]+sys.argv[1:])", ""
        ]))
        python.chmod(0o700)
        environment = os.environ | {"PATH": str(phase_wrapper) + os.pathsep + os.environ["PATH"]}
        for label, phase in (("plain", "1"), ("quoted", "`1`")):
            race = write_case(parent / (label + "-phase-read-drift"), {"Phase": phase})
            result = subprocess.run(["bash", str(HELPER), "--nonterminal-yield", str(race)],
                                    text=True, capture_output=True, env=environment)
            assert (race / "schedule-triggered").read_text() == "0", "phase mutation must follow a successful predicate"
            assert result.returncode != 0 and "yield read-set changed" in result.stderr, result.stdout + result.stderr
            print("PASS " + label + "-phase-read-drift")
        # The regular-file lstat can race an actual FIFO replacement. Exercise
        # both new open sites without altering the source being executed.
        if hasattr(os, "mkfifo"):
            for stage, argument_count in (("initial", 4), ("predicate", 3)):
                race = write_case(parent / (stage + "-fifo-race"))
                wrapper = parent / (stage + "-fifo-bin")
                wrapper.mkdir()
                trigger = parent / (stage + "-fifo-trigger.json")
                python = wrapper / "python"
                python.write_text("\n".join([
                    "#!" + sys.executable, "from pathlib import Path", "import os,sys,json",
                    "args=[a for a in sys.argv[1:] if a != '-B']",
                    "if len(args)==" + str(argument_count) + " and args[0]=='-' and args[1].endswith('/STATE.md'):",
                    "    source=sys.stdin.read();state=Path(args[1]);prior_open=os.open",
                    "    trigger=Path(" + repr(str(trigger)) + ")",
                    "    def scheduled_open(path,flags,*rest,**kw):",
                    "        if str(path)==str(state) and not trigger.exists():",
                    "            state.rename(state.with_suffix('.regular-preimage'))",
                    "            os.mkfifo(state)",
                    "            trigger.write_text(json.dumps({'scheduled':True,'nonblock':bool(flags & getattr(os,'O_NONBLOCK',0))}))",
                    "        return prior_open(path,flags,*rest,**kw)",
                    "    os.open=scheduled_open;sys.argv=args",
                    "    exec(compile(source,'<unchanged-yield-consumer>','exec'),{'__name__':'__main__'})",
                    "else:",
                    "    os.execv(sys.executable,[sys.executable]+sys.argv[1:])", ""
                ]))
                python.chmod(0o700)
                process = subprocess.Popen(["bash", str(HELPER), "--nonterminal-yield", str(race)],
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, start_new_session=True,
                    env=os.environ | {"PATH": str(wrapper) + os.pathsep + os.environ["PATH"]})
                try:
                    stdout, stderr = process.communicate(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.communicate()
                    raise AssertionError(stage + " FIFO replacement blocked the read instead of refusing")
                observed = json.loads(trigger.read_text())
                assert observed == {"scheduled": True, "nonblock": True}, observed
                expected = "yield read-set unavailable" if stage == "initial" else "nonterminal yield refused"
                assert process.returncode != 0 and expected in stderr and "nonregular" in stderr, stdout + stderr
                fifo_count += 1
                print("PASS " + stage + "-fifo-replacement-refused")
        else:
            print("SKIP FIFO race controls: host has no mkfifo")
    print(f"nonterminal-yield-cases: ok ({len(cases) + 5 + fifo_count + dependency_count} record controls; native Stop UNVERIFIED)")


if __name__ == "__main__":
    main()
