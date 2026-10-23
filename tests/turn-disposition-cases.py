#!/usr/bin/env python3
"""Composed R0037 record dispositions; these controls grant no host authority."""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('yield_cases', ROOT / 'tests/nonterminal-yield-cases.py')
yield_cases = importlib.util.module_from_spec(spec)
spec.loader.exec_module(yield_cases)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--helper', type=Path, default=ROOT / 'skills/implementaudit/scripts/validate-run-root.sh')
    parser.add_argument('--repo-root', type=Path, default=Path.cwd())
    args = parser.parse_args()
    head = subprocess.check_output(['git', '-C', str(args.repo_root), 'rev-parse', 'HEAD'], text=True).strip()
    results = []
    with tempfile.TemporaryDirectory(prefix='turn-disposition-') as tmp:
        tmp = Path(tmp)
        def case(name, disposition, expected, change=None, contains='', hook=None):
            root = tmp / name
            changes = {}
            if disposition == 'TERMINAL_CLOSURE':
                changes = {'Status': 'DONE', 'Audit object state': 'terminal verified closure'}
            elif disposition == 'AUDITED_HANDOFF':
                changes = {'Status': 'BLOCKED', 'Blocker': 'Owner request request-17 requires another executor',
                    'Containment': 'No dependent effect or terminal claim admitted',
                    'Next probe': 'Receive request-17 continuation authorization',
                    'Next action': 'Owner executor receives checkpoint C1 and revalidates inputs',
                    'Handoff basis': 'owner-request', 'Handoff evidence': 'evidence/owner-request.md'}
            yield_cases.write_case(root, changes)
            (root / 'evidence').mkdir(exist_ok=True)
            record = root / ('closure.md' if disposition == 'TERMINAL_CLOSURE' else 'handoff.md')
            if disposition == 'TERMINAL_CLOSURE':
                state = root / 'STATE.md'
                state.write_text(state.read_text() + '\n## Final closure checker inputs\n\n'
                    '| Input | Value |\n|---|---|\n| Superseded plans | none |\n'
                    '| Cycle-accounted plans | none |\n| Steer directory | ' + str(root) + ' |\n')
                roadmap = root / 'ROADMAP.md'
                roadmap.write_text(roadmap.read_text().replace('| pending |', '| done |'))
                phase = root / 'phases/phase-1.md'
                phase.write_text(phase.read_text().replace('- [ ]', '- [x]').replace('Status recorded here.', 'Status: done'))
                record.write_text('AUDIT_START\nRound: 1\nAUDIT_START_ANCHOR: ' + head + '\n'
                    'AUDIT_VERIFY\nAUDIT_VERIFY_ANCHOR: ' + head + '\n'
                    'REANCHOR_DISPOSITION: unchanged\nREANCHOR_EVIDENCE: none\n'
                    'equivalent_config_attempts: 1/1\nstochasticity_budget: none\n'
                    'terminal_qualification: QUALIFIED\n'
                    're_verified / (re_verified + trust_prior) = 1 / (1 + 0) = 1\n'
                    'claim: C1 | surface: source | status: verified | evidence-surface: source\n'
                    'AUDIT_COMPLETE\nIMPLEMENTAUDIT_RUN_COMPLETE\n')
            elif disposition == 'AUDITED_HANDOFF':
                (root / 'evidence/owner-request.md').write_text('request-17: Owner requests handoff to the receiving executor before completion.\n')
                record.write_text('packet_id: request-17\npacket_version: 1\npacket_content_hash: PLACEHOLDER\n'
                    'sender_run_id: composed-control\nhas_state_claims: no\nAUDIT_HANDOFF\n')
            extra = []
            if change:
                extra = change(root, record) or []
            if disposition == 'AUDITED_HANDOFF' and record.is_file() and not record.is_symlink():
                raw = record.read_bytes()
                body = b''.join(line for line in raw.splitlines(keepends=True) if not line.startswith(b'packet_content_hash:'))
                digest = hashlib.sha256(body).hexdigest().encode('ascii')
                record.write_bytes(raw.replace(b'packet_content_hash: PLACEHOLDER', b'packet_content_hash: ' + digest))
            selected_helper = args.helper
            if hook:
                skill = tmp / (name + '-skill')
                shutil.copytree(args.helper.parent.parent, skill)
                owners = skill / 'scripts'
                selected_helper = owners / args.helper.name
                consumer = owners / 'check-closure-surface.sh'
                consumer.write_text(consumer.read_text() + '\n' + hook + '\n')
            command = ['bash', str(selected_helper), '--turn-disposition', disposition, str(root)]
            if disposition != 'NONTERMINAL_YIELD':
                command += ['--closure-record' if disposition == 'TERMINAL_CLOSURE' else '--handoff-packet', str(record)]
            command += extra
            completed = subprocess.run(command, cwd=args.repo_root, text=True, capture_output=True, timeout=30)
            output = completed.stdout + completed.stderr
            passed = (completed.returncode == 0) == expected and (not contains or contains in output)
            if expected and completed.returncode == 0:
                try:
                    result = json.loads(completed.stdout.splitlines()[-1])
                    passed &= result['record_disposition'] == disposition and result['authority'] == 'NONE'
                    passed &= result['native_enforcement'] is False and result['effect_authority'] is False
                    passed &= 'stop_allowed' not in result and 'object_closed' not in result
                except (ValueError, KeyError, IndexError):
                    passed = False
            pid_record = root / 'closure.md.pids'
            if pid_record.is_file():
                for pid in pid_record.read_text().split():
                    status = Path('/proc') / pid / 'stat'
                    if status.exists() and status.read_text().split()[2] not in {'Z','X'}:
                        passed = False
                        output += '\nLaunched process remains active: ' + pid
            results.append({'case': name, 'expected_accept': expected, 'exit': completed.returncode,
                            'pass': bool(passed), 'output': output})
        def replace(path, old, new):
            path.write_text(path.read_text().replace(old, new))
        def andon(root, packet):
            state = root / 'STATE.md'
            replace(state, '| Handoff basis | owner-request |', '| Handoff basis | andon |')
            replace(state, 'Owner request request-17 requires another executor', 'provider request-17 is unavailable')
            replace(state, 'Owner executor receives checkpoint C1 and revalidates inputs', 'Owner supplies the terminal request-17 result')
            state.write_text(state.read_text() + '| 1 | occ-17 | 1 | dependency | provider unavailable | bounded probe request-17 | evidence/owner-request.md | blocked (handoff condition) |\n')
            phase = root / 'phases/phase-1.md'
            replace(phase, 'Status recorded here.', 'Status: blocked')
            replace(packet, 'AUDIT_HANDOFF', 'ANDON_HANDOFF')
            packet.write_text(packet.read_text() + 'Phase: 1\nFailing criterion: request-17 provider result absent\n'
                'Probe and escalation history: evidence/owner-request.md records provider checks and escalation\n'
                'Handoff trigger: external-dependency\nRemaining blocker: provider request-17 is unavailable\n'
                'Next owner action: Owner supplies the terminal request-17 result\n')
        def plans(root, record):
            path = root / 'replaced-plan.md'
            path.write_text('SUPERSEDED_BY: ROADMAP.md — accepted refinement\n- [ ] Stale objective | RECONCILIATION: STALE\n')
            replace(root/'STATE.md', '| Superseded plans | none |', '| Superseded plans | replaced-plan.md |')
            return ['--superseded-plan', str(path)]
        def full_state(root, record):
            template = (ROOT/'skills/implementaudit/templates/STATE.md').read_text()
            minimal = (root/'STATE.md').read_text()
            start = minimal.index('## Current phase')
            end = minimal.index('## Andon log')
            template = template[:template.index('## Current phase')] + minimal[start:end] + template[template.index('## Audit object state'):]
            template = template.replace('## AGENTS_UPDATE_DECISION\n\nStatus: pending', '## AGENTS_UPDATE_DECISION\n\nStatus: not warranted')
            template = template.replace('## CONTINUITY_DECISION\n\nStatus: pending', '## CONTINUITY_DECISION\n\nStatus: none')
            template = template.replace('Reason:\n', 'Reason: Focused record qualification changes no enduring project behavior.\n')
            (root/'STATE.md').write_text(template)
        case('full-state-template-positive', 'TERMINAL_CLOSURE', True, full_state)
        case('full-state-pending-continuity', 'TERMINAL_CLOSURE', False,
            lambda r,p: (full_state(r,p),replace(r/'STATE.md','## CONTINUITY_DECISION\n\nStatus: none','## CONTINUITY_DECISION\n\nStatus: pending')) and None)
        case('active-rehearsal-does-not-execute', 'TERMINAL_CLOSURE', False,
            lambda r,p: (r/'phases/phase-1.md').write_text((r/'phases/phase-1.md').read_text()+'\nScarce resource budget: real-producer-launch\n') and None,
            contains='unsupported active rehearsal')
        case('missing-andon-phase', 'AUDITED_HANDOFF', False,
            lambda r,p: (andon(r,p),replace(p,'Phase: 1\n','')) and None, contains='phase mismatch')
        case('andon-handoff-positive', 'AUDITED_HANDOFF', True, andon)
        case('andon-no-count-cap', 'AUDITED_HANDOFF', False,
            lambda r,p: (andon(r,p), replace(p, 'Handoff trigger: external-dependency', 'Handoff trigger: retry-cap')) and None)
        case('applicable-plan-positive', 'TERMINAL_CLOSURE', True, plans)
        case('omitted-applicable-plan', 'TERMINAL_CLOSURE', False,
            lambda r,p: (plans(r,p), None)[1])
        case('multiple-claims-positive', 'TERMINAL_CLOSURE', True,
            lambda r,p: replace(p, 'AUDIT_COMPLETE\n', 'claim: C2 | surface: source | status: verified | evidence-surface: source\nAUDIT_COMPLETE\n'))
        case('false-coverage-arithmetic', 'TERMINAL_CLOSURE', False,
            lambda r,p: replace(p, '= 1 / (1 + 0) = 1', '= 1 / (1 + 0) = 0'))
        case('zero-coverage-denominator', 'TERMINAL_CLOSURE', False,
            lambda r,p: replace(p, '= 1 / (1 + 0) = 1', '= 0 / (0 + 0) = 1'))
        case('valid-owner-disposition-positive', 'TERMINAL_CLOSURE', True,
            lambda r,p: (r/'STATE.md').write_text((r/'STATE.md').read_text() + '\n## Occurrence resolution and residuals\nOccurrence resolution: partially-resolved\n'
                '| Residual | Consequential | Disposition | Owner / policy ref | Evidence |\n|---|---|---|---|---|\n'
                '| residual-17 | yes | transferred | receiving executor issue-211 | evidence/checkpoint-C1 |\n') and None)
        case('read-substitution-after-owner', 'TERMINAL_CLOSURE', False,
            contains='read-set changed', hook='printf "\\nsubstituted after consumption\\n" >> "$file"')
        case('added-input-after-owner', 'TERMINAL_CLOSURE', False,
            contains='read-set changed', hook='printf "new steer\\n" > "$(dirname "$file")/added-steer.md"')
        case('removed-input-after-owner', 'TERMINAL_CLOSURE', False,
            contains='read-set changed', hook='rm "$(dirname "$file")/THINKING.md"')
        case('source-directory-ABA-after-owner', 'TERMINAL_CLOSURE', False,
            contains='owner source changed', hook='owner_dir="$(dirname "$0")"; mv "$owner_dir" "$owner_dir.kept"; mkdir "$owner_dir"; printf "#!/usr/bin/env bash\\nexit 0\\n" > "$owner_dir/check-lesson-lift.sh"; bash "$owner_dir/check-lesson-lift.sh" "$file"; rm "$owner_dir/check-lesson-lift.sh"; rmdir "$owner_dir"; mv "$owner_dir.kept" "$owner_dir"')
        case('source-substitution-after-owner', 'TERMINAL_CLOSURE', False,
            contains='owner source changed', hook='printf "\\n# source substituted after consumption\\n" >> "$(dirname "$0")/validate-run-root.sh"')
        for verdict in ('BLOCKED','GAP-REVISE'):
            case('declared-review-' + verdict, 'TERMINAL_CLOSURE', False,
                lambda r,p,v=verdict: (r/'ROADMAP.md').write_text('# Roadmap\n| Phase | Objective | Review | Status |\n|---|---|---|---|\n| 1 | Greeting repair | '+v+' | done |\n') and None)
        case('declared-review-PASS', 'TERMINAL_CLOSURE', True,
            lambda r,p: (r/'ROADMAP.md').write_text('# Roadmap\n| Phase | Objective | Review | Status |\n|---|---|---|---|\n| 1 | Greeting repair | PASS | done |\n') and None)
        case('directory-ABA-after-owner', 'TERMINAL_CLOSURE', False,
            contains='read-set changed', hook='base="$(dirname "$file")"; mv "$base/evidence" "$base/kept-evidence"; mkdir "$base/evidence"; rmdir "$base/evidence"; mv "$base/kept-evidence" "$base/evidence"')
        case('documented-review-not-applicable', 'TERMINAL_CLOSURE', True,
            lambda r,p: (r/'ROADMAP.md').write_text('# Roadmap\n| Phase | Objective | Review | Status |\n|---|---|---|---|\n| 1 | Greeting repair | not applicable | done |\n') and None)
        case('yield-future-capture-is-not-required', 'NONTERMINAL_YIELD', True,
            lambda r,p: replace(r/'phases/phase-1.md', '## Mandatory commands\n', '## Mandatory commands\n- `true`; capture: evidence/not-produced-yet.log; expected: exit 0\n'))
        case('yield-positive', 'NONTERMINAL_YIELD', True)
        case('closure-positive', 'TERMINAL_CLOSURE', True)
        case('owner-handoff-positive', 'AUDITED_HANDOFF', True)
        case('crlf-packet-positive', 'AUDITED_HANDOFF', True,
             lambda r,p: p.write_bytes(p.read_bytes().replace(b'\r\n', b'\n').replace(b'\n', b'\r\n')) and None)
        case('yield-cannot-downgrade-done', 'NONTERMINAL_YIELD', False,
             lambda r,p: replace(r/'STATE.md', '| IN_PHASE |', '| DONE |'))
        case('yield-terminal-response', 'NONTERMINAL_YIELD', False,
             lambda r,p: (p.write_text('AUDIT_COMPLETE\nIMPLEMENTAUDIT_RUN_COMPLETE\n'), ['--response-record', str(p)])[1])
        case('mixed-markers', 'TERMINAL_CLOSURE', False,
             lambda r,p: p.write_text(p.read_text() + 'AUDIT_HANDOFF\n') and None)
        case('structural-green-unverified', 'TERMINAL_CLOSURE', False,
             lambda r,p: replace(p, '| status: verified |', '| status: unverified |'))
        case('missing-current-anchor', 'TERMINAL_CLOSURE', False,
             lambda r,p: replace(p, 'AUDIT_VERIFY_ANCHOR: ' + head + '\n', ''))
        case('wrong-final-order', 'TERMINAL_CLOSURE', False,
             lambda r,p: replace(p, 'AUDIT_COMPLETE\nIMPLEMENTAUDIT_RUN_COMPLETE', 'IMPLEMENTAUDIT_RUN_COMPLETE\nAUDIT_COMPLETE'))
        case('nonterminal-phase', 'TERMINAL_CLOSURE', False,
             lambda r,p: replace(r/'ROADMAP.md', '| done |', '| pending |'))
        case('unverified-criterion', 'TERMINAL_CLOSURE', False,
             lambda r,p: replace(r/'phases/phase-1.md', '- [x]', '- [ ]'))
        case('pending-child-success-is-not-closure', 'TERMINAL_CLOSURE', False,
             lambda r,p: replace(r/'STATE.md', '| terminal verified closure |', '| open; child RETURNED success, JOIN pending |'))
        case('handoff-packet-alone', 'AUDITED_HANDOFF', False,
             lambda r,p: replace(r/'STATE.md', '| Handoff evidence | evidence/owner-request.md |', ''))
        case('handoff-cannot-be-done', 'AUDITED_HANDOFF', False,
             lambda r,p: replace(r/'STATE.md', '| BLOCKED |', '| DONE |'))
        case('handoff-no-owner-source', 'AUDITED_HANDOFF', False,
             lambda r,p: replace(r/'STATE.md', '| Owner/source | issue207/211 governor |', ''))
        case('closure-unresolved-ledger', 'TERMINAL_CLOSURE', False,
             lambda r,p: (r/'deferrals.jsonl').write_text('{"ts":"2026-10-23T00:00:00Z","phase":"1","what":"required check","why":"blocked","owner":"owner","unblock":"access grant","disposition":"pending"}\n') and None)
        case('conflicting-response', 'AUDITED_HANDOFF', False,
             lambda r,p: ((r/'response.md').write_text('IMPLEMENTAUDIT_RUN_COMPLETE\n'), ['--response-record', str(r/'response.md')])[1])
        if hasattr(os,'mkfifo'):
            case('fifo-record', 'TERMINAL_CLOSURE', False,
                 lambda r,p: (p.unlink(), os.mkfifo(p)) and None)
            case('fifo-at-subordinate-open', 'TERMINAL_CLOSURE', False,
                 contains='owner read timed out; no disposition',
                 hook='rm "$file"; mkfifo "$file"; cat "$file" & reader_pid=$!; printf "%s %s\\n" "$$" "$reader_pid" > "${file}.pids"; wait "$reader_pid"')
        case('symlink-record', 'TERMINAL_CLOSURE', False,
             lambda r,p: (p.rename(r/'real-closure.md'), p.symlink_to('real-closure.md')) and None)
    print(json.dumps({'passed':sum(r['pass'] for r in results),'total':len(results),'results':results}, indent=2))
    return 0 if all(r['pass'] for r in results) else 1


if __name__ == '__main__':
    raise SystemExit(main())
