#!/usr/bin/env python3
"""Prepare one actual Windows subject and the existing W-FULL operation record.

Reuses the published subject author and maintained claim/rotation/prepare owners.
No protected execute command, grant, model call, retry, or original award exists here.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import sys
import tarfile

SOURCE_HEAD = '6b353b48b2fc8a6de0c6223f48d341c484c98191'
SOURCE_TREE = '92da6bf5f9d2d8d7ea723b56f2e99c838a9d984b'


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ('source', 'python', 'bash', 'git', 'out', 'controller',
                 'preparation-authorization-reference'):
        parser.add_argument('--' + name, required=True)
    args = parser.parse_args()
    if os.name != 'nt' or sys.platform != 'win32':
        raise SystemExit('Authentic Windows preparation required; no subject created.')

    packet = Path(__file__).absolute().parent
    driver = load(Path(args.source) / 'scripts/run-r0039-windows-resume.py', 'maintained_windows_owner')
    author = load(packet / 'task_bodies.py', 'existing_actual_task_author')
    source = driver.physical(args.source)
    driver.Q.require(author.SOURCE_HEAD == SOURCE_HEAD, 'actual task source identity differs')
    tools = {name: {'path': str(driver.physical(getattr(args, name))),
                    'sha256': driver.ident(getattr(args, name))['sha256']}
             for name in ('python', 'bash', 'git')}
    driver.Q.require(Path(tools['python']['path']).samefile(sys.executable),
                     'run through the selected physical Python')
    driver.Q.direct_git_layout(tools['git']['path'])
    driver.Q.require(args.preparation_authorization_reference.strip(), 'actual preparation authority reference required')
    out = driver.separated_output(args.out, source, packet)
    out.mkdir(exist_ok=False)
    subject, raw = out / 'subject', out / 'raw'
    subject.mkdir()
    raw.mkdir()
    # The actual hosted TEMP/TMP use 8.3 aliases; pass canonical physical names
    # to the unchanged reader instead of relaxing its alias refusal.
    inherited_temp_paths = {name: os.environ[name] for name in ('TEMP', 'TMP') if name in os.environ}
    for name, value in inherited_temp_paths.items():
        os.environ[name] = str(driver.physical(value))
    env = driver.environment(tools)
    env.update(GIT_CONFIG_NOSYSTEM='1', GIT_CONFIG_GLOBAL=os.devnull, GIT_TERMINAL_PROMPT='0')
    request = {'source_root': str(source), 'subject_root': str(subject),
               'controller': args.controller, 'source_head': SOURCE_HEAD,
               'source_tree': SOURCE_TREE, 'tools': tools}
    report = {'status': 'PREPARATION_IN_PROGRESS', 'authority': 'PREPARATION_ONLY',
              'source_head': SOURCE_HEAD, 'source_tree': SOURCE_TREE,
              'controller': args.controller, 'protected_execute_called': False,
              'original_acceptance_delta': 0, 'automatic_retry': False,
              'maintained_environment': driver.environment(tools),
              'inherited_temp_paths': inherited_temp_paths}
    ordinal = 0

    def command(argv, label):
        nonlocal ordinal
        ordinal += 1
        report['last_step'] = label
        return driver.command(argv, subject, env, raw, f'{ordinal:03d}-{label}').stdout

    def git(*arguments, label):
        return command([tools['git']['path'], '-C', subject, *arguments], label)

    def claim(*arguments, label):
        return command(driver.claim(request, *arguments), label)

    try:
        # Exact setup sequence from the published owner; no fixture history is used.
        shutil.copytree(source / 'skills', subject / 'skills')
        git('-c', 'init.templateDir=', 'init', '-q', '-b', 'qualification', label='init')
        driver.save(subject / '.gitignore', b'.IMPLEMENTAUDIT/\nskills/\n')
        driver.save(subject / 'TASK.md', (
            '# Actual fresh Windows W-FULL preparation\n\n'
            f'Runtime source {SOURCE_HEAD} / {SOURCE_TREE}.\n'
            'Prepare one exact operation record; stop before protected execute.\n'
            'No historical H0, model session, old controller custody, or acceptance is asserted.\n'
        ).encode())
        git('add', '--', 'TASK.md', '.gitignore', label='add-task')
        git('-c', 'user.name=PRO-EXECUTOR-01', '-c', 'user.email=pro-executor-01@example.invalid',
            '-c', 'commit.gpgsign=false', '-c', 'core.hooksPath=NUL',
            'commit', '-qm', 'Define actual bounded Windows W-FULL preparation', label='baseline')
        driver.source_snapshot(request)
        head = git('rev-parse', 'HEAD', label='subject-head').decode().strip()
        tree = git('rev-parse', 'HEAD^{tree}', label='subject-tree').decode().strip()
        relative = claim('--controller', args.controller, 'Fresh Windows W-FULL preparation',
                         label='claim').decode().strip()
        run = subject / relative
        next_action = 'Obtain the exact owner grant, then execute and independently receive the prepared Windows operation'
        command([tools['python']['path'], '-I', '-X', 'utf8', '-B',
                 source / 'fixtures/controller-initialization/author_checkpoint.py',
                 '--repo', subject, '--run-root', relative, '--source', subject,
                 '--purpose', 'Prepare an actual new Windows W-FULL subject and exact operation record under owner engineering authority; protected execute requires its separate fresh owner grant.',
                 '--next-action', next_action], 'author-actual-task')
        inspection = json.loads(claim('--inspect-controller-initialization', args.controller,
                                      '--run-root', relative, label='inspect-initialization'))
        activation = json.loads(claim('--activate-controller', args.controller, '--run-root', relative,
                                      '--expected-initialization', inspection['initialization_token'],
                                      label='activate-exact'))
        driver.Q.require(activation['status'] == 'BOUND_ELIGIBLE_FOR_NORMAL_CURRENTNESS',
                         'actual initialization did not activate')
        actual_claim = dict(line.split('=', 1) for line in (run / '.claimed').read_text().splitlines())
        authored = {role: (run / (role + '.md')).read_bytes() for role in ('STATE', 'ROADMAP')}
        meta = {'controller': args.controller, 'claim_id': actual_claim['claim_id'],
                'run_relative': relative, 'head': head, 'tree': tree, 'next_action': next_action}
        owner_source = (source / 'skills/implementaudit/scripts/claim-run-rotation.py').read_bytes()
        bodies, frontier = author.task_bodies(meta, authored, owner_source.decode())
        # Current task facts narrow the existing author to preparation only.
        for field in ('instructions', 'authorisations'):
            bodies['STATE']['payload'][field]['value'][0]['subject'] = 'Prepare one exact Windows W-FULL operation; protected execute requires a separate fresh owner grant'
        planning = bodies['ROADMAP']['payload']['planning']['value']
        planning['goal'] = 'Prepare one exact actual Windows whole-owner operation record for owner grant and independent receiving'
        planning['action_selection']['selected'][-1] = 'maintained prepare only; protected execute withheld'
        factory = load(source / 'fixtures/canonical-state-rotation/protected_projection_v2_test.py',
                       'existing_pair_format_helpers')
        artifacts = {
            'authorization': driver.canonical({'reference': args.preparation_authorization_reference,
                'scope': 'This actual new subject preparation only; not a protected execute grant',
                'authentication': 'OWNER_INSTRUCTION_RECEIVED_BY_EXECUTOR; NOT_AUTHENTICATED_BY_TOOL'}),
            'initialization': driver.canonical(activation), 'public_owner_source': owner_source,
            'work_graph': driver.canonical({'schema': 'r5.new-task-frontier.v1',
                                           'frontier': frontier, 'authority': 'TASK_FACTS_ONLY'})}
        (run / 'evidence').mkdir()
        for name in ('authorization', 'initialization', 'public_owner_source'):
            driver.save(run / 'evidence' / (name + '.txt'), artifacts[name])
        driver.save(run / 'WORK_GRAPH.json', artifacts['work_graph'])
        pair = factory.render_pair(bodies)
        driver.Q.require(sum(map(len, pair.values())) > 131072,
                         'actual captured source population does not trigger byte policy')
        for role in ('STATE', 'ROADMAP'):
            (run / (role + '.md')).write_bytes(pair[role])
            command([tools['python']['path'], '-I', '-X', 'utf8', '-B', '-c',
                     'from pathlib import Path;import sys;sys.stdout.buffer.write(Path(sys.argv[1]).read_bytes())',
                     run / (role + '.md')], 'read-' + role)
        first_receipt = claim('--resume-controller', args.controller, '--boundary', 'new-session',
                              '--epoch', 'G0001', label='first-resume').decode().strip()
        for flag, label in (('--verify-resume-receipt', 'verify-first'),
                            ('--require-current-continuity', 'require-first')):
            operand = first_receipt if flag == '--verify-resume-receipt' else args.controller
            driver.Q.require(claim(flag, operand, label=label).decode().strip() == first_receipt,
                             'actual first receipt/currentness differs')
        artifacts['receipt'] = git('cat-file', 'blob', first_receipt.rsplit('@', 1)[1], label='first-receipt-blob')
        driver.save(run / 'owner-map.json', {'schema': 'implementaudit.rotation-owner-map.v2',
                    'owner_map': factory.build_owner_map(bodies, pair, artifacts)})
        rotation = json.loads(claim('--rotate-canonical-state', args.controller,
                                    '--owner-map', 'owner-map.json', label='first-rotation'))
        driver.Q.require(rotation['status'] == 'ROTATED', 'actual first rotation did not complete')
        claim('--require-current-continuity', args.controller, label='require-migrated')
        claim('--invalidate-continuity', args.controller, '--boundary', 'manual-resume',
              '--event', args.controller + '-actual-manual-resume', label='manual-invalidation')
        prepared = json.loads(command([tools['python']['path'], '-I', '-X', 'utf8', '-B',
            source / 'scripts/run-r0039-windows-resume.py', 'prepare', '--source', source,
            '--repo', subject, '--controller', args.controller, '--source-head', SOURCE_HEAD,
            '--source-tree', SOURCE_TREE, '--bash', tools['bash']['path'],
            '--python', tools['python']['path'], '--git', tools['git']['path'],
            '--out', out / 'operation'], 'maintained-prepare'))
        plan = Path(prepared['plan'])
        driver.Q.require(prepared['sha256'] == driver.ident(plan)['sha256'], 'prepared plan digest differs')
        report.update(status='PREPARED_ONLY_EXACT_OWNER_GRANT_REQUIRED',
                      plan=prepared, subject_root=str(subject), run_relative=relative,
                      subject_head=head, subject_tree=tree, tools=tools)
    except BaseException as error:
        report.update(status='PREPARATION_FAILED', first_failure=str(error),
                      exception_type=type(error).__name__)
        raise
    finally:
        # Fresh subject contains only public source and new task facts; preserve Git refs too.
        archive = out / 'SUBJECT.tar'
        with tarfile.open(archive, 'x') as stream:
            stream.add(subject, arcname='subject')
        report['subject_archive'] = {'path': str(archive), **driver.ident(archive)}
        driver.save(out / 'PREPARATION.json', report)
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == '__main__':
    main()
