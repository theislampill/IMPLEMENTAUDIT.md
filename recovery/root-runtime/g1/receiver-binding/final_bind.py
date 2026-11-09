"""Fresh current04 public receiver binding; no issuer or effect interfaces.

Uses the actual fine-grained current04 phase, independent review and root
offline decision. Historical paths and modes are evidence data, not local
runtime prerequisites. Output is a relocatable source candidate, not a seal.
"""
import ast
import hashlib
import json
import os
from pathlib import Path
import sys
from physical_io import read_file

BASE = Path(__file__).resolve().parent
PHASE_SHA = '7a391c1c74329b1298349a85d3df25013707d0eb09044cf8583b3ea8bc9a038c'
TREE = '8390375505282e602759c7976b6bca82a44d5737'
SOURCE = '7e2b00b3a2a16fc6033a5eabe4fc795f6249366f'
SOURCE_TREE = '6d3f972a424583f9d3d56d8bfd9ae11cf36ecf6e'
CORE = 'tree/qualification/dg16-r5-g1-hosted-episode/'


def need(value, code):
    if not value:
        raise ValueError(code)


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)+'\n').encode()


def desc(raw):
    return dict(bytes=len(raw), sha256=hashlib.sha256(raw).hexdigest())


def parse(raw):
    def pairs(rows):
        out = {}
        for k, v in rows:
            need(k not in out, 'DUPLICATE_KEY')
            out[k] = v
        return out
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: need(False, 'NONFINITE_JSON'))


def body(row):
    need(type(row) is dict and set(row) == {'path','bytes','sha256'}, 'EXACT_DESCRIPTOR')
    raw = read_file(row['path'], 32*1024**2)
    need(desc(raw) == {k:row[k] for k in ('bytes','sha256')}, 'DESCRIPTOR_CHANGED')
    return raw


def assign(raw, name, value):
    text = raw.decode()
    nodes = [n for n in ast.parse(text).body if isinstance(n, ast.Assign)
             and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)
             and n.targets[0].id == name]
    need(len(nodes) == 1, 'UNIQUE_SOURCE_PIN')
    lines = text.splitlines(True)
    n = nodes[0]
    lines[n.lineno-1:n.end_lineno] = [name+' = '+repr(value)+'\n']
    return ''.join(lines).encode()


def collect(actual):
    fields = {'schema','phase','phase_root','host_review','root_offline_receiving',
              'export_adoption','export_review','root_transport_review_receiving'}
    need(type(actual) is dict and set(actual) == fields and
         actual['schema'] == 'dg16.current04-public-receiver-binding-inputs.v1', 'BINDING_FIELDS')
    raw_phase = body(actual['phase'])
    need(desc(raw_phase)['sha256'] == PHASE_SHA, 'EXACT_CURRENT04_PHASE')
    phase = parse(raw_phase)
    need(phase['phase'] == 'finish', 'FINISHED_PHASE_REQUIRED')
    phase_root = Path(actual['phase_root'])
    need(phase_root == Path(actual['phase']['path']).parent, 'PHASE_ROOT_JOIN')
    need({p.relative_to(phase_root).as_posix() for p in phase_root.rglob('*') if p.is_file()}
         == set(phase['members']) | {'PHASE.json'}, 'EXACT_PHASE_POPULATION')
    out = {'phase/PHASE.json':raw_phase}
    for name, pin in phase['members'].items():
        need(not Path(name).is_absolute() and '..' not in Path(name).parts, 'PHASE_MEMBER_PATH')
        raw = read_file(phase_root/name, 32*1024**2)
        need(desc(raw) == pin, 'PHASE_MEMBER_CHANGED')
        out['phase/'+name] = raw
    # These are original actual records, never newly authored decisions.
    evidence = {n:body(actual[n]) for n in fields - {'schema','phase','phase_root'}}
    review = parse(evidence['host_review'])
    need(review['schema'] == 'dg16.g1-current04-whole-host-source-independent-receiving.v1'
         and review['review_completion'] == 'COMPLETE'
         and review['disposition'] == 'ACCEPT_EXACT_CURRENT04_WHOLE_HOST_SOURCE_FOR_ROOT_DECISION_ONLY'
         and review['blocking_source_findings'] == [] and review['original_awards'] == [],
         'ACTUAL_CURRENT04_INDEPENDENT_REVIEW')
    subject = review['exact_subject']
    need(subject['finish_phase_sha256'] == PHASE_SHA and subject['expected_git_tree'] == TREE
         and subject['sole_parent'] == SOURCE and subject['run_sha256'] == desc(out['phase/'+CORE+'run.py'])['sha256'],
         'INDEPENDENT_EXACT_SUBJECT')
    root = parse(evidence['root_offline_receiving'])
    need(root['schema'] == 'dg16.current04.actual-root-offline-host-receiving.v1'
         and root['actor'] == '/root' and root['state'] == 'PASS_EXACT_PURE_REQUEST_INTEGRITY'
         and root['decision'] == 'ACCEPT_CURRENT04_FINISHED_WHOLE_HOST_SOURCE_AT_COMPOSITION_SCOPE'
         and root['source_commit'] == SOURCE and root['source_tree'] == SOURCE_TREE
         and root['phase_sha256'] == PHASE_SHA and root['expected_tree'] == TREE
         and root['sole_parent'] == SOURCE and root['effect_grant'] is False
         and root['original_awards'] == [], 'ACTUAL_ROOT_OFFLINE_RECEIVING')
    need({k:root['actual_independent_final'][k] for k in ('bytes','sha256')} == desc(evidence['host_review'])
         and {k:root['phase'][k] for k in ('bytes','sha256')} == desc(raw_phase), 'ROOT_REVIEW_PHASE_JOIN')
    adoption = parse(evidence['export_adoption'])
    need(adoption['schema'] == 'dg16.current03-export-repair-root-adoption.v1'
         and adoption['state'] == 'EXACT_EXPORT_OWNER_DELTA_ADOPTED_AS_FUTURE_SOURCE_INPUT'
         and adoption['provider_effect_grant'] is False and adoption['original_awards'] == []
         and {k:adoption['review_final'][k] for k in ('bytes','sha256')} == desc(evidence['export_review']),
         'EXACT_FINE_GRAINED_EXPORT_ADOPTION')
    transport = parse(evidence['root_transport_review_receiving'])
    need(transport['schema'] == 'dg16.root-receiver-r1-review-root-receiving.v1'
         and transport['actor'] == '/root'
         and transport['status'] == 'ACCEPT_EXACT_ROOT_TRANSPORT_COMPONENT_REVIEW'
         and transport['effect_grant'] is False and transport['original_awards'] == [],
         'ACTUAL_RETAINED_TRANSPORT_REVIEW')
    for name, raw in evidence.items():
        out['evidence/'+name+'.json'] = raw
    return out


def compose(actual):
    out = collect(actual)
    baseline = read_file(BASE/'baseline/receiver.py')
    need(desc(baseline)['sha256'] == '0298666f31eae09b15aa941a74929794a35a96fd45499e550f254634ec8363a4',
         'RETAINED_RECEIVER_CHANGED')
    source = baseline.decode()
    # Correct only physical/source binding. Every receipt/provider/ZIP/control
    # semantic function remains byte-identical as an AST to the retained owner.
    start = source.index('def read(path,maximum=MAX_RESULT):')
    end = source.index('\nclass Sources:', start)
    source = source[:start] + 'def read(path,maximum=MAX_RESULT):\n    return read_file(path,maximum)\n' + source[end:]
    physical_source = read_file(BASE/'physical_io.py')
    physical_loader = ("\n_physical=types.ModuleType('fixed_current04_physical_io')\n"
        "exec(compile("+repr(physical_source)+",'<fixed-current04-physical-io>','exec'),_physical.__dict__)\n"
        "read_file=_physical.read_file\n")
    source = source.replace('import zipfile\n', 'import zipfile\n'+physical_loader)
    start = source.index("        for name in ('phase','author_seal'")
    end = source.index('        members=self.phase', start)
    source = source[:start] + '''        for row in [self.sources['phase'],self.sources['root_broker'],*self.sources['qualification_inputs'].values()]:
            need(desc(read(self.local(row['path']),32*1024**2))=={k:row[k] for k in ('bytes','sha256')},'BOUND_SOURCE_CHANGED')
        self.root=self.local(self.sources['phase_root']);self.phase=parse(read(self.root/'PHASE.json'))
''' + source[end:]
    source = source.replace('    def body(self,path):', '''    def local(self,path):
        need(type(path) is str and not Path(path).is_absolute() and not Path(path).drive and '..' not in Path(path).parts,'LOCAL_SOURCE_PATH')
        value=LANE/path;need(value.resolve()==value,'LOCAL_SOURCE_ALIAS');return value
    def body(self,path):''')
    source = source.replace("Path(self.sources['root_broker']['path'])", "self.local(self.sources['root_broker']['path'])")
    source = source.replace("m.__file__=self.sources['root_broker']['path'] if name=='tool_broker'", "m.__file__=str(self.local(self.sources['root_broker']['path'])) if name=='tool_broker'")
    source = source.replace("            if n in local:need(level==0,'RELATIVE_DEPENDENCY_REFUSED');return self.module(n)",
        "            if n in local:need(level==0,'RELATIVE_DEPENDENCY_REFUSED');return self.module(n)\n"
        "            if n=='resource' and os.name=='nt':raise Refusal('POSIX_RESOURCE_REQUIRED_FOR_WHOLE_HOST_MODULE')")
    # Whole run.py cannot import resource on Windows. Public validators are
    # selected unchanged AST definitions below; no pretend resource API exists.
    source = source.replace("        exec(compile(raw,m.__file__,'exec'),m.__dict__)",
        "        if name=='run' and os.name=='nt':raw=windows_public_run(raw)\n"
        "        exec(compile(raw,m.__file__,'exec'),m.__dict__)\n"
        "        if name=='g3_receiving':m.read_file=read")
    source = source.replace('class Sources:', '''def windows_public_run(raw):
    tree=ast.parse(raw)
    # Data-only validator closure. No actual host/lifecycle entry is exported.
    allowed={'need','canonical','digest','parse_json','integer','hash_value',
             'validate_transport','validate_failure_files','validated_effects','validate_nss_effect'}
    nodes=[]
    for node in tree.body:
        if isinstance(node,ast.Import):
            names=[x for x in node.names if x.name not in ('resource','ctypes')]
            if names:nodes.append(ast.Import(names=names))
        elif isinstance(node,ast.ImportFrom):nodes.append(node)
        elif isinstance(node,(ast.Assign,ast.AnnAssign,ast.ClassDef)):nodes.append(node)
        elif isinstance(node,ast.FunctionDef) and node.name in allowed:nodes.append(node)
    return compile(ast.fix_missing_locations(ast.Module(body=nodes,type_ignores=[])),'<current04-public-run-validators>','exec')

class Sources:''')
    # compile() accepts the code object already selected by the Windows view.
    source = source.replace("exec(compile(raw,m.__file__,'exec'),m.__dict__)",
        "exec(raw if isinstance(raw,types.CodeType) else compile(raw,m.__file__,'exec'),m.__dict__)")
    # Private POSIX journal remains the original owner; refuse before mkdir on
    # Windows instead of pretending NTFS permission bits implement 0700/0600.
    source = source.replace('        self.path=Path(path);self.s=s;', "        need(os.name=='posix','POSIX_PRIVATE_JOURNAL_REQUIRED')\n        self.path=Path(path);self.s=s;")
    source = source.replace("        s.context(ctx);need(phase in PHASES,'FIXED_PHASE');p=Path(path);", "        need(os.name=='posix','POSIX_PRIVATE_JOURNAL_REQUIRED')\n        s.context(ctx);need(phase in PHASES,'FIXED_PHASE');p=Path(path);")
    for name in ('tool_broker.py','precore_projection_snapshot.py'):
        out['author/'+name] = read_file(BASE/'baseline'/name)
    out['author/physical_io.py'] = read_file(BASE/'physical_io.py')
    evidence = {name:dict(path=name,**desc(raw)) for name,raw in out.items() if name.startswith('evidence/')}
    sources = dict(schema='dg16.current04-public-receiver-sources.v1',authority='NONE',
        phase_root='phase',phase=dict(path='phase/PHASE.json',**desc(out['phase/PHASE.json'])),
        root_broker=dict(path='author/tool_broker.py',**desc(out['author/tool_broker.py'])),
        qualification_inputs=evidence,expected_tree=TREE,original_awards=[])
    out['SOURCES.json'] = encode(sources)
    out['author/receiver.py'] = assign(source.encode(),'SOURCE_SHA',desc(out['SOURCES.json'])['sha256'])
    resolver = read_file(BASE/'baseline/resolve_artifact.py')
    out['author/resolve_artifact.py'] = assign(resolver,'RECEIVER_SHA',desc(out['author/receiver.py'])['sha256'])
    return out


def build(actual, destination):
    files = compose(actual)
    destination = Path(destination)
    need(destination.is_absolute() and destination.parent.resolve()==destination.parent
         and destination.is_relative_to(BASE) and not destination.exists(), 'FRESH_OWNED_OUTPUT')
    destination.mkdir()
    for name, raw in files.items():
        p = destination/name
        p.parent.mkdir(parents=True,exist_ok=True)
        with p.open('xb') as f:
            f.write(raw)
            f.flush()
            os.fsync(f.fileno())
        need(read_file(p,32*1024**2)==raw,'OUTPUT_READBACK')
    return dict(schema='dg16.current04-public-receiver-candidate.v1',authority='NONE',
        files={n:desc(b) for n,b in files.items()},semantic_receipt_owner='RETAINED_UNCHANGED',
        source_physical_delta='EXPLICIT_CURRENT04_PORTABLE_BINDING_AND_BOUNDED_WINDOWS_READ',
        actual_review_or_author_seal_issued=False,effect_grant=False,original_awards=[])


if __name__ == '__main__':
    need(len(sys.argv)==3,'ACTUAL_INPUTS_AND_FRESH_OUTPUT')
    print(json.dumps(build(parse(read_file(Path(sys.argv[1]))),Path(sys.argv[2])),sort_keys=True))
