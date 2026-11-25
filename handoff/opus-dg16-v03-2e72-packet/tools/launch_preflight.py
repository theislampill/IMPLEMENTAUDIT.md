"""Static launch preflight for the one-shot V03 run commit (read-only; publishes no ref).

GitHub evaluates `on.push.paths` for a NEW branch with a two-dot diff against the parent of the
deepest commit pushed; if that push carries no new commit (the commit is already on any remote
ref) no file is changed and the workflow does not run (observed for 0556962). Checks:
  (a) the workflow's branch filter and job ref guard are exactly the r2 run branch;
  (b) the candidate's sole parent is the frozen subject and `git diff --name-only SUBJECT..COMMIT`
      intersects the workflow `paths` list;
  (c) the preflight itself obtains the census of published refs (`git ls-remote --heads --tags
      REMOTE`, taken twice and required identical, non-empty and well formed). A caller-supplied
      head list is accepted only if it equals that census exactly. For every census object:
      missing locally -> REFUSE; `git merge-base --is-ancestor CANDIDATE HEAD` exit 1 -> not
      published (ok), exit 0 -> already published (REFUSE), any other exit -> REFUSE (a Git error
      is never treated as absence). PASS requires every step to succeed.
Optional --bundle (only after a PASS of all checks) builds `git bundle create FILE ^SUBJECT <local
unpublished run-branch ref at COMMIT>`, runs `git bundle verify`, and deletes the local ref.

usage: launch_preflight.py --repo R --commit C --remote REMOTE [--remote-head SHA ...] [--bundle FILE]
"""
import argparse, json, re, subprocess, sys

SUBJECT = '2e72a912136607e464e953c71fc8e2b44d047d92'
RUN_BRANCH = 'engineering/pro-dg16-v03-2e72-20261125-01'
WORKFLOW = '.github/workflows/dg16-r5-full-g2.yml'


class Refusal(Exception):
    pass


def need(ok, code):
    if not ok:
        raise Refusal(code)


def git(repo, *args, check=True):
    p = subprocess.run(['git', '-C', repo, *args], capture_output=True, text=True)
    if check and p.returncode:
        raise Refusal('GIT_FAILED ' + ' '.join(args) + ': ' + p.stderr.strip()[:300])
    return p


def push_filter(text):
    """Minimal reader for this workflow's fixed `on: push: branches/paths` block."""
    lines = text.split('\n')
    need('on:' in lines, 'WORKFLOW_ON_MISSING')
    i = lines.index('on:'); need(lines[i + 1] == '  push:', 'WORKFLOW_ON_PUSH_SHAPE')
    out, key = {'branches': [], 'paths': []}, None
    for line in lines[i + 2:]:
        if re.fullmatch(r'    (branches|paths):', line):
            key = line.strip()[:-1]; continue
        m = re.fullmatch(r'      - (\S+)', line)
        if m and key:
            out[key].append(m.group(1)); continue
        if line and not line.startswith('    '):
            break
        need(line == '', 'WORKFLOW_FILTER_UNEXPECTED_LINE ' + line)
    return out


def census(repo, remote):
    """Complete published-ref census obtained by the preflight itself; never trusted from the caller."""
    def listing():
        p = git(repo, 'ls-remote', '--heads', '--tags', remote, check=False)
        need(p.returncode == 0, 'CENSUS_COMMAND_FAILED rc=%d %s' % (p.returncode, p.stderr.strip()[:200]))
        rows = [line.split('\t') for line in p.stdout.splitlines()]
        need(rows, 'CENSUS_EMPTY')
        need(all(len(r) == 2 and re.fullmatch('[0-9a-f]{40}', r[0]) and r[1].startswith(('refs/heads/', 'refs/tags/'))
                 for r in rows), 'CENSUS_MALFORMED')
        refs = [r[1] for r in rows]
        need(len(refs) == len(set(refs)), 'CENSUS_DUPLICATE_REF')
        need(any(r.startswith('refs/heads/') for r in refs), 'CENSUS_HAS_NO_HEADS')
        return sorted((r[1], r[0]) for r in rows)
    first = listing(); second = listing()
    need(first == second, 'CENSUS_UNSTABLE_BETWEEN_TWO_LISTINGS')
    return first


def main():
    a = argparse.ArgumentParser()
    a.add_argument('--repo', required=True); a.add_argument('--commit', required=True)
    a.add_argument('--remote', help='remote name or URL whose published refs form the census')
    a.add_argument('--remote-head', action='append', default=None,
                   help='optional caller list; accepted only if it equals the obtained census objects')
    a.add_argument('--bundle')
    args = a.parse_args()
    report = {'schema': 'dg16.v03-launch-preflight.v2', 'authority': 'NONE', 'refusals': [], 'completed_checks': []}

    def step(name, fn):
        try:
            fn(); report['completed_checks'].append(name)
        except Refusal as exc:
            report['refusals'].append({'check': name, 'code': str(exc)})

    state = {}

    def candidate():
        p = git(args.repo, 'rev-parse', '--verify', '--quiet', args.commit + '^{commit}', check=False)
        need(p.returncode == 0, 'CANDIDATE_UNKNOWN')
        state['commit'] = report['commit'] = p.stdout.strip()
        parents = git(args.repo, 'rev-list', '--parents', '-n', '1', state['commit']).stdout.split()[1:]
        report['parents'] = parents
        need(parents == [SUBJECT], 'CANDIDATE_SOLE_PARENT_NOT_SUBJECT')
        state['workflow'] = git(args.repo, 'show', state['commit'] + ':' + WORKFLOW).stdout
        state['filter'] = push_filter(state['workflow'])

    def branch_filter():  # (a)
        wf, flt = state['workflow'], state['filter']
        report['branches'] = flt['branches']
        need(flt['branches'] == [RUN_BRANCH], 'WORKFLOW_BRANCH_FILTER')
        need(("github.ref == 'refs/heads/%s'" % RUN_BRANCH) in wf and 'github.event.created == true' in wf
             and 'github.event.forced == false' in wf and "github.run_attempt == '1'" in wf
             and "github.event.before == '0000000000000000000000000000000000000000'" in wf, 'WORKFLOW_JOB_GUARD')

    def two_dot():  # (b)
        changed = [p for p in git(args.repo, 'diff', '--name-only', '--no-renames', SUBJECT + '..' + state['commit']).stdout.splitlines() if p]
        matched = sorted(set(changed) & set(state['filter']['paths']))
        report['two_dot_diff'] = {'range': SUBJECT + '..' + state['commit'], 'changed_files': len(changed),
                                  'paths_filter_entries': len(state['filter']['paths']), 'matched_paths': matched}
        need(matched, 'TWO_DOT_DIFF_DOES_NOT_INTERSECT_PATHS')

    def not_published():  # (c)
        need(args.remote, 'CENSUS_REMOTE_NOT_GIVEN')
        rows = census(args.repo, args.remote)
        objects = sorted({sha for _, sha in rows})
        report['census'] = {'remote': args.remote, 'refs': len(rows), 'objects': len(objects),
                            'listing_sha256': __import__('hashlib').sha256(json.dumps(rows).encode()).hexdigest()}
        if args.remote_head is not None:
            supplied = sorted(set(args.remote_head))
            report['census']['caller_list'] = {'supplied': len(supplied), 'equal': supplied == objects}
            need(supplied == objects, 'CALLER_HEAD_LIST_NOT_EQUAL_TO_CENSUS supplied=%d census=%d' % (len(supplied), len(objects)))
        published, errors = [], []
        for sha in objects:
            if git(args.repo, 'cat-file', '-e', sha, check=False).returncode != 0:
                errors.append({'object': sha, 'error': 'CENSUS_OBJECT_MISSING_LOCALLY_FETCH_FIRST'}); continue
            rc = git(args.repo, 'merge-base', '--is-ancestor', state['commit'], sha, check=False).returncode
            if rc == 0:
                published.append(sha)
            elif rc != 1:
                errors.append({'object': sha, 'error': 'MERGE_BASE_EXIT_%d' % rc})
        report['census'].update(checked=len(objects), already_published=published, errors=errors[:20], error_count=len(errors))
        need(not published, 'CANDIDATE_ALREADY_PUBLISHED ' + ','.join(published))
        need(not errors, 'CENSUS_REACHABILITY_UNPROVABLE %d error(s)' % len(errors))

    def bundle():
        ref = 'refs/heads/' + RUN_BRANCH   # LOCAL and unpublished; removed afterwards
        need(git(args.repo, 'rev-parse', '--verify', '--quiet', ref, check=False).returncode != 0, 'BUNDLE_LOCAL_REF_EXISTS')
        git(args.repo, 'update-ref', ref, state['commit'], '')
        try:
            git(args.repo, 'bundle', 'create', args.bundle, '^' + SUBJECT, ref)
        finally:
            git(args.repo, 'update-ref', '-d', ref, state['commit'])
        v = git(args.repo, 'bundle', 'verify', args.bundle)
        listed = git(args.repo, 'bundle', 'list-heads', args.bundle).stdout.split()
        report['bundle'] = {'path': args.bundle, 'verify': (v.stdout + v.stderr).strip().splitlines()[-1],
                            'heads': listed, 'prerequisite': SUBJECT, 'ref_published': False}
        need(state['commit'] in listed, 'BUNDLE_HEAD_MISSING')

    step('candidate', candidate)
    if 'filter' in state:
        for name, fn in (('a_branch_filter', branch_filter), ('b_two_dot_diff', two_dot), ('c_not_published', not_published)):
            step(name, fn)
    required = ['candidate', 'a_branch_filter', 'b_two_dot_diff', 'c_not_published']
    ready = not report['refusals'] and report['completed_checks'] == required
    if args.bundle and ready:
        step('bundle', bundle)
        ready = not report['refusals']
    report['status'] = 'LAUNCH_PREFLIGHT_PASS' if ready else 'LAUNCH_PREFLIGHT_REFUSED'
    print(json.dumps(report, indent=1))
    return 0 if ready else 1


if __name__ == '__main__':
    sys.exit(main())
