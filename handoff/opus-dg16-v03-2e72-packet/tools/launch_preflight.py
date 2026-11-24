"""Static launch preflight for the one-shot V03 run commit (read-only; publishes no ref).

GitHub evaluates `on.push.paths` for a NEW branch with a two-dot diff against the parent of the
deepest commit pushed; if that push carries no new commit (the commit is already on any remote
ref) no file is changed and the workflow does not run (observed for 0556962). Checks:
  (a) the workflow's branch filter and job ref guard are exactly the r2 run branch;
  (b) the candidate's sole parent is the frozen subject and `git diff --name-only SUBJECT..COMMIT`
      intersects the workflow `paths` list;
  (c) the candidate is not reachable from any supplied remote ref head (equal to it or an
      ancestor of it); an unknown head refuses because reachability cannot be proved.
Optional --bundle builds `git bundle create FILE SUBJECT..<local unpublished run-branch ref at COMMIT>` and runs `git bundle verify`.

usage: launch_preflight.py --repo R --commit C [--remote-head H ...] [--bundle FILE]
"""
import argparse, json, re, subprocess, sys

SUBJECT = '2e72a912136607e464e953c71fc8e2b44d047d92'
RUN_BRANCH = 'engineering/opus-dg16-v03-2e72-r2-20261124'
WORKFLOW = '.github/workflows/dg16-r5-full-g2.yml'


class Refusal(Exception):
    pass


def need(ok, code):
    if not ok:
        raise Refusal(code)


def git(repo, *args, check=True):
    p = subprocess.run(['git', '-C', repo, *args], capture_output=True, text=True)
    if check and p.returncode:
        raise Refusal('GIT_FAILED ' + ' '.join(args) + ': ' + p.stderr.strip())
    return p


def push_filter(text):
    """Minimal reader for this workflow's fixed `on: push: branches/paths` block."""
    lines = text.split('\n')
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


def main():
    a = argparse.ArgumentParser()
    a.add_argument('--repo', required=True); a.add_argument('--commit', required=True)
    a.add_argument('--remote-head', action='append', default=[]); a.add_argument('--bundle')
    args = a.parse_args()
    report = {'schema': 'dg16.v03-launch-preflight.v1', 'authority': 'NONE', 'refusals': []}

    def step(name, fn):
        try:
            fn()
        except Refusal as exc:
            report['refusals'].append({'check': name, 'code': str(exc)})

    commit = git(args.repo, 'rev-parse', '--verify', args.commit + '^{commit}').stdout.strip()
    report['commit'] = commit

    def parent():
        parents = git(args.repo, 'rev-list', '--parents', '-n', '1', commit).stdout.split()[1:]
        report['parents'] = parents
        need(parents == [SUBJECT], 'CANDIDATE_SOLE_PARENT_NOT_SUBJECT')

    workflow = git(args.repo, 'show', commit + ':' + WORKFLOW).stdout
    flt = push_filter(workflow)

    def branch_filter():  # (a)
        report['branches'] = flt['branches']
        need(flt['branches'] == [RUN_BRANCH], 'WORKFLOW_BRANCH_FILTER')
        need(("github.ref == 'refs/heads/%s'" % RUN_BRANCH) in workflow and 'github.event.created == true' in workflow
             and 'github.event.forced == false' in workflow and "github.run_attempt == '1'" in workflow
             and "github.event.before == '0000000000000000000000000000000000000000'" in workflow, 'WORKFLOW_JOB_GUARD')

    def two_dot():  # (b)
        changed = [p for p in git(args.repo, 'diff', '--name-only', '--no-renames', SUBJECT + '..' + commit).stdout.splitlines() if p]
        matched = sorted(set(changed) & set(flt['paths']))
        report['two_dot_diff'] = {'range': SUBJECT + '..' + commit, 'changed_files': len(changed),
                                  'paths_filter_entries': len(flt['paths']), 'matched_paths': matched}
        need(matched, 'TWO_DOT_DIFF_DOES_NOT_INTERSECT_PATHS')

    def not_prepublished():  # (c)
        rows = []; report['remote_heads_checked'] = rows
        for head in args.remote_head:
            p = git(args.repo, 'rev-parse', '--verify', '--quiet', head + '^{commit}', check=False)
            need(p.returncode == 0, 'REMOTE_HEAD_UNKNOWN_REACHABILITY_UNPROVABLE ' + head)
            h = p.stdout.strip()
            reachable = git(args.repo, 'merge-base', '--is-ancestor', commit, h, check=False).returncode == 0
            rows.append({'head': h, 'candidate_reachable': reachable})
            need(not reachable, 'CANDIDATE_ALREADY_ON_REMOTE_REF ' + h)

    def bundle():
        # git bundle needs a named ref: use a LOCAL, unpublished ref in --repo (never pushed), removed after.
        ref = 'refs/heads/' + RUN_BRANCH
        need(git(args.repo, 'rev-parse', '--verify', '--quiet', ref, check=False).returncode != 0, 'BUNDLE_LOCAL_REF_EXISTS')
        git(args.repo, 'update-ref', ref, commit, '')
        try:
            git(args.repo, 'bundle', 'create', args.bundle, '^' + SUBJECT, ref)
        finally:
            git(args.repo, 'update-ref', '-d', ref, commit)
        v = git(args.repo, 'bundle', 'verify', args.bundle)
        listed = git(args.repo, 'bundle', 'list-heads', args.bundle).stdout.split()
        report['bundle'] = {'path': args.bundle, 'verify': (v.stdout + v.stderr).strip().splitlines()[-1],
                            'heads': listed, 'prerequisite': SUBJECT, 'ref_published': False}
        need(commit in listed, 'BUNDLE_HEAD_MISSING')

    for name, fn in (('parent', parent), ('a_branch_filter', branch_filter), ('b_two_dot_diff', two_dot),
                     ('c_not_prepublished', not_prepublished)):
        step(name, fn)
    if args.bundle and not report['refusals']:
        step('bundle', bundle)
    report['status'] = 'LAUNCH_PREFLIGHT_REFUSED' if report['refusals'] else 'LAUNCH_PREFLIGHT_PASS'
    print(json.dumps(report, indent=1))
    return 1 if report['refusals'] else 0


if __name__ == '__main__':
    sys.exit(main())
