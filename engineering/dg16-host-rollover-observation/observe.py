#!/usr/bin/env python3
"""One bounded public host/runtime observation; no adoption or operation entry.

The historical profile reader is reused byte for byte. The selected source and
12-selector observer are the exact current bodies; this adapter only joins their
read-only results plus one exact Git clone alias. All output is unqualified
observation, including a MATCH.
"""
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import signal
import stat
import sys
import time
import types

REPOSITORY = 'theislampill/IMPLEMENTAUDIT.md'
BRANCH = 'engineering/pro-dg16-host-rollover-observe-20261126-05'
WORKFLOW = '.github/workflows/dg16-host-rollover-observe.yml'
RELATIVE = 'engineering/dg16-host-rollover-observation'
PACKET = 'qualification/dg16-r5-g1-hosted-episode-v21/packet'
SOURCE = '6d2c0c3522ce128ea8143d7fc93e1180f46227f8'
TREE = 'a0c86d6a71e1f8b9ac3aed2d7c984ac79aeef26e'
ALLOWED_IMAGES = ('20261116.376.1', '20261116.133.1', '20261122.23.1')
PROFILE_READER_SHA256 = '15a0be03138e3d6767a20d17c3d9066c6f7ba27c47024f6494729b7c4da62b62'
PINS = {
    'operation.py': 'ac0760a9f1d124d29df9fd282df689ac8aeb0336fc11e6bb6a2b9e4aa453f13f',
    'runtime_preflight.py': '8d6ff960139767c333714bf951cb79bb4205b8c61bbf9df8c578d2ff37cc5a40',
    'host_utility.py': '51a88c08bbea3fd82986aaa6028aa16b92f5500de48950300398e542d5701b5a',
    'SOURCE_MANIFEST.json': '06a8cd9b2e4ab37c71784342f7d83e58b6d879c58fee0649d88273f5a96ecc28',
}
MAX_OUTPUT = 98304
DEADLINE_SECONDS = 120
PROFILE_AND_SOURCE_READ_BYTES = 512 * 1024**2
MEMORY_BYTES = 768 * 1024**2
CLONE_ALIAS = '/usr/bin/git-upload-pack'
CLONE_ALIAS_EXPECTED = {'bytes': 4640352, 'link': 'git', 'mode': 493, 'resolved': '/usr/bin/git', 'sha256': '824d5b2fffef332ec7ba053e579659bb12f26a0b4747da6f9c6dc0e71d36f235'}
GIT_FILES_SHA256 = 'a7a96fbd6a3144abb6d2d5efd26d48630336dc29c38f9d0e0c7beff2fb90f436'
MAX_ALIAS_PUBLIC_BYTES = 32768


class Refusal(ValueError):
    pass


class Deadline(BaseException):
    """The immutable readers' ordinary ValueError refusals must not consume this."""


def expired(_sig, _frame):
    raise Deadline('DEADLINE')


def need(value, code):
    if not value:
        raise Refusal(code)


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'),
                       ensure_ascii=True, allow_nan=False) + '\n').encode('ascii')


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def module(raw, path, expected):
    need(type(raw) is bytes and len(raw) <= 1024**2 and sha(raw) == expected, 'MODULE_PIN')
    value = types.ModuleType('read_only_' + path.stem)
    value.__file__ = str(path)
    exec(compile(raw, str(path), 'exec'), value.__dict__)
    return value


def context(env):
    fixed = {'GITHUB_ACTIONS': 'true', 'RUNNER_ENVIRONMENT': 'github-hosted',
             'GITHUB_REPOSITORY': REPOSITORY, 'GITHUB_REF': 'refs/heads/' + BRANCH,
             'GITHUB_RUN_ATTEMPT': '1', 'GITHUB_EVENT_NAME': 'push', 'DG16_FRESH_BRANCH_PUSH': 'true',
             'GITHUB_JOB': 'observe', 'ImageOS': 'ubuntu24',
             'GITHUB_WORKFLOW_REF': REPOSITORY + '/' + WORKFLOW + '@refs/heads/' + BRANCH}
    need(all(env.get(key) == value for key, value in fixed.items()), 'CONTEXT')
    need(env.get('ImageVersion') in ALLOWED_IMAGES, 'IMAGE_CONTEXT')
    head, run = env.get('GITHUB_SHA', ''), env.get('GITHUB_RUN_ID', '')
    need(re.fullmatch('[0-9a-f]{40}', head) is not None and env.get('GITHUB_WORKFLOW_SHA') == head
         and re.fullmatch('[1-9][0-9]{0,19}', run) is not None, 'CONTEXT')
    return dict(repository=REPOSITORY, branch=BRANCH, workflow=WORKFLOW, job='observe',
                run_id=run, run_attempt=1, workflow_commit=head, fresh_branch_push=True,
                image_version=env['ImageVersion'])


def profiles(raw):
    # Only a literal data assignment is consumed from the current host utility.
    nodes = [node.value for node in ast.parse(raw).body if isinstance(node, ast.Assign)
             and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
             and node.targets[0].id == 'G1_HOST_PROFILES']
    need(len(nodes) == 1, 'PROFILE_POPULATION')
    rows = ast.literal_eval(nodes[0])
    need(type(rows) is tuple and len(rows) == 5 and len({row['id'] for row in rows}) == 5,
         'PROFILE_POPULATION')
    return rows


def require_runtime_bookends(value):
    # A stable new tuple can differ from prior pins; incomplete or drifting
    # captures cannot establish the requested measurement's closing bookend.
    need(value['selector_count'] == 12 and value['source_current'] is True
         and all(row['opening']['kind'] == row['closing']['kind'] == 'FILE'
                 and row['bookends_equal'] is True for row in value['selectors']),
         'RUNTIME_CAPTURE_INCOMPLETE_OR_CHANGED')


def source_census(reader, source, manifest, budget):
    """Exact source bodies/modes, including ignored files; only .git is separate."""
    need(manifest['commit'] == SOURCE and manifest['tree'] == TREE
         and manifest['file_count'] == 1991 and manifest['total_bytes'] == 175658093,
         'SOURCE_MANIFEST_SUBJECT')
    wanted = {row['path']: row for row in manifest['members']}
    need(len(wanted) == 1991, 'SOURCE_MANIFEST_POPULATION')
    allowed_dirs = {str(parent) for name in wanted for parent in Path(name).parents if str(parent) != '.'}
    observed = set(); total = 0; entries = 0; digest = hashlib.sha256()
    for parent, dirs, files in os.walk(source, followlinks=False):
        dirs.sort(); files.sort()
        if Path(parent) == source:
            if '.git' in dirs: dirs.remove('.git')
            if '.git' in files: files.remove('.git')
        for name in dirs:
            path = Path(parent) / name; relative = path.relative_to(source).as_posix()
            info = path.lstat(); entries += 1
            need(entries <= 4096 and relative in allowed_dirs and not path.is_symlink()
                 and stat.S_ISDIR(info.st_mode), 'SOURCE_DIRECTORY')
        for name in files:
            path = Path(parent) / name; relative = path.relative_to(source).as_posix(); entries += 1
            need(entries <= 4096 and relative in wanted and relative not in observed
                 and not path.is_symlink(), 'SOURCE_POPULATION')
            expected = wanted[relative]
            row, _ = reader.read_file(path, 128 * 1024**2, budget, (source,))
            need(row['canonical'] == str(path) and row['stat']['nlink'] == 1
                 and stat.S_IMODE(row['stat']['mode']) == (0o755 if expected['mode'] == '100755' else 0o644)
                 and row['bytes'] == expected['bytes'] and row['sha256'] == expected['sha256'], 'SOURCE_MEMBER')
            digest.update(encode(row)); observed.add(relative); total += row['bytes']
    need(observed == set(wanted) and total == 175658093, 'SOURCE_POPULATION')
    return dict(files=len(observed), bytes=total, entries=entries,
                physical_bookend_sha256=digest.hexdigest(), all_manifest_members_match=True,
                includes_ignored_files=True, git_head_checked_separately=True)


def clone_alias_selection(engine):
    """Bind the one extra requested spelling to the exact selected declarations."""
    engine.CHECK()
    selected = engine.SPEC['git_files']
    need(type(selected) is dict and len(selected) == 17
         and sha(encode(selected)) == GIT_FILES_SHA256
         and selected.get(CLONE_ALIAS) == CLONE_ALIAS_EXPECTED, 'CLONE_ALIAS_SOURCE_BINDING')


def clone_alias_compare(observer, opening, closing):
    """A stable mismatch is useful observation, never pin adoption."""
    observer.validate_row(opening); observer.validate_row(closing)
    need(opening['kind'] == closing['kind'] == 'FILE' and opening == closing,
         'CLONE_ALIAS_CAPTURE_INCOMPLETE_OR_CHANGED')
    match = all(opening[key] == CLONE_ALIAS_EXPECTED[key] for key in observer.FIELDS)
    value = dict(schema='dg16.fixed-git-clone-alias-observation.v1',
        source_revision=observer.REVISION, requested=CLONE_ALIAS,
        selected_git_files_sha256=GIT_FILES_SHA256, expected=dict(CLONE_ALIAS_EXPECTED),
        opening=dict(opening), closing=dict(closing), opening_match=match, closing_match=match,
        bookends_equal=True, match=match, status='MATCH' if match else 'REFUSED',
        source_current=True, complete_runtime_qualification=False, automatic_adoption=False)
    need(len(encode(value)) <= MAX_ALIAS_PUBLIC_BYTES, 'CLONE_ALIAS_PUBLIC_BOUND')
    return value


def public_clone_alias(observer, value):
    need(type(value) is dict and set(value) == {
        'schema','source_revision','requested','selected_git_files_sha256','expected',
        'opening','closing','opening_match','closing_match','bookends_equal','match','status',
        'source_current','complete_runtime_qualification','automatic_adoption'}, 'CLONE_ALIAS_PUBLIC_PROJECTION')
    rebuilt = clone_alias_compare(observer, value['opening'], value['closing'])
    need(encode(value) == encode(rebuilt), 'CLONE_ALIAS_PUBLIC_PROJECTION')
    return rebuilt


def main():
    need(len(sys.argv) == 1 and sys.flags.isolated == 1 and sys.flags.no_site == 1
         and sys.dont_write_bytecode is True, 'ISOLATED_ENTRY')
    ctx = context(os.environ)
    need(sys.platform == 'linux' and os.getuid() == os.geteuid() == os.getgid() == os.getegid() == 0,
         'ROOT_OBSERVER_REQUIRED')
    signal.signal(signal.SIGALRM, expired); signal.signal(signal.SIGTERM, expired)
    signal.alarm(DEADLINE_SECONDS)
    resource.setrlimit(resource.RLIMIT_AS, (MEMORY_BYTES, MEMORY_BYTES))
    resource.setrlimit(resource.RLIMIT_CPU, (60, 60))
    resource.setrlimit(resource.RLIMIT_FSIZE, (MAX_OUTPUT, MAX_OUTPUT))
    resource.setrlimit(resource.RLIMIT_NOFILE, (64, 64))
    started = time.time_ns()
    workspace = Path(os.environ.get('GITHUB_WORKSPACE', ''))
    need(workspace.is_absolute() and workspace.resolve(strict=True) == workspace, 'WORKSPACE')
    packet_root, source = workspace / 'packet', workspace / 'source'
    here = packet_root / RELATIVE
    need(Path(__file__).absolute() == here / 'observe.py' and here.resolve(strict=True) == here, 'ENTRY_LOCATION')
    reader_path = here / 'profile_reader.py'
    # This bootstrap read is bounded and digest-authenticated before compilation.
    fd = os.open(reader_path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try: raw = os.read(fd, 65537)
    finally: os.close(fd)
    need(len(raw) <= 65536, 'READER_BOUND')
    reader = module(raw, reader_path, PROFILE_READER_SHA256)
    budget = reader.Budget(PROFILE_AND_SOURCE_READ_BYTES, DEADLINE_SECONDS)
    held = {}; bodies = {}
    relative_pins = {RELATIVE + '/profile_reader.py': PROFILE_READER_SHA256,
                     **{PACKET + '/' + name: pin for name, pin in PINS.items()}}
    observer_pin = os.environ.get('EXPECTED_OBSERVER_SHA256', '')
    need(re.fullmatch('[0-9a-f]{64}', observer_pin) is not None, 'OBSERVER_PIN')
    relative_pins[RELATIVE + '/observe.py'] = observer_pin
    for relative, pin in relative_pins.items():
        row, body = reader.read_file(packet_root / relative, 1024**2, budget, (packet_root,), retain=True)
        need(row['requested'] == row['canonical'] and row['sha256'] == pin, 'MODULE_PIN')
        held[relative] = row; bodies[relative] = body
    for root, expected in ((packet_root, ctx['workflow_commit']), (source, SOURCE)):
        row, body = reader.read_file(root / '.git/HEAD', 128, budget, (root,), retain=True)
        need(body == (expected + '\n').encode('ascii'), 'CHECKOUT_HEAD')
        held[str(root / '.git/HEAD')] = row
    baseline = profiles(bodies[PACKET + '/host_utility.py'])
    manifest = json.loads(bodies[PACKET + '/SOURCE_MANIFEST.json'])
    opening_source = source_census(reader, source, manifest, budget)
    facts, release = reader.capture_facts(budget)
    need(facts['image_version'] == ctx['image_version'], 'IMAGE_CONTEXT_CHANGED')
    need(facts['os'] == {'ID': 'ubuntu', 'VERSION_ID': '24.04'} and facts['architecture'] == 'x86_64',
         'HOST_FAMILY')
    boot = reader.read_boot_identity(budget)
    tools = {name: reader.observe_tool(Path('/usr/bin') / name, budget, (Path('/usr'),))
             for name in reader.TOOLS}
    need(tools['python3.12'].get('available') is True
         and Path(sys.executable).resolve(strict=True) == Path(tools['python3.12']['canonical']), 'INTERPRETER')
    owner = module(bodies[PACKET + '/operation.py'], packet_root / PACKET / 'operation.py', PINS['operation.py'])
    observer = module(bodies[PACKET + '/runtime_preflight.py'], packet_root / PACKET / 'runtime_preflight.py',
                      PINS['runtime_preflight.py'])
    engine = owner.load_selected(source)  # read-only load/CHECK; never a session or provider call
    clone_alias_selection(engine)
    alias_opening = observer.capture(engine.B, CLONE_ALIAS)
    runtime = observer.public(observer.observe(engine))
    require_runtime_bookends(runtime)
    alias_closing = observer.capture(engine.B, CLONE_ALIAS)
    clone_alias_selection(engine)
    alias = public_clone_alias(observer, clone_alias_compare(observer, alias_opening, alias_closing))
    closing_facts, closing_release = reader.capture_facts(budget)
    closing_tools = {name: reader.observe_tool(Path('/usr/bin') / name, budget, (Path('/usr'),))
                     for name in reader.TOOLS}
    closing_source = source_census(reader, source, manifest, budget)
    need(closing_facts == facts and closing_release == release and closing_tools == tools
         and reader.read_boot_identity(budget) == boot and closing_source == opening_source, 'BOOKENDS_CHANGED')
    for row in (*held.values(), release): reader.close_file(row)
    for row in tools.values(): reader.close_tool(row)
    clone_alias_selection(engine); need(context(os.environ) == ctx, 'CONTEXT_CHANGED'); budget.check()
    value = dict(schema='dg16.host-rollover-observation.v3', authority='NONE', status='CAPTURED_UNQUALIFIED',
        context=ctx, allowed_image_versions=list(ALLOWED_IMAGES), observed_image_version=facts['image_version'],
        requested_image_observed=facts['image_version'] in ALLOWED_IMAGES,
        facts=facts, boot_identity_sha256=sha(boot), os_release=release, tools=tools,
        prior_finite_profile_policy_sha256=sha(encode(baseline)),
        profile_comparison=reader.compare_profile(facts, {'profiles': baseline}),
        core_tool_comparison={name: {'observed_sha256': tools[name].get('sha256'),
            'matches_profile_ids': [row['id'] for row in baseline
                if tools[name].get('available') and tools[name]['sha256'] == row['core_tool_sha256'][name]]}
            for name in ('python3.12', 'git', 'bwrap')},
        runtime_selectors=runtime, git_clone_alias=alias, source=dict(commit=SOURCE, tree=TREE, opening=opening_source, closing=closing_source),
        executing_body_pins=relative_pins, opening_unix_ns=started, closing_unix_ns=time.time_ns(),
        limits=dict(deadline_seconds=DEADLINE_SECONDS, cpu_seconds=60, address_space_bytes=MEMORY_BYTES,
            maximum_profile_and_source_read_bytes=PROFILE_AND_SOURCE_READ_BYTES,
            actual_profile_and_source_read_bytes=budget.used, runtime_selector_count=12,
            runtime_capture_count=24, clone_alias_selector_count=1, clone_alias_capture_count=2,
            total_selector_count=13, total_capture_count=26,
            maximum_runtime_selector_bytes=observer.MAX_FILE_BYTES,
            maximum_runtime_capture_bytes=26 * observer.MAX_FILE_BYTES,
            source_owner_maximum_member_bytes=1024**2, source_owner_read_bytes_metered=False,
            maximum_open_files=64, maximum_output_file_bytes=MAX_OUTPUT, maximum_public_bytes=MAX_OUTPUT),
        closing_unchanged=True, automatic_adoption=False, commands_executed=[], observer_network_calls=0,
        provider_setup=False, native_execution=False, private_inputs_read=False, original_awards=[])
    raw = encode(value); need(len(raw) <= MAX_OUTPUT, 'OUTPUT_BOUND')
    sys.stdout.buffer.write(raw); sys.stdout.buffer.flush(); signal.alarm(0)
    return 0


if __name__ == '__main__':
    try:
        rc = main()
    except BaseException as exc:
        known = type(exc) in (Refusal, Deadline) and len(exc.args) == 1 and type(exc.args[0]) is str \
                and re.fullmatch('[A-Z0-9_]{1,64}', exc.args[0]) is not None
        value = dict(schema='dg16.host-rollover-observation-refusal.v1', authority='NONE', status='REFUSED',
                     code=exc.args[0] if known else 'UNCLASSIFIED_OBSERVATION_REFUSAL',
                     automatic_adoption=False, original_awards=[])
        sys.stdout.buffer.write(encode(value)); rc = 1
    raise SystemExit(rc)
