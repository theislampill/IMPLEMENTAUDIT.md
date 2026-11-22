"""Read-only current-Pro receiving and unissued preparation interfaces.

This loads only exact selected validator declarations, not any full original
module. It cannot call model-side tools, issue a grant, start a sender, encrypt
private inputs, publish a control or invoke a protected consumer.
"""
from __future__ import annotations
import argparse
import ast
import base64
import datetime
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import secrets
import select
import stat
import sys
import termios
import time
import types
import zipfile

INDEX_SHA256 = '58a831b74aec61df5f159ca72cc5c54bc2d50c13f0aea78651bdfe48f0d8e983'
CORE = 'tree/qualification/dg16-r5-g1-hosted-episode/'
ENTRY = 'tree/qualification/dg16-r5-g1-hosted-entry/'
MAX_SOURCE_FILE = 1024 * 1024
MAX_INPUT = 8 * 1024 * 1024


def need(value, code):
    if not value:
        raise ValueError(code)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def desc(raw):
    return dict(bytes=len(raw), sha256=sha(raw))


def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False) + '\n').encode()


def parse(raw, maximum=MAX_INPUT):
    need(type(raw) is bytes and 0 < len(raw) <= maximum, 'BOUNDED_JSON_BYTES')
    def pairs(items):
        result = {}
        for key, value in items:
            need(key not in result, 'DUPLICATE_KEY')
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs,
                      parse_constant=lambda _: need(False, 'NONFINITE_JSON'))


def read_pinned(path, expected=None, maximum=MAX_SOURCE_FILE):
    path = Path(path)
    need(path.is_absolute() and path.resolve(strict=True) == path, 'CANONICAL_INSTALLATION_PATH')
    need(not any(p.is_symlink() for p in path.parents), 'INSTALLATION_ANCESTOR_ALIAS')
    before = path.lstat()
    need(stat.S_ISREG(before.st_mode) and before.st_nlink == 1
         and before.st_uid == os.geteuid() and stat.S_IMODE(before.st_mode) in (0o400, 0o444)
         and 0 < before.st_size <= maximum, 'OWNED_READONLY_SOURCE_BODY')
    def mark(s):
        return (s.st_dev,s.st_ino,s.st_mode,s.st_nlink,s.st_uid,s.st_gid,s.st_size,s.st_mtime_ns,s.st_ctime_ns)
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC)
    try:
        need(mark(os.fstat(fd)) == mark(before) and not os.listxattr(fd), 'SOURCE_OPEN_CHANGED')
        raw = os.pread(fd, maximum + 1, 0)
        need(len(raw) == before.st_size and mark(os.fstat(fd)) == mark(before) == mark(path.lstat())
             and path.resolve(strict=True) == path, 'SOURCE_CLOSING_CHANGED')
    finally:
        os.close(fd)
    need(expected is None or encode(desc(raw)) == encode(expected), 'FIXED_SOURCE_PIN')
    return raw


class CurrentSources:
    """Relocatable exact installation; root path conveys no authority."""
    def __init__(self, root):
        self.root = Path(root).absolute()
        need(self.root.resolve(strict=True) == self.root and not self.root.is_symlink(), 'INSTALLATION_ALIAS')
        st = self.root.lstat()
        need(stat.S_ISDIR(st.st_mode) and st.st_uid == os.geteuid() and not st.st_mode & 0o022, 'INSTALLATION_DIRECTORY')
        raw = read_pinned(self.root / 'SOURCE_INDEX.json')
        need(sha(raw) == INDEX_SHA256, 'FIXED_CURRENT_SOURCE_INDEX')
        self.index = parse(raw)
        need(self.index['schema'] == 'g132.current-pro-fixed-source-index.v1'
             and self.index['state'] == 'UNISSUED' and self.index['authority'] == 'NONE'
             and self.index['runtime_adoption_issued'] is False, 'UNISSUED_SOURCE_SCOPE')
        actual = {p.relative_to(self.root).as_posix() for p in self.root.rglob('*') if p.is_file()}
        need(actual == set(self.index['files']) | {'SOURCE_INDEX.json'}, 'EXACT_INSTALLATION_POPULATION')
        need(not any(p.is_symlink() for p in self.root.rglob('*')), 'INSTALLATION_SYMLINK')
        for name in self.index['files']:
            self.file(name)
        self.identity = parse(self.file('HOST_IDENTITY_UNISSUED.json'))
        self.phase = parse(self.file('phase/PHASE.json'))
        need(self.identity['state'] == self.phase['state'] == 'UNISSUED', 'UNISSUED_IDENTITY_REQUIRED')
        need(set(self.phase['members']) == {p.removeprefix('phase/') for p in self.index['files'] if p.startswith('phase/tree/')}, 'EXACT_PHASE_POPULATION')
        for name, pin in self.phase['members'].items():
            need(encode(pin) == encode(desc(self.file('phase/' + name))), 'PHASE_BODY_JOIN')
        self._check_git_identity()
        self._modules = {}
        self._plan = parse(self.file('PURE_SOURCE_PLAN.json'))
        self.C = self.module('codec')
        self.P = self.module('policy')
        self.V = self.module('provider')
        self.B = self.module('broker')
        self.H = self.module('host_tools')
        self.G = self.module('g3')
        self.I = self.module('proof')
        self.R = self.module('run')
        self.receiver = self.module('receiver')
        self.issuer = self.module('issuer')
        self.binding_raw = self.body(CORE + 'carrier/CARRIER_COMPOSITION.json')
        self.binding = parse(self.binding_raw)
        self.input_index = parse(self.body(CORE + 'carrier/INPUT_INDEX.json'))
        self.binding['_binding_raw'] = self.binding_raw
        self.binding['_index'] = self.input_index
        # The original receiver calls this attribute `index` for the input census.
        self.source_index = self.index
        self.index = self.input_index
        self.anchor = {'public_manifest_sha256':sha(self.body(ENTRY+'PUBLIC_PACKET_MANIFEST.json')),
                       'bootstrap_admission_sha256':sha(self.body(ENTRY+'BOOTSTRAP_ADMISSION.json'))}
        self.sources = {'phase':desc(self.file('phase/PHASE.json'))}
        self.proof_pins = self.I.pins_contract(parse(self.body(CORE+'INDEPENDENT_PROOF_PINS.json')))
        self.scope_basis_raw = self.body(CORE+'ORIGINAL_SCOPE.json')
        self.scope_basis = parse(self.scope_basis_raw)
        need(self.proof_pins['consumer_sha256'] == sha(self.body(CORE+'proof_consumer.py'))
             and self.proof_pins['scope_module_sha256'] == sha(self.body(CORE+'g3_receiving.py'))
             and self.proof_pins['scope_sha256'] == sha(self.body(CORE+'ORIGINAL_SCOPE.json'))
             and self.proof_pins['adverse_sha256'] == sha(self.body(CORE+'ADVERSE_APPLICABILITY.json')), 'INDEPENDENT_SOURCE_JOIN')
        self.G.receive_exact_m4(self.retained_m4_bodies())
        author=parse(self.file('sender-author/AUTHOR_SOURCE_INDEX.json'))['members']
        need(len(author)==46,'EXACT_ORIGINAL_AUTHOR_SUBSET')
        self.templates={n.removeprefix('templates/'):self.file('sender-author/'+n) for n in author if n.startswith('templates/')}
        template_index=parse(self.file('sender-author/inputs/TEMPLATE_INDEX.json'))
        need(len(self.templates)==42 and encode({n:desc(v) for n,v in self.templates.items()})==encode(template_index),'EXACT_ORIGINAL_TEMPLATE_INDEX')
        self._checked_receivings = set()

    def file(self, name):
        path = PurePosixPath(name)
        need(type(name) is str and str(path) == name and not path.is_absolute() and '..' not in path.parts, 'FIXED_MEMBER_PATH')
        index = getattr(self, 'source_index', self.index)
        need(name in index['files'], 'FIXED_MEMBER_REQUIRED')
        return read_pinned(self.root / name, index['files'][name])

    def body(self, name):
        need(name in self.phase['members'], 'FIXED_PHASE_MEMBER')
        return self.file('phase/' + name)

    def retained_m4_bodies(self):
        names = ('M4_FINAL_CHECK.json','M4_INDEPENDENT_REPORT.md','M4_INDEPENDENT_RESULT.json','M4_ROOT_RECEIVING.json')
        return {n:self.body(CORE+'retained-m4/'+n) for n in names}

    def _check_git_identity(self):
        def oid(kind, raw):
            return hashlib.sha1(kind.encode()+b' '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        identity = self.identity
        raw = self.file('git-candidate/'+identity['commit']+'.commit')
        need(oid('commit',raw) == identity['commit'], 'PROSPECTIVE_COMMIT_BYTES')
        lines = raw.splitlines()
        need(lines[0] == ('tree '+identity['tree']).encode()
             and [l[7:].decode() for l in lines if l.startswith(b'parent ')] == [identity['parent']], 'PROSPECTIVE_TREE_PARENT')
        need(oid('tree',self.file('git-candidate/'+identity['tree']+'.tree')) == identity['tree'], 'PROSPECTIVE_TREE_BYTES')
        chain = ['301aeecde08ba6f169bc3cd837eae6f6ad068219','625f310d04cb5b5a1f02901cfdcf3c3815730a5e',
                 '8489ea6cc94dc4f7de8a722b3ac1949e04b0d1fb','2f6a96427a307dc57ed88664aeb8224918fe6bf5',
                 '434f12f038da9420f9addaf2fed7178e1e41e20f','e76a07b2bae7c945e5a9d529ed8cf9069f4c9064']
        need(identity['parent'] == chain[0], 'EXACT_NEW_SOURCE_PARENT')
        for number, commit in enumerate(chain):
            body = self.file('git-lineage/'+commit+'.commit')
            need(oid('commit',body) == commit, 'ANCESTOR_BODY')
            if number+1 < len(chain):
                need([l[7:].decode() for l in body.splitlines() if l.startswith(b'parent ')] == [chain[number+1]], 'EXACT_ANCESTRY')

    def host_commit(self, commit):
        need(type(commit) is dict and commit.get('sha') == self.identity['commit']
             and commit.get('tree',{}).get('sha') == self.identity['tree']
             and [p.get('sha') for p in commit.get('parents',[])] == [self.identity['parent']], 'EXACT_SELECTED_HOST_COMMIT_TREE_PARENT')
        return commit['sha']

    def context(self, ctx):
        self.P.context(ctx)
        for name in ('repository','branch','workflow_path','job_name'):
            need(type(ctx[name]) is type(self.identity[name]) and ctx[name] == self.identity[name], 'SELECTED_HOST_CONTEXT')
        need(ctx['workflow_commit'] == self.identity['commit'], 'SELECTED_HOST_COMMIT')
        return ctx

    def endpoint(self, ctx, artifact_id, kind):
        self.context(ctx)
        return self.B.endpoint(ctx, artifact_id, kind)

    def _profile_policy(self, binding, *, observe=False):
        need(observe is False, 'HOST_OBSERVATION_NOT_AVAILABLE_HERE')
        raw = self.body(CORE+'host_utility.py')
        need(encode(desc(raw)) == encode(binding['core_bodies']['host_utility.py']), 'HOST_PROFILE_CHANGED')
        return self.module('profile')

    def _run_module(self, name):
        if name == 'g3_receiving':
            return self.module('g3')
        need(name == 'nss_configuration', 'PURE_MODULE_ONLY')
        member = CORE + 'nss_configuration.py'
        raw = self.body(member)
        need(desc(raw) == self.phase['members'][member], 'PHASE_BODY_JOIN')
        try:
            tree = ast.parse(raw)
        except (ValueError, SyntaxError) as exc:
            raise ValueError('NSS_DATA_SOURCE') from exc

        fields = {'PHASES', 'REFUSALS'}
        bindings = {}
        for statement in tree.body:
            if isinstance(statement, ast.Assign) and len(statement.targets) == 1:
                target = statement.targets[0]
                if isinstance(target, ast.Name) and target.id in fields:
                    bindings[target.id] = statement
        need(bindings.keys() == fields, 'NSS_DATA_FIELDS')
        # An alternate binding must not compete with either simple declaration.
        for node in ast.walk(tree):
            if isinstance(node, ast.Name) and node.id in fields and isinstance(node.ctx, (ast.Store, ast.Del)):
                need(node is bindings[node.id].targets[0], 'NSS_DATA_BINDING')
            elif isinstance(node, ast.alias):
                need((node.asname or node.name.split('.')[0]) not in fields, 'NSS_DATA_BINDING')
            elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef, ast.ExceptHandler,
                                   ast.MatchAs, ast.MatchStar)):
                need(node.name not in fields, 'NSS_DATA_BINDING')
            elif isinstance(node, ast.MatchMapping):
                need(node.rest not in fields, 'NSS_DATA_BINDING')

        phases = bindings['PHASES'].value
        call = bindings['REFUSALS'].value
        need(isinstance(phases, ast.Tuple), 'NSS_DATA_PHASES')
        need(isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id == 'frozenset'
             and len(call.args) == 1 and not call.keywords and isinstance(call.args[0], ast.Set), 'NSS_DATA_REFUSALS')
        refusals = call.args[0]
        for collection in (phases, refusals):
            need(collection.elts and all(isinstance(item, ast.Constant) and type(item.value) is str and item.value
                                         for item in collection.elts), 'NSS_DATA_STRINGS')
            need(len({item.value for item in collection.elts}) == len(collection.elts), 'NSS_DATA_DUPLICATE_MEMBER')
        return types.SimpleNamespace(PHASES=ast.literal_eval(phases), REFUSALS=frozenset(ast.literal_eval(refusals)))

    def module(self, name, *, work_root=None, byte_reader=None):
        need(name in self._plan, 'FIXED_PURE_MODULE')
        if name not in ('pipeline','binder') and name in self._modules:return self._modules[name]
        raw = self.file('pure/'+name+'.py')
        plan = self._plan[name]
        need(desc(raw) == {'bytes':plan['projection_bytes'],'sha256':plan['projection_sha256']}, 'EXACT_PURE_PROJECTION')
        t = ast.parse(raw)
        need(all(isinstance(n,(ast.Assign,ast.FunctionDef,ast.ClassDef)) for n in t.body), 'DECLARATIONS_ONLY')
        need(not any(isinstance(n,(ast.Import,ast.ImportFrom)) for n in ast.walk(t)), 'NO_SOURCE_IMPORTS')
        namespace = dict(ast=ast,hashlib=hashlib,json=json,re=re,base64=base64,datetime=datetime,
                         io=io,zipfile=zipfile,stat=stat)
        if name == 'policy':namespace['C']=self.module('codec')
        if name in ('provider','broker','host_tools'):
            namespace['P']=self.module('policy')
        if name in ('broker','host_tools'):namespace['V']=self.module('provider')
        if name in ('provider','host_tools'):
            namespace['local_artifact_chronology']=lambda *a,**k:self.module('receiver').local_artifact_chronology(*a,**k)
        if name == 'profile':namespace.update(require=need,sha=sha)
        if name == 'host_tools':namespace['_profile_policy']=self._profile_policy
        if name == 'g3':namespace['current_original_scope_body']=lambda:self.body(CORE+'ORIGINAL_SCOPE.json')
        if name == 'run':
            namespace.update(load_module=self._run_module,
                             retained_m4_packet_bodies=self.retained_m4_bodies)
        if name == 'receiver':namespace['current_sender_requirements']=self.sender_requirements
        if name == 'compose':namespace.update(templates=lambda:dict(self.templates),compile=compile,W=self.module('workflow'))
        if name == 'assembler':namespace.update(C=self.module('compose'),Path=PurePosixPath)
        if name == 'late':namespace.update(PurePosixPath=PurePosixPath,current_dispatcher_derive=self.dispatcher_derive)
        if name == 'binder':
            need(callable(byte_reader),'EXPLICIT_BYTE_ONLY_DERIVER_READER')
            def fixed_read(path):
                name=str(path)
                for member in ('dispatcher_entry.py','dispatch.js'):
                    if name=='/fixed-original-dispatcher/'+member:
                        return self.file('operator/dispatcher-templates-02/'+member)
                return byte_reader(path)
            namespace.update(read=fixed_read,Path=PurePosixPath,BASE=PurePosixPath('/fixed-original-dispatcher'),compile=compile)
        if name == 'pipeline':
            base = self.work_root(work_root)
            namespace.update(os=os,Path=Path,time=time,BASE=base)
        module = types.SimpleNamespace()
        exec(compile(t,'<fixed-projection:'+name+'>','exec'),namespace)
        module.__dict__.update(namespace)
        if name not in ('pipeline','binder'):self._modules[name]=module
        return module

    def receive_public(self, phase, context, results, archive, note, previous=None, actual_root_raw=None):
        # Provider tools run model-side; this method only receives full bytes.
        self.context(context)
        if previous is not None:self._require_received(previous)
        got = self.receiver.receive(self,phase,context,results,archive,note,time.time_ns()//1000000,previous,actual_root_raw)
        self._checked_receivings.add(self.receiving_key(got))
        return got

    def receiving_key(self, received):
        need(type(received) is dict and set(received)=={'phase','context','files','receipt'}, 'EXACT_RECEIVING_FIELDS')
        need(type(received['files']) is dict and all(type(v) is bytes for v in received['files'].values()), 'EXACT_RECEIVED_PUBLIC_BYTES')
        return sha(encode(dict(phase=received['phase'],context=received['context'],receipt=received['receipt'],
                               files={n:desc(raw) for n,raw in sorted(received['files'].items())},source_index_sha256=INDEX_SHA256)))

    def _require_received(self, received):
        need(self.receiving_key(received) in self._checked_receivings, 'EXACT_CURRENT_RECEIVING_REQUIRED')

    def requirements(self, received):
        self._require_received(received)
        self.context(received['context'])
        return self.receiver.requirements(self, received)

    def validate_control(self, received, raw):
        self._require_received(received)
        self.context(received['context'])
        return self.receiver.validate_control(self, received, raw, time.time_ns()//1000000)

    def sender_requirements(self, source, received, root_selection, actual_host_receiving):
        need(source is self, 'EXACT_CURRENT_SOURCE_RECEIVER')
        self._require_received(received)
        self.context(received['context'])
        # Explicit actual selection: descriptors authenticate bytes only. Root
        # must separately receive provenance and issue every resulting decision.
        need(type(root_selection) is dict and set(root_selection)=={'state','packet_directory','archive','nonce'}, 'SENDER_SELECTION_FIELDS')
        need(root_selection['state']=='UNISSUED' and type(root_selection['archive']) is bytes, 'UNISSUED_SENDER_SELECTION')
        packet = Path(root_selection['packet_directory'])
        need(packet.is_absolute() and packet.name=='packet' and packet.parent.name=='assembled'
             and packet.parent.parent.resolve(strict=True)==packet.parent.parent
             and not os.path.lexists(packet.parent), 'FRESH_SELECTED_SENDER_PACKET')
        parent = self.work_root(packet.parent.parent).lstat()
        need(stat.S_ISDIR(parent.st_mode) and parent.st_uid == os.geteuid()
             and stat.S_IMODE(parent.st_mode)==0o700, 'OWNED_PRIVATE_SENDER_PARENT')
        nonce = root_selection['nonce']
        need(type(nonce) is str and re.fullmatch('[0-9a-f]{64}',nonce), 'OPERATION_NONCE_SHAPE')
        values = self.issuer.derive(self.module('receiver'),self,received,root_selection['archive'],actual_host_receiving,
                                    packet,time.time_ns()//1000000,nonce,os.geteuid(),os.getegid())
        # A requirements envelope cannot be submitted as any original admission.
        documents = {name:parse(raw) for name,raw in values.items() if name.endswith('.json')}
        return {'schema':'g132.current-pro-sender-requirements.v1','authority':'NONE','state':'UNISSUED',
                'source_index_sha256':INDEX_SHA256,'host_identity':self.identity,
                'expected_documents':documents,'required_body_descriptors':{n:desc(v) for n,v in values.items()},
                'admission_issued':False,'sender_started':False,'encryption_performed':False,
                'provider_authentication':'ACTUAL_ROOT_RECEIVING_REQUIRED','original_awards':[]}

    def work_root(self, path):
        need(type(path) in (str,Path) or isinstance(path,Path),'EXPLICIT_WORK_ROOT_REQUIRED')
        base=Path(path)
        need(base.is_absolute() and base.resolve(strict=True)==base
             and not base.is_relative_to(self.root) and not self.root.is_relative_to(base), 'SEPARATE_CANONICAL_WORK_ROOT')
        need(not any(p.is_symlink() for p in base.parents), 'WORK_ROOT_ANCESTOR_ALIAS')
        st=base.lstat()
        need(stat.S_ISDIR(st.st_mode) and st.st_uid==os.geteuid()
             and stat.S_IMODE(st.st_mode)==0o700 and not os.listxattr(base), 'CURRENT_PRIVATE_WORK_ROOT')
        return base

    def dispatcher_selection(self, work_root, args):
        # Uses unchanged original currentness/custody/manifest/fresh-path gates.
        # It writes only a local selection, never an admission or sender process.
        return self.module('pipeline',work_root=work_root).dispatcher_selection(args)

    def sender_host_view(self):
        # Explicit filename view for the original author. The root manifest is
        # a byte-exact additional reference, never a workspace/source alias.
        host={name:self.body(name) for name in self.phase['members']}
        host['PUBLIC_PACKET_MANIFEST.json']=self.body(ENTRY+'PUBLIC_PACKET_MANIFEST.json')
        return host

    def sender_author(self):
        return types.SimpleNamespace(C=self.module('compose'),A=self.module('assembler'))

    def dispatcher_derive(self, dispatcher_source, selection, byte_reader):
        need(desc(dispatcher_source)==desc(self.file('operator/dispatcher-templates-02/bind_dispatcher.py')),'EXACT_ORIGINAL_DERIVER_BYTES')
        return self.module('binder',byte_reader=byte_reader).derive(selection)

    def assemble_sender_source(self, received, inputs):
        """Pure source assembly only; never called by the public frame service.

        Requires all five actually selected late bodies and eleven private
        source bodies. Root must authenticate issuance independently. The code
        preserves original joins; preparation never authenticates issuer text.
        """
        self._require_received(received);need(received['phase']=='recipient','CURRENT_RECIPIENT_RECEIVING_REQUIRED')
        selected=parse(inputs['ROOT_SENDER_ASSEMBLY_SELECTION.json'])
        operation=parse(inputs['PRO_SENDER_OPERATION.json']);self.context(operation['context'])
        need(encode(operation['context'])==encode(received['context']),'CURRENT_RECIPIENT_OPERATION_CONTEXT')
        need(inputs['ROOT_REQUEST_ARTIFACT.zip'] and desc(inputs['ROOT_REQUEST_ARTIFACT.zip'])==received['receipt']['archive'],'CURRENT_RECIPIENT_ARCHIVE')
        self.issuer.publication_join(self.receiver,self,inputs['HOST_PUBLICATION_ROOT_RECEIVING.json'],received['context'])
        now=time.time_ns()//1000000
        need(type(operation['issued_unix_ms']) is int and type(operation['expires_unix_ms']) is int
             and operation['issued_unix_ms']<=now<operation['expires_unix_ms']<=operation['issued_unix_ms']+600000,'ACTUAL_LATE_SOURCE_WINDOW')
        need(type(operation['sender_uid']) is int and type(operation['sender_gid']) is int
             and operation['sender_uid']==os.getuid()==os.geteuid()>0
             and operation['sender_gid']==os.getgid()==os.getegid(),'ACTUAL_LATE_SOURCE_NONROOT_IDENTITY')
        packet=Path(selected['fixed_packet_directory'])
        need(packet.name=='packet' and packet.parent.name=='assembled' and not os.path.lexists(packet.parent),'FRESH_LATE_SOURCE_DESTINATION')
        self.work_root(packet.parent.parent)
        files=self.module('late').assemble(self.sender_author(),self.sender_host_view(),
            self.file('operator/public-receiver-02/author/tool_broker.py'),inputs)
        need(time.time_ns()//1000000<operation['expires_unix_ms'],'ACTUAL_LATE_SOURCE_WINDOW')
        return files

    def expected_public_sender_sources(self, selection, operation_raw, sender_admission_raw):
        """Recompute only the original author's public source substitutions.

        This does not create an executable packet: all eleven private inputs,
        original late assembly and actual issuer/custody receiving remain
        required. Returned bytes are an equality oracle for a received capture.
        """
        author=self.sender_author();C=author.C
        host,_=self.module('late').transported_host(author,self.sender_host_view(),self.file('operator/public-receiver-02/author/tool_broker.py'))
        packet={n.removeprefix(CORE):b for n,b in host.items() if n.startswith(CORE)}
        op=parse(operation_raw);self.context(op['context'])
        need(operation_raw==encode(op) and op['source_commit']==self.P.SOURCE_COMMIT and op['source_tree']==self.P.SOURCE_TREE
             and op['carrier_binding_sha256']==sha(self.binding_raw)
             and op['input_index_sha256']==self.binding['input_index']['sha256'],'EXACT_CURRENT_PUBLIC_SENDER_BINDING')
        sender=parse(packet['carrier/PRO_SENDER_COMPOSITION.json'])
        expected={'schema':'dg16.pro-private-sender-root-admission.v1','issuer':'R5_ROOT_GOVERNOR','successor':'PRO-EXECUTOR-01, designated by owner',
            'operation_sha256':sha(operation_raw),'capture_profile':sender['capture_profile'],'provider_profile':sender['provider_profile'],
            'source_commit':self.P.SOURCE_COMMIT,'source_tree':self.P.SOURCE_TREE,'carrier_binding_sha256':op['carrier_binding_sha256'],
            'limits':self.binding['limits'],'one_encryption':True,'metadata_reads':18,'automatic_retry':False,'host_or_native_effect_grant':False,'original_awards':[]}
        need(sender_admission_raw==encode(expected),'EXACT_ORIGINAL_SENDER_ADMISSION_BYTES')
        sender.update(state='REVIEWED_EXACT_PRO_SENDER',source_commit=C.SOURCE,source_tree=C.TREE,
                      operation=desc(operation_raw),admission=desc(sender_admission_raw))
        packet['carrier/PRO_SENDER_COMPOSITION.json']=encode(sender)
        packet['carrier/sender_policy.py']=C.assignments(packet['carrier/sender_policy.py'],{'BINDING_SHA256':sha(packet['carrier/PRO_SENDER_COMPOSITION.json'])})
        carrier={n[8:]:b for n,b in packet.items() if n.startswith('carrier/')};C.loader_bind(carrier)
        packet['carrier/carrier_loader.py']=carrier['carrier_loader.py']
        packet_path=PurePosixPath(selection['operation_path']).parent.parent
        entry=C.assignments(C.templates()['adapter/integration/root_sender_entry.py'],{
            'ENTRY_STATE':'REVIEWED_EXACT_ROOT_SENDER_ENTRY','FIXED_PACKET_DIRECTORY':str(packet_path),
            'LOADER_DESCRIPTOR':desc(packet['carrier/carrier_loader.py'])})
        return {'root_sender_entry.py':entry,'packet/carrier/PRO_SENDER_OPERATION.json':operation_raw,
            'packet/carrier/PRO_SENDER_ADMISSION.json':sender_admission_raw,
            **{'packet/'+n:packet[n] for n in ('carrier/carrier_loader.py','carrier/tool_broker.py','carrier/sender_policy.py','carrier/PRO_SENDER_COMPOSITION.json')}}

    def validate_dispatcher_capture(self, selection, sender_bodies, admission, bound_files):
        """Verify dynamic late bytes with the exact original pure binder.

        Source bytes are received as data. No bound entry/helper is imported,
        no dispatcher journal is touched, and issuer provenance remains Root's
        independently authenticated live admission responsibility.
        """
        names={'root_sender_entry.py','packet/carrier/PRO_SENDER_OPERATION.json',
            'packet/carrier/carrier_loader.py','packet/carrier/tool_broker.py',
            'packet/carrier/sender_policy.py','packet/carrier/PRO_SENDER_COMPOSITION.json',
            'packet/carrier/PRO_SENDER_ADMISSION.json','ROOT_LATE_RECEIVING.json'}
        need(type(sender_bodies) is dict and set(sender_bodies)==names
             and all(type(v) is bytes and 0<len(v)<=MAX_SOURCE_FILE for v in sender_bodies.values()),'EXACT_PUBLIC_SENDER_CAPTURE')
        need(type(admission) is bytes and 0<len(admission)<=16384,'BOUNDED_DISPATCH_ADMISSION_BYTES')
        source_expected=self.expected_public_sender_sources(selection,sender_bodies['packet/carrier/PRO_SENDER_OPERATION.json'],
            sender_bodies['packet/carrier/PRO_SENDER_ADMISSION.json'])
        need(all(sender_bodies[n]==body for n,body in source_expected.items()),'EXACT_CURRENT_GENERATED_SENDER_SOURCES')
        base=PurePosixPath(selection['entry_path']).parent
        mapped={str(base/n):raw for n,raw in sender_bodies.items() if n!='ROOT_LATE_RECEIVING.json'}
        mapped[selection['late_sender_receiving_path']]=sender_bodies['ROOT_LATE_RECEIVING.json']
        def read(path):
            need(str(path) in mapped,'EXACT_PUBLIC_CAPTURE_PATH');return mapped[str(path)]
        expected=self.module('binder',byte_reader=read).bind(selection,admission)
        need(type(bound_files) is dict and set(bound_files)==set(expected)
             and all(type(bound_files[n]) is bytes and bound_files[n]==raw for n,raw in expected.items()),'EXACT_ORIGINAL_BOUND_DISPATCHER_BYTES')
        op=parse(sender_bodies['packet/carrier/PRO_SENDER_OPERATION.json']);self.context(op['context'])
        need(type(op['sender_uid']) is int and type(op['sender_gid']) is int
             and op['sender_uid']==os.getuid()==os.geteuid()>0 and op['sender_gid']==os.getgid()==os.getegid(),'ACTUAL_CURRENT_DISPATCHER_OWNER')
        need(op['issued_unix_ms']<=time.time_ns()//1000000<op['expires_unix_ms'],'CURRENT_DISPATCH_OPERATION_WINDOW')
        return {'schema':'g132.current-pro-validated-dispatcher-capture.v1','authority':'NONE','state':'UNISSUED',
            'source_index_sha256':INDEX_SHA256,'host_commit':self.identity['commit'],
            'dispatcher':{'path':selection['helper_path'],'descriptor':desc(expected['dispatcher_entry.py'])},
            'sender_entry':{'path':selection['entry_path'],**desc(sender_bodies['root_sender_entry.py']),'deadline_ms':op['expires_unix_ms']},
            'admission':desc(admission),'context':op['context'],'original_binder_source':desc(self.file('operator/dispatcher-templates-02/bind_dispatcher.py')),
            'live_root_issuer_and_capture_provenance':'SEPARATE_AUTHENTICATED_CAPABILITY_REQUIRED',
            'original_binder_executed_as_module':False,'original_sender_started':False,'effect_grant':False,'original_awards':[]}

    def description(self):
        return {'schema':'g132.current-pro-interface-description.v1','authority':'NONE','state':'UNISSUED',
            'installation_index_sha256':INDEX_SHA256,'host_identity':self.identity,
            'public_source_files':len(self.phase['members']),'bounded_projections':sorted(self._plan),
            'model_side_tools_required':True,'original_sender_started':False,'original_acceptance':False}

    def public_batch(self, value):
        """Bounded public-only receiving; effects and issuances have no command."""
        need(type(value) is dict and set(value)=={'schema','source_index_sha256','commands'}
             and value['schema']=='g132.current-pro-public-batch.v1'
             and value['source_index_sha256']==INDEX_SHA256, 'EXACT_PUBLIC_BATCH_SOURCE')
        need(type(value['commands']) is list and 1<=len(value['commands'])<=8, 'BOUNDED_PUBLIC_COMMANDS')
        received={}; out=[]
        def bytes64(text):
            need(type(text) is str and len(text)<=12*1024*1024, 'PUBLIC_BASE64_BOUND')
            body=base64.b64decode(text,validate=True)
            need(base64.b64encode(body).decode()==text, 'PUBLIC_BASE64_CANONICAL')
            return body
        for command in value['commands']:
            need(type(command) is dict and type(command.get('action')) is str, 'PUBLIC_COMMAND_OBJECT')
            action=command['action']
            if action=='describe':
                need(set(command)=={'action'},'DESCRIBE_FIELDS');result=self.description()
            elif action=='read-plan':
                need(set(command)=={'action','context','artifact_id'},'READ_PLAN_FIELDS')
                self.context(command['context'])
                need(type(command['artifact_id']) is int and command['artifact_id']>0,'ARTIFACT_ID')
                result={'authority':'NONE','model_side_only':True,'calls':[
                    {'kind':k,'tool':'mcp__codex_apps__github_fetch','arguments':{'url':self.endpoint(command['context'],command['artifact_id'],k)}}
                    for k in self.B.KINDS]}
            elif action=='receive':
                need(set(command)=={'action','id','phase','context','results','archive','note','previous','actual_root'},'PUBLIC_RECEIVE_FIELDS')
                key=command['id'];need(type(key) is str and re.fullmatch('[a-z0-9_-]{1,32}',key) and key not in received,'FRESH_RECEIVING_HANDLE')
                prior=command['previous'];need(prior is None or prior in received,'EXACT_PREVIOUS_RECEIVING_HANDLE')
                got=self.receive_public(command['phase'],command['context'],{n:bytes64(v) for n,v in command['results'].items()},
                    bytes64(command['archive']),command['note'],received.get(prior),
                    None if command['actual_root'] is None else bytes64(command['actual_root']))
                received[key]=got
                result={'handle':key,'receiving_sha256':self.receiving_key(got),'receipt':got['receipt'],
                        'files':{n:desc(v) for n,v in got['files'].items()}}
            elif action in ('requirements','validate-control'):
                need(set(command)==({'action','id'} if action=='requirements' else {'action','id','body'}),'CONTROL_COMMAND_FIELDS')
                need(command['id'] in received,'CURRENT_RECEIVING_HANDLE')
                got=received[command['id']]
                result=self.requirements(got) if action=='requirements' else self.validate_control(got,bytes64(command['body']))
            elif action=='sender-requirements':
                need(set(command)=={'action','id','selection','archive','publication'},'SENDER_REQUIREMENTS_FIELDS')
                need(command['id'] in received,'CURRENT_RECEIVING_HANDLE')
                selection=dict(command['selection']);selection['archive']=bytes64(command['archive'])
                result=self.sender_requirements(self,received[command['id']],selection,bytes64(command['publication']))
            elif action=='verify-dispatcher':
                need(set(command)=={'action','selection','sender_bodies','admission','bound_files'},'DISPATCH_CAPTURE_FIELDS')
                result=self.validate_dispatcher_capture(command['selection'],{n:bytes64(v) for n,v in command['sender_bodies'].items()},
                    bytes64(command['admission']),{n:bytes64(v) for n,v in command['bound_files'].items()})
            else:
                raise ValueError('NO_EFFECT_OR_ISSUANCE_COMMAND')
            out.append({'action':action,'result':result})
        return {'schema':'g132.current-pro-public-batch-result.v1','authority':'NONE','state':'UNISSUED',
                'source_index_sha256':INDEX_SHA256,'results':out,'original_sender_started':False,
                'original_consumer_invoked':False,'issuer_decision_created':False,'original_awards':[]}


READY='READY_FOR_EPHEMERAL_DOWNLOAD_RESULT_LENGTH_FRAME'

def receive_frame(deadline_ms):
    # Same length-framed TTY transport as the demonstrated Pro adapter, with an
    # independent public-only command population. No filesystem payload reads.
    need(sys.stdin.isatty(), 'ACTUAL_TTY_REQUIRED')
    left=min(45,(deadline_ms-time.time_ns()//1000000)/1000)
    need(left>0,'PUBLIC_FRAME_EXPIRED');deadline=time.monotonic()+left
    before=termios.tcgetattr(0);changed=list(before);changed[6]=list(before[6])
    changed[3]&=~(termios.ECHO|termios.ICANON);changed[6][termios.VMIN]=1;changed[6][termios.VTIME]=0
    termios.tcsetattr(0,termios.TCSANOW,changed)
    def exact(count):
        parts=[];size=0
        while size<count:
            need(time.monotonic()<deadline,'PUBLIC_FRAME_EXPIRED')
            if select.select([0],[],[],min(.1,max(0,deadline-time.monotonic())))[0]:
                part=os.read(0,min(65536,count-size));need(part,'PUBLIC_FRAME_EOF');parts.append(part);size+=len(part)
        return b''.join(parts)
    try:
        print(READY,flush=True);header=b''
        while not header.endswith(b'\n'):
            need(len(header)<9,'PUBLIC_FRAME_HEADER_BOUND');header+=exact(1)
        need(re.fullmatch(rb'[1-9][0-9]*\n',header),'PUBLIC_FRAME_LENGTH')
        size=int(header);need(size<=24*1024*1024,'PUBLIC_FRAME_BOUND')
        return exact(size)
    finally:termios.tcsetattr(0,termios.TCSANOW,before)


def emit(value):
    sys.stdout.buffer.write(encode(value));sys.stdout.buffer.flush()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--installation',required=True,type=Path)
    parser.add_argument('--describe',action='store_true')
    parser.add_argument('--serve-one-public-batch',action='store_true')
    parser.add_argument('--deadline-ms',type=int)
    args=parser.parse_args()
    source=CurrentSources(args.installation)
    need(args.describe != args.serve_one_public_batch,'ONE_EXPLICIT_INTERFACE_ACTION')
    if args.describe:
        need(args.deadline_ms is None,'NO_DESCRIBE_DEADLINE');emit(source.description());return
    now=time.time_ns()//1000000
    need(type(args.deadline_ms) is int and now<args.deadline_ms<=now+600000,'ACTUAL_PUBLIC_PROCESS_DEADLINE')
    emit({'event':'intent','intent':{'schema':'g132.current-pro-public-interface-intent.v1',
        'kind':'public-batch','source_index_sha256':INDEX_SHA256,'maximum_bytes':24*1024*1024,
        'no_original_effects':True}})
    raw=receive_frame(args.deadline_ms)
    emit({'event':'retained','kind':'public-batch','actual_result':desc(raw)})
    result=source.public_batch(parse(raw,24*1024*1024))
    need(time.time_ns()//1000000<args.deadline_ms,'PUBLIC_PROCESS_EXPIRED')
    emit({'event':'complete','receipt':result})


if __name__=='__main__':
    try:main()
    except Exception:
        # Never echo an input body or arbitrary parser diagnostic to the model.
        emit({'event':'failure','status':'PUBLIC_INTERFACE_REFUSED','authority':'NONE',
              'original_consumer_invoked':False,'original_sender_started':False})
        raise SystemExit(1)
