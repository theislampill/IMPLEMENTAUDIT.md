"""Compute registry mapping/command stream exactly as pair_driver.py MAPPING phase does (no verifier run)."""
import hashlib, importlib.util, json, sys
from pathlib import Path
repo = Path(sys.argv[1]).resolve()
path = repo / 'scripts/qualify-work-graph-verifier.py'
spec = importlib.util.spec_from_file_location('hosted_full_pair_owner', path)
owner = importlib.util.module_from_spec(spec); sys.modules[spec.name] = owner; spec.loader.exec_module(owner)
registry = (repo / 'scripts/verify-package.sh').read_bytes()
registered = owner.WG.verifier_registered_tests_v1(registry)
physical = sorted(p.relative_to(repo).as_posix() for p in (repo / 'tests').glob('*.test.sh'))
environment = owner.environment_identity(child_resolution=True)
mapping = owner.WG.compile_verifier_graph_v1(registry, physical, environment)
stream = owner.WG.verifier_command_stream_v1(mapping, registry)
reassembled = b''.join(n['source'].encode() for n in mapping['nodes']) == registry
print(json.dumps({'owner_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
  'registry_sha256': hashlib.sha256(registry).hexdigest(), 'registered_tests': len(registered),
  'registered_equals_physical': registered == physical, 'mapped_nodes': len(mapping['nodes']),
  'exact_registry_reassembly': reassembled, 'command_stream_sha256': hashlib.sha256(stream).hexdigest(),
  'command_stream_bytes': len(stream)}, indent=1))
