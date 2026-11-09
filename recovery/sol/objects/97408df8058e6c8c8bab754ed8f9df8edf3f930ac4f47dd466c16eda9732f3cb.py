"""Pure nonpublic current04 sender integration; never starts or installs a sender.

The immutable f49 author subset replaces the unavailable Pro monolithic author
seal. Current04 host/source receiving and real late issuer inputs remain
separate. Windows/WSL dispatch and the public receiver stay Root-owned.
"""
import ast
import builtins
import hashlib
import json
from pathlib import PurePosixPath
import types

BROKER_SHA='827d4c32a2d5be3d48bdc370fdfe3df763cb7b8792421092294e3e9c65c5fbed'
PROFILE='ROOT_SUPPORTED_GITHUB_FETCH_ARTIFACT_LIST_FILE_BROKER_V2'
REPRESENTATION='SUPPORTED_COMPLETE_RUN_ARTIFACT_LIST_SELECTED_V1'
CORE='tree/qualification/dg16-r5-g1-hosted-episode/'
AUTHOR_PINS={
 'author/compose.py':'59b007f8e1c979adaffa502a1651b06ff0652bdc5dc1399a77320516f9c6e800',
 'author/workflow.py':'2c4348240873c9c7d816574044d6a10331805da14695438bfd5a3299da61c470',
 'author/sender_assembly.py':'604922c0ee2091d2698e97915cda1636e98036389ad6302f4f976d93f43d6884',
 'inputs/TEMPLATE_INDEX.json':'794223557462f723a160c76339547aa6bedc3e6c56caa0bb897ca6bf32e0a204'}
sha=lambda b:hashlib.sha256(b).hexdigest()
desc=lambda b:dict(bytes=len(b),sha256=sha(b))
encode=lambda v:(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)+'\n').encode()

def need(ok,code):
    if not ok:raise ValueError(code)

def literal(raw,name):
    hits=[n.value for n in ast.parse(raw).body if isinstance(n,ast.Assign)
      and any(isinstance(t,ast.Name) and t.id==name for t in n.targets)]
    need(len(hits)==1,'UNIQUE_LITERAL');return ast.literal_eval(hits[0])

class Author:
    """Load only exact generator algorithms from an explicit immutable byte map."""
    def __init__(self,bodies,index):
        need(type(bodies) is dict and type(index) is dict and set(index)==set(bodies),'AUTHOR_INDEX_POPULATION')
        for name,raw in bodies.items():need(type(raw) is bytes and desc(raw)==index[name],'AUTHOR_BODY_PIN')
        for name,pin in AUTHOR_PINS.items():
            need(name in bodies and sha(bodies[name])==pin,'MAINTAINED_AUTHOR_PIN')
        templates={n[len('templates/'):]:raw for n,raw in bodies.items() if n.startswith('templates/')}
        template_index=json.loads(bodies['inputs/TEMPLATE_INDEX.json'])
        need(len(templates)==42 and {n:desc(raw) for n,raw in templates.items()}==template_index,'EXACT_42_TEMPLATE_CENSUS')
        need(set(bodies)==set(AUTHOR_PINS)|{'templates/'+n for n in templates},'EXACT_AUTHOR_SUBSET')
        self.bodies=bodies;self.modules={};self.C=self.module('compose')
        self.C.templates=lambda:dict(templates)
        self.A=self.module('sender_assembly')
        # assemble uses Path only for lexical fixed Linux layout validation.
        # No claim of executing the POSIX reader/physical custody on Windows.
        self.A.Path=PurePosixPath

    def module(self,name):
        if name in self.modules:return self.modules[name]
        need(name in ('compose','workflow','sender_assembly'),'FIXED_AUTHOR_MODULE')
        raw=self.bodies['author/'+name+'.py'];m=types.ModuleType('current04_bound_'+name)
        m.__file__='/immutable-author/author/'+name+'.py'
        def importer(n,*args,**kwargs):
            return self.module(n) if n in ('compose','workflow','sender_assembly') else builtins.__import__(n,*args,**kwargs)
        m.__dict__['__builtins__']=dict(vars(builtins),__import__=importer)
        self.modules[name]=m;exec(compile(raw,m.__file__,'exec'),m.__dict__);return m

def transported_host(author,host,broker):
    """Version the Root-only transport view, preserving the public host bytes."""
    need(type(host) is dict and type(broker) is bytes and sha(broker)==BROKER_SHA,'ROOT_BROKER_PIN')
    need(literal(broker,'PROFILE')==PROFILE and literal(broker,'ARTIFACT_REPRESENTATION')==REPRESENTATION,'ROOT_BROKER_PROFILE')
    C=author.C;before=dict(host);out=dict(host);p=CORE+'carrier/'
    sender=C.parse(out[p+'PRO_SENDER_COMPOSITION.json'])
    need(sender['state']=='UNRESOLVED_PRO_SENDER_COMPONENT' and sender['operation'] is None
      and sender['admission'] is None,'ACTUAL_UNRESOLVED_HOST_REQUIRED')
    sender['provider_profile']=PROFILE
    out[p+'tool_broker.py']=broker
    out[p+'PRO_SENDER_COMPOSITION.json']=C.encode(sender)
    out[p+'sender_policy.py']=C.assignments(out[p+'sender_policy.py'],dict(PROVIDER_PROFILE=PROFILE,
      BINDING_SHA256=sha(out[p+'PRO_SENDER_COMPOSITION.json'])))
    carrier={n[len(p):]:raw for n,raw in out.items() if n.startswith(p)}
    C.loader_bind(carrier);out[p+'carrier_loader.py']=carrier['carrier_loader.py']
    allowed={p+n for n in ('tool_broker.py','PRO_SENDER_COMPOSITION.json','sender_policy.py','carrier_loader.py')}
    need({n for n in out if out[n]!=before[n]}==allowed,'EXACT_UNRESOLVED_ROOT_TRANSPORT_DELTA')
    need(out['PUBLIC_PACKET_MANIFEST.json']==before['PUBLIC_PACKET_MANIFEST.json'],'HOST_MANIFEST_UNCHANGED')
    return out,before

def stage(author,host,broker,private):
    """Close immutable, deliberately unresolved source packet before a live run."""
    transported,before=transported_host(author,host,broker);p=CORE+'carrier/'
    index=author.C.parse(before[p+'INPUT_INDEX.json'])
    need({n:desc(raw) for n,raw in private.items()}==index and len(private)==11,'EXACT_ACTUAL_ELEVEN_PRIVATE_SOURCE_BODIES')
    files={'packet/'+n[len(CORE):]:raw for n,raw in transported.items() if n.startswith(CORE)}
    files.update({'packet/private-inputs/'+n:raw for n,raw in private.items()})
    need('root_sender_entry.py' not in files and 'packet/carrier/PRO_SENDER_OPERATION.json' not in files
      and 'packet/carrier/PRO_SENDER_ADMISSION.json' not in files,'UNRESOLVED_STAGE_CANNOT_BE_AN_EXECUTABLE_ADMISSION')
    files['STAGE_BOUNDARY.json']=encode(dict(schema='dg16.current04-late-sender-source-stage.v1',authority='NONE',
      state='UNRESOLVED_SOURCE_ONLY_NOT_A_LATE_OPERATION',host_manifest=desc(before['PUBLIC_PACKET_MANIFEST.json']),
      provider_profile=PROFILE,original_host_modified=False,private_source_bodies=11,
      actual_recipient_nonce_or_root_operation_supplied=False,actual_installation=False,
      actual_sender_or_provider_execution=False,original_awards=[]))
    return files

def assemble(author,host,broker,inputs):
    """Consume the five REAL late bodies plus eleven exact private source bodies.

    This constructs source only. Matching bytes do not authenticate an issuer,
    provider, publication or live recipient. Root receives those separately.
    """
    transported,before=transported_host(author,host,broker)
    out=author.A.assemble(transported,inputs)
    allowed={'carrier/tool_broker.py','carrier/PRO_SENDER_COMPOSITION.json','carrier/sender_policy.py','carrier/carrier_loader.py'}
    delta={}
    for name,raw in before.items():
        if name.startswith(CORE):
            rel=name[len(CORE):];actual=out['packet/'+rel]
            if actual!=raw:
                need(rel in allowed,'UNEXPECTED_ROOT_PACKET_DELTA');delta[rel]=dict(before=desc(raw),after=desc(actual))
    need(set(delta)==allowed,'EXACT_FOUR_LATE_ROOT_CODE_DELTAS')
    need(out['packet/carrier/CARRIER_COMPOSITION.json']==before[CORE+'carrier/CARRIER_COMPOSITION.json']
      and out['packet/carrier/INPUT_INDEX.json']==before[CORE+'carrier/INPUT_INDEX.json'],'HOST_BINDING_INDEX_UNCHANGED')
    out['ROOT_TRANSPORT_DELTA.json']=encode(dict(schema='dg16.root-only-artifact-list-sender-delta.v1',authority='NONE',
      host_manifest=desc(before['PUBLIC_PACKET_MANIFEST.json']),host_installed_bodies_changed=False,
      provider_profile=PROFILE,artifact_representation=REPRESENTATION,changed_root_packet_members=delta,
      metadata_reads=18,fresh_listings_per_phase=2,automatic_retry=False,sender_started=False,
      root_tool_history_authentication_required=True,original_awards=[]))
    manifest=author.C.parse(out['ROOT_SENDER_INSTALL_MANIFEST.json'])
    manifest['members']={n:desc(raw) for n,raw in out.items() if n!='ROOT_SENDER_INSTALL_MANIFEST.json'}
    out['ROOT_SENDER_INSTALL_MANIFEST.json']=author.C.encode(manifest)
    return out

def dispatcher_requirements(dispatcher_source,late_packet,selection,late_receiving):
    """Run exact retained derive() through a byte-only reader, never bind JS.

    Root owns Windows/WSL helper adaptation/installation and real dispatch
    admission. This function emits an authority-NONE requirements object only.
    """
    need(sha(dispatcher_source)=='d83c761dbc666d78856cf2d52ced4db2b6b8d373742deef4938b2d4b6434938f','CURRENT04_CORRECTED_DISPATCHER_DERIVER_PIN')
    m=types.ModuleType('current04_dispatcher_requirements');m.__file__='/immutable-author/bind_dispatcher.py'
    exec(compile(dispatcher_source,m.__file__,'exec'),m.__dict__)
    m.Path=PurePosixPath
    entry=PurePosixPath(selection['entry_path']);base=entry.parent
    mapped={str(base/name):raw for name,raw in late_packet.items()}
    mapped[selection['late_sender_receiving_path']]=late_receiving
    def read(path):
        name=str(path);need(name in mapped,'EXACT_LATE_DERIVER_INPUT_ONLY');return mapped[name]
    m.read=read
    binding,expected,evidence=m.derive(selection)
    return encode(dict(schema='dg16.dispatcher-root-admission-requirements.v1',authority='NONE',
      actual_admission=False,expected_body=expected,actual_late_receiving=evidence,
      transport_adaptation='ROOT_OWNED_WINDOWS_WSL_HELPER_SEPARATE',original_awards=[]))

def requirements():
    return dict(schema='dg16.current04-late-sender-input-contract.v1',authority='NONE',
      actual_late_inputs_required=['ROOT_SENDER_ASSEMBLY_SELECTION.json','PRO_SENDER_OPERATION.json',
        'PRO_SENDER_ADMISSION.json','ROOT_REQUEST_ARTIFACT.zip','HOST_PUBLICATION_ROOT_RECEIVING.json'],
      private_inputs='ELEVEN_CURRENT04_ACTUAL_BODIES_WITH_EXACT_CURRENT04_INDEX; NEVER_PUBLIC',
      no_longer_required='LOST_PRO_MONOLITHIC_AUTHOR_SEAL_OR_RUNTIME',
      preserved_authority='Exact f49 author subset + current04 actual phase/review/Root receiving, all independently byte-bound',
      late_fields='Actual same-run recipient/request nonce and separate Root operation nonce/time/nonroot identity; actual publication and authenticated supported provider history',
      issuer='ROOT_MUST_ACTUALLY_ISSUE_OPERATION_ADMISSION_AND_SELECTION_AFTER_REAL_RECIPIENT_RECEIVING',
      installation='Fresh nonalias POSIX packet tree owner actualuid/gid; directories0700/public0400/private0600; independent full index/mode/readback required before execute',
      dispatcher='Retained pure derive only; actual dispatch admission and Windows/WSL helper remain Root owned',
      no_effect=True,original_awards=[])
