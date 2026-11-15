"""Rebuild the inert DG17 driver bundle at an explicit final author directory.

No native operation, grant, account access, home setup or acceptance is performed.
Historical author inputs remain unchanged. Windows paths retain Windows semantics
when preparing on POSIX. Unobserved host inputs remain unresolved dependencies.
"""
import argparse
import ast
import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path, PureWindowsPath
import stat
import subprocess
import sys

HERE = Path(__file__).absolute().parent
BASE = HERE.parent.parent / 'dg17-next-release' / 'author'
MEMBERS = {'OPERATION_A.json', 'PROFILE.toml', 'bind_stage_b.py', 'native_rpc.py',
           'parent_launch_a.py', 'parent_launch_b.py', 'positive_hook_constructor.py',
           'source_setup.py', 'stage_a.py', 'stage_b.py'}
OLD_BASELINE = 'b0fcb565d1c81900899181d4607e2f3a8cc621a6'


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + '\n').encode()


def physical(path, *, directory=False):
    path = Path(path).absolute()
    for member in (path, *path.parents):
        if member.exists() or member.is_symlink():
            info = member.lstat()
            if stat.S_ISLNK(info.st_mode) or getattr(info, 'st_file_attributes', 0) & 1024:
                raise ValueError('Aliased or reparse input/output path: ' + str(member))
    if directory and not path.is_dir():
        raise ValueError('Missing input directory: ' + str(path))
    return path


def pin(path):
    path = physical(path)
    before = path.lstat()
    if not stat.S_ISREG(before.st_mode) or before.st_nlink != 1:
        raise ValueError('Non-regular or multiply linked input: ' + str(path))
    identity = lambda s: (s.st_dev, s.st_ino, s.st_mode, s.st_nlink, s.st_size,
                          s.st_mtime_ns, s.st_ctime_ns)
    with path.open('rb') as stream:
        if identity(before) != identity(os.fstat(stream.fileno())):
            raise ValueError('Input identity changed before read')
        raw = stream.read(before.st_size + 1)
        after = os.fstat(stream.fileno())
    if identity(before) != identity(after) or identity(after) != identity(path.lstat()):
        raise ValueError('Input identity changed during read')
    if len(raw) != before.st_size:
        raise ValueError('Input length changed')
    return {'path': str(path), 'bytes': len(raw), 'sha256': sha(raw)}


def foreign_path(value):
    return PureWindowsPath(value) if PureWindowsPath(value).is_absolute() else Path(value)


def relative(value, parent):
    try:
        return foreign_path(value).relative_to(foreign_path(parent))
    except ValueError:
        return None


def replace_once(raw, old, new, label):
    if raw.count(old.encode()) != 1:
        raise ValueError('Expected exactly one pinned literal: ' + label)
    return raw.replace(old.encode(), new.encode())


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()


def make_stage_b(raw):
    spec = importlib.util.spec_from_file_location('dg17_acl_generator', HERE / 'make_acl_stage_b.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.render(raw)


def make_parent_a(raw):
    text = raw.decode('utf-8')
    nodes = [node for node in ast.parse(text).body
             if isinstance(node, ast.FunctionDef) and node.name == 'capture']
    if len(nodes) != 1:
        raise ValueError('Exact parent capture owner required')
    capture = ast.get_source_segment(text, nodes[0])
    prefix = 'import hashlib,os,stat,sys;from pathlib import Path\n' + capture + '\n'
    helper = ("CAPTURE_LOADER=" + repr(prefix) + "\n"
              "def driver_loader(driver_path,argv):\n"
              " return CAPTURE_LOADER+'raw=capture('+repr(str(driver_path))+','+repr(DRIVER_SHA)+',keep=True)\\nsys.argv='+repr(argv)+'\\nexec(compile(raw,'+repr(str(driver_path))+\",'exec'),{'__name__':'__main__','__file__':\"+repr(str(driver_path))+'})'\n\n")
    if text.count('def main():\n') != 1:
        raise ValueError('Exact parent main required')
    text = text.replace('def main():\n', helper + 'def main():\n')
    lines = text.splitlines(keepends=True)
    encoded = [i for i, line in enumerate(lines) if line.startswith(' encoded=base64.b64encode(driver)')]
    if len(encoded) != 1 or not lines[encoded[0] + 1].startswith(' loader='):
        raise ValueError('Exact predecessor encoded command required')
    lines[encoded[0]:encoded[0] + 2] = [' loader=driver_loader(driver_path,argv)\n']
    writes = [i for i, line in enumerate(lines) if line.startswith(' save(window,')]
    if len(writes) != 1:
        raise ValueError('Exact episode-window write required')
    window_write = lines.pop(writes[0])
    bounds = [i for i, line in enumerate(lines)
              if line.startswith(' assert len(subprocess.list2cmdline(command))<30000')]
    if len(bounds) != 1:
        raise ValueError('Original command-size bound required')
    lines.insert(bounds[0] + 1, window_write)
    result = ''.join(lines).encode('utf-8')
    compile(result, 'parent_launch_a.py', 'exec')
    return result


def build(base, output, source, package=None):
    base, source = physical(base, directory=True), physical(source, directory=True)
    output = physical(output)
    if output.exists() or output.is_relative_to(base) or base.is_relative_to(output):
        raise ValueError('Fresh, disjoint output author directory required')
    if (output.parent / 'PINS.json').exists():
        raise ValueError('Output manifest already exists')
    if {p.name for p in base.iterdir() if p.name != '__pycache__'} != MEMBERS:
        raise ValueError('Unexpected base author population')
    original = {name: (base / name).read_bytes() for name in MEMBERS}
    before = {name: sha(raw) for name, raw in original.items()}
    op = json.loads(original['OPERATION_A.json'])
    old_op = copy.deepcopy(op)
    if encoded(op) != original['OPERATION_A.json']:
        raise ValueError('Noncanonical historical operation')
    branch = git(source, 'branch', '--show-current')
    if not branch:
        raise ValueError('A named source branch is required by the existing clone driver')
    head, tree = git(source, 'rev-parse', 'HEAD'), git(source, 'rev-parse', 'HEAD^{tree}')
    old_author = str(foreign_path(op['rpc_module']['path']).parent)
    old_source = op['local_plugin_selection']['source_root']
    source_rebindings = {}
    for item in [*op['readset'], op['binding_owner']]:
        rel = relative(item['path'], old_source)
        if rel is not None:
            current = pin(source.joinpath(*rel.parts))
            committed = subprocess.check_output(['git', '-C', str(source), 'show', 'HEAD:' + '/'.join(rel.parts)])
            if sha(committed) != current['sha256']:
                raise ValueError('Runtime source differs from selected HEAD: ' + '/'.join(rel.parts))
            source_rebindings[item['path']] = current
    bodies = dict(original)
    bodies['stage_b.py'] = make_stage_b(original['stage_b.py'])
    bodies['parent_launch_a.py'] = make_parent_a(original['parent_launch_a.py'])
    bodies['stage_a.py'] = replace_once(
        original['stage_a.py'], "'Baseline ref':'" + OLD_BASELINE + "'",
        "'Baseline ref':head", 'Stage A current baseline')
    constructor = bodies['positive_hook_constructor.py']
    for key, old_pin in [('binding_owner', op['binding_owner'])] + [
            (key, next(x for x in op['readset'] if foreign_path(x['path']).name == name))
            for key, name in [('handler', 'host-stop-interlock.py'),
                              ('validator', 'validate-run-root.sh'),
                              ('custody', 'canonical_custody.py')]]:
        new_pin = source_rebindings[old_pin['path']]
        constructor = replace_once(constructor, key + "='" + old_pin['sha256'] + "'",
                                   key + "='" + new_pin['sha256'] + "'", key)
    bodies['positive_hook_constructor.py'] = constructor
    bodies['parent_launch_b.py'] = replace_once(
        bodies['parent_launch_b.py'], before['stage_b.py'], sha(bodies['stage_b.py']), 'B driver')
    bodies['parent_launch_a.py'] = replace_once(
        bodies['parent_launch_a.py'], before['stage_a.py'], sha(bodies['stage_a.py']), 'A driver')

    def author_pin(name):
        return {'path': str(output / name), 'bytes': len(bodies[name]), 'sha256': sha(bodies[name])}

    package_pin = pin(package) if package is not None else None
    if package_pin:
        # Delegate population, identity, budget and parity to the existing owner.
        # This remains package evidence; it is not installation or activation.
        subprocess.run([sys.executable, '-B', str(source / 'scripts/package-contract.py'),
                        '--repo-root', str(source), '--verify-artifact', 'canonical_plugin',
                        str(Path(package).absolute()), '--require-clean-source'], check=True)

    def repin(item):
        rel = relative(item['path'], old_author)
        if rel is not None:
            if len(rel.parts) != 1 or rel.name in {'OPERATION_A.json', 'parent_launch_a.py', 'bind_stage_b.py'}:
                raise ValueError('Unexpected cyclic or nested author pin')
            return author_pin(rel.name)
        if item['path'] in source_rebindings:
            return source_rebindings[item['path']]
        if package_pin and item['path'] == old_op['package']['path']:
            return package_pin
        return copy.deepcopy(item)

    op['readset'] = [repin(x) for x in op['readset']]
    for key in ['rpc_module', 'constructor', 'binding_owner', 'package']:
        op[key] = repin(op[key])
    if not any(item['path'] == op['binding_owner']['path'] for item in op['readset']):
        op['readset'].append(copy.deepcopy(op['binding_owner']))
    op.update(source_worktree=str(source), source_head=head, source_tree=tree, branch=branch)
    op['source_pins'] = {name: pin(source / name)['sha256'] for name in op['source_pins']}
    op['source_pins']['skills/implementaudit/scripts/host-session-binding.py'] = op['binding_owner']['sha256']
    op['native_skill_pins'] = {name: pin(source / 'skills' / name / 'SKILL.md')['sha256']
                             for name in op['native_skill_pins']}
    op['local_plugin_selection']['source_root'] = str(source)
    op['local_plugin_selection']['marketplace_file'] = str(source / '.claude-plugin/marketplace.json')
    unresolved = []
    for item in op['readset']:
        if relative(item['path'], str(output)) is not None:
            continue
        if PureWindowsPath(item['path']).is_absolute() and os.name != 'nt':
            unresolved.append({'path': item['path'], 'reason': 'WINDOWS_HOST_INPUT_NOT_OBSERVED'})
            continue
        try:
            observed = pin(item['path'])
        except (OSError, ValueError):
            unresolved.append({'path': item['path'], 'reason': 'EXACT_INPUT_NOT_OBSERVED'})
        else:
            if any(observed[k] != item[k] for k in ['bytes', 'sha256']):
                unresolved.append({'path': item['path'], 'reason': 'EXACT_INPUT_PIN_MISMATCH'})
    op['status'] = 'INERT_SOURCE_REBUILD_NO_NATIVE_ADMISSION'
    op['episode_successor'] += (' Source-only rebuild: final author paths and complete B2 source pins '
                                'forwarded; Stage A baseline follows selected HEAD; Windows store '
                                'DACL admits only the authorized user and SYSTEM. Historical carrier '
                                'and issuer are retained as inputs, never a fresh grant. Stage A parent '
                                'uses the existing exact-digest capture owner inside the child, avoiding '
                                'a base64 command that exceeds the unchanged 30000-character bound.')
    op['preparation'] = {
        'authority': 'NONE', 'native_admission': False,
        'historical_operation_sha256': before['OPERATION_A.json'],
        'unverified_inputs': unresolved,
        'required_before_native': [
            'Rebuild at the actual final Windows location and read every exact host input back',
            'Reconcile current issuer and fresh written owner grant naming this exact record',
            'Confirm two genuine Codex turns, independent post-A receiving and the unchanged shared window',
            'Re-run Windows custody controls including the stricter Administrators refusal',
            'Keep all 14 custody differences UNKNOWN; no replay or implied receiving'],
    }
    if op['limits'] != old_op['limits']:
        raise ValueError('Original limits changed')
    bodies['OPERATION_A.json'] = encoded(op)
    operation_sha = sha(bodies['OPERATION_A.json'])
    for name in ['parent_launch_a.py', 'bind_stage_b.py']:
        bodies[name] = replace_once(bodies[name], before['OPERATION_A.json'], operation_sha, name)
    for name, raw in bodies.items():
        if name.endswith('.py'):
            compile(raw, name, 'exec')
    for name, expected in {
            'parent_launch_a.py': {'OP_SHA': operation_sha, 'DRIVER_SHA': sha(bodies['stage_a.py']),
                                   'RPC_SHA': sha(bodies['native_rpc.py'])},
            'parent_launch_b.py': {'DRIVER_SHA': sha(bodies['stage_b.py'])},
            'bind_stage_b.py': {'A_SHA': operation_sha}}.items():
        constants = {node.targets[0].id: ast.literal_eval(node.value)
                     for node in ast.parse(bodies[name]).body if isinstance(node, ast.Assign)
                     and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name)
                     and node.targets[0].id in expected}
        if constants != expected:
            raise ValueError('Unclosed generated command pins: ' + name)
    for item in op['readset']:
        rel = relative(item['path'], str(output))
        if rel is not None and item != author_pin(rel.name):
            raise ValueError('Unclosed author pin: ' + rel.name)
    if {name: sha((base / name).read_bytes()) for name in MEMBERS} != before:
        raise ValueError('Historical author inputs changed')
    output.mkdir(parents=True, exist_ok=False)
    for name in sorted(bodies):
        with (output / name).open('xb') as stream:
            stream.write(bodies[name])
    manifest = {
        'authority': 'NONE - source-only preparation, not native evidence',
        'author_dir': str(output), 'base_author_dir': str(base),
        'source_head': head, 'source_tree': tree,
        'operation_A_sha256': operation_sha, 'operation_A_bytes': len(bodies['OPERATION_A.json']),
        'previous_operation_A_sha256': before['OPERATION_A.json'],
        'limits_unchanged': True, 'unverified_input_count': len(unresolved),
        'native_admission': False, 'original14_custody_unknown_differences': 14,
        'files': {name: dict(pin(output / name), previous_sha256=before[name]) for name in sorted(bodies)},
    }
    with (output.parent / 'PINS.json').open('xb') as stream:
        stream.write(encoded(manifest))
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base-author', type=Path, default=BASE)
    parser.add_argument('--output-author', type=Path, required=True)
    parser.add_argument('--source-root', type=Path, required=True)
    parser.add_argument('--package', type=Path)
    args = parser.parse_args()
    result = build(args.base_author, args.output_author, args.source_root, args.package)
    print(json.dumps({k: v for k, v in result.items() if k != 'files'}, indent=2))


if __name__ == '__main__':
    main()
