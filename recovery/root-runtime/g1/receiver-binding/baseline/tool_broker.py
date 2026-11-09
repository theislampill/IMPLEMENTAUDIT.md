"""Eighteen fixed supported-tool reads over owned write-once files.

This module never performs a network/tool call. Only the explicitly reviewed
root dispatcher may execute a reserved plan with the supported GitHub tool.
The result bytes and tool history are the authentication boundary; fields in
these files never attest that a tool or an actor really produced them.
"""
import os
from pathlib import Path
import re
import stat
import time
import carrier_policy as P
import carrier_io as F
import provider_reader as V

PROFILE='ROOT_SUPPORTED_GITHUB_FETCH_ARTIFACT_LIST_FILE_BROKER_V2'
ARTIFACT_REPRESENTATION='SUPPORTED_COMPLETE_RUN_ARTIFACT_LIST_SELECTED_V1'
TOOL='mcp__codex_apps__github_fetch'
KINDS=('run','attempt','jobs','artifact','artifacts','workflow')
PHASES=('OPENING','PRE_ENCRYPTION','CLOSING')
PARTS=('REQUEST','REQUEST_READY','DISPATCH_INTENT','TOOL_RESULT','REPLY','REPLY_READY','JOIN')
MAX_BYTES=12*1024**2
MAX_ENTRIES=18*7+2
TOOL_MAX=4*1024**2
END_MAX=65536
LIMITS={'REQUEST':4096,'REQUEST_READY':0,'DISPATCH_INTENT':8192,'TOOL_RESULT':TOOL_MAX,
        'REPLY':8192,'REPLY_READY':0,'JOIN':8192}

def endpoint(context,artifact_id,kind):
    P.context(context);P.integer(artifact_id,1,10**20);P.need(kind in KINDS,'BROKER_FIXED_KIND')
    run=context['run_id'];prefix='https://api.github.com/repos/'+P.REPOSITORY
    paths={'run':'/actions/runs/'+run,'attempt':'/actions/runs/'+run+'/attempts/1',
      'jobs':'/actions/runs/'+run+'/attempts/1/jobs?per_page=100&page=1',
      'artifact':'/actions/runs/'+run+'/artifacts?per_page=100','artifacts':'/actions/runs/'+run+'/artifacts?per_page=100',
      'workflow':'/contents/'+context['workflow_path']+'?ref='+context['workflow_commit']}
    return prefix+paths[kind]

def name(ordinal,part):
    P.integer(ordinal,0,17);P.need(part in PARTS,'BROKER_FIXED_PART')
    return 'BROKER_%02d_%s'%(ordinal,part)

def allowed():
    result={'BROKER_START.json':END_MAX,'BROKER_END.json':END_MAX}
    result.update({name(i,p):LIMITS[p] for i in range(18) for p in PARTS})
    return result

def unwrap_tool_result(raw,url,*,kind,context=None,workflow_sha256=None,artifact_id=None):
    P.need(kind in KINDS,'BROKER_FIXED_KIND')
    if kind=='workflow':
        P.need(url==V.workflow_endpoint(context),'BROKER_WORKFLOW_ENDPOINT_CONTEXT')
        P.digest(workflow_sha256)
    P.need(type(raw) is bytes and 0<len(raw)<=TOOL_MAX,'BROKER_TOOL_RESULT_BOUND')
    value=V.json_body(raw)
    P.need(type(value) is dict and set(value)<= {'content','structuredContent','isError','_meta'}
      and value.get('isError') is False,'BROKER_TOOL_ERROR_OR_SHAPE')
    meta=value.get('_meta',{})
    P.need(type(meta) is dict and not any(meta.get(k) for k in ('truncated','isTruncated','partial','hasMore')),
      'BROKER_TOOL_TRUNCATION')
    sc=value.get('structuredContent')
    P.need(type(sc) is dict and set(sc)<= {'content','title','modified_date','url','display_url','display_title','structuredContent'}
      and sc.get('url')==url and sc.get('display_url')==url and type(sc.get('content')) is str,
      'BROKER_ACTUAL_TOOL_ENDPOINT')
    if 'structuredContent' in sc:
        inner=sc['structuredContent']
        P.need(type(inner) is dict and set(inner)<= {'title','content','display_url'}
          and inner.get('content')==sc['content'] and inner.get('display_url')==url,'BROKER_NESTED_RESULT_CHANGED')
    body=sc['content'].encode('utf-8')
    P.need(0<len(body)<=P.MAX_METADATA,'BROKER_PROVIDER_BODY_BOUND')
    if kind=='workflow':parsed=V.supported_workflow(body,raw,context,workflow_sha256)
    else:
        parsed=V.json_body(body);P.need(type(parsed) is dict,'BROKER_PROVIDER_BODY_SHAPE')
    if kind=='artifact':
        P.need(url==endpoint(context,artifact_id,'artifact'),'BROKER_ARTIFACT_LIST_ENDPOINT')
        parsed=select_artifact(parsed,artifact_id)
    return body,parsed


def select_artifact(listing,artifact_id):
    """Select an object from a complete genuine listing; never invent an endpoint."""
    P.integer(artifact_id,1,10**20)
    P.need(type(listing) is dict and set(listing)=={'total_count','artifacts'}
      and type(listing['total_count']) is int and type(listing['artifacts']) is list
      and listing['total_count']==len(listing['artifacts'])<=100,'BROKER_ARTIFACT_LIST_COMPLETE')
    seen=set();selected=[]
    for row in listing['artifacts']:
        P.need(type(row) is dict,'BROKER_ARTIFACT_LIST_ROW');P.integer(row.get('id'),1,10**20)
        P.need(row['id'] not in seen,'BROKER_ARTIFACT_LIST_DUPLICATE_ID');seen.add(row['id'])
        if row['id']==artifact_id:selected.append(row)
    P.need(len(selected)==1,'BROKER_ARTIFACT_LIST_UNIQUE_ID');value=selected[0]
    P.need(type(value.get('name')) is str and bool(value['name'])
      and len([r for r in listing['artifacts'] if r.get('name')==value['name']])==1,'BROKER_ARTIFACT_LIST_UNIQUE_NAME')
    return value

def artifact_provenance(raw,url,context,artifact_id):
    body,value=unwrap_tool_result(raw,url,kind='artifact',context=context,artifact_id=artifact_id)
    listing=V.json_body(body)
    return dict(schema='dg16.selected-artifact-list-provenance.v1',authority='NONE',representation=ARTIFACT_REPRESENTATION,
      endpoint=url,run_id=context['run_id'],run_attempt=context['run_attempt'],artifact_id=artifact_id,
      complete_listing_count=listing['total_count'],actual_tool_result=P.descriptor(raw),provider_listing_body=P.descriptor(body),
      selected_artifact_object=P.descriptor(P.encode(value)),direct_artifact_endpoint_used=False,
      authentication_boundary='ACTUAL_ROOT_TOOL_HISTORY_REQUIRED')

class Store:
    """Internal held-directory API; the external dispatcher derives its path."""
    def __init__(self,directory,binding,operation,deadline,*,budget=None,create=False):
        self.directory=Path(directory);self.binding=binding;self.op=operation;self.deadline=deadline;self.closed=False
        self.fd=os.open(self.directory,os.O_RDONLY|os.O_DIRECTORY|os.O_CLOEXEC|os.O_NOFOLLOW)
        try:
            self.identity=F.directory_id(os.fstat(self.fd));self.ancestry=F.parents(self.directory/'marker')
            self._current()
            if create:
                P.need(budget is not None,'BROKER_PREALLOCATION_REQUIRED');budget.reserve(MAX_BYTES,MAX_ENTRIES)
                P.need(not any(p.name.startswith('BROKER_') for p in self.directory.iterdir()),'BROKER_FRESH_SESSION_REQUIRED')
                start=dict(schema='dg16.root-tool-broker-start.v1',profile=PROFILE,context=operation['context'],
                  source_commit=binding['source_commit'],source_tree=binding['source_tree'],
                  carrier_binding_sha256=P.sha(binding['_binding_raw']),input_index_sha256=P.C.check_index(binding['_index']),
                  request_artifact=operation['artifact'],artifact_id=operation['artifact_id'],nonce=operation['nonce'],
                  operation_sha256=P.sha(P.encode(operation)),directory_identity=self.identity,deadline_monotonic=deadline,
                  max_bytes=MAX_BYTES,max_entries=MAX_ENTRIES,tool=TOOL,authority='NONE',original_awards=[])
                self.write('BROKER_START.json',P.encode(start),opening=True)
            start=self.read_json('BROKER_START.json');self.start=start
            P.need(start==dict(schema='dg16.root-tool-broker-start.v1',profile=PROFILE,context=operation['context'],
              source_commit=binding['source_commit'],source_tree=binding['source_tree'],
              carrier_binding_sha256=P.sha(binding['_binding_raw']),input_index_sha256=P.C.check_index(binding['_index']),
              request_artifact=operation['artifact'],artifact_id=operation['artifact_id'],nonce=operation['nonce'],
              operation_sha256=P.sha(P.encode(operation)),directory_identity=self.identity,deadline_monotonic=deadline,
              max_bytes=MAX_BYTES,max_entries=MAX_ENTRIES,tool=TOOL,authority='NONE',original_awards=[]),'BROKER_START_BINDING')
        except BaseException:
            os.close(self.fd);self.closed=True;raise
    def _current(self):
        P.need(not self.closed and F.directory_id(os.fstat(self.fd))==self.identity
          and F.directory_id(self.directory.lstat())==self.identity and not self.directory.is_symlink()
          and os.fstat(self.fd).st_uid==os.geteuid() and stat.S_IMODE(os.fstat(self.fd).st_mode)==0o700
          and not os.listxattr(self.fd) and F.parents(self.directory/'marker')==self.ancestry,'BROKER_DIRECTORY_CUSTODY')
    def census(self):
        self._current();result={};limits=allowed()
        for entry in sorted(self.directory.iterdir()):
            if not entry.name.startswith('BROKER_'):continue
            P.need(entry.name in limits,'BROKER_UNKNOWN_MEMBER')
            raw,row=F.read_file(entry,limits[entry.name],private=True)
            P.need(F.directory_id(self.directory.lstat())==self.identity,'BROKER_CENSUS_CHANGED')
            result[entry.name]=row
        P.need(len(result)<=MAX_ENTRIES and sum(r['bytes'] for r in result.values())<=MAX_BYTES,'BROKER_ALLOCATION_BOUND')
        return result
    def write(self,member,raw,*,opening=False,closing=False):
        self._current();P.need(member in allowed() and type(raw) is bytes and len(raw)<=allowed()[member],'BROKER_WRITE_SCOPE')
        rows=self.census();P.need('BROKER_END.json' not in rows,'BROKER_ALREADY_TERMINAL')
        P.need(member not in rows,'BROKER_WRITE_ONCE')
        P.need(sum(r['bytes'] for r in rows.values())+len(raw)+(0 if closing else END_MAX)<=MAX_BYTES
          and len(rows)+1+(0 if closing else 1)<=MAX_ENTRIES,'BROKER_PROSPECTIVE_ALLOCATION')
        P.need(opening or closing or time.monotonic()<self.deadline,'BROKER_DEADLINE')
        # Keep the directory FD open throughout the no-follow, exclusive write.
        fd=os.open(member,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW|os.O_CLOEXEC,0o600,dir_fd=self.fd)
        try:
            os.fchmod(fd,0o600)
            offset=0
            while offset<len(raw):
                n=os.write(fd,raw[offset:]);P.need(n>0,'BROKER_WRITE');offset+=n
            os.fsync(fd)
        finally:os.close(fd)
        os.fsync(self.fd);observed,row=F.read_file(self.directory/member,allowed()[member],private=True)
        self._current();P.need(observed==raw,'BROKER_WRITE_READBACK');return row
    def read(self,member):
        self._current();P.need(member in allowed(),'BROKER_READ_SCOPE')
        raw,row=F.read_file(self.directory/member,allowed()[member],private=True);self._current();return raw,row
    def read_json(self,member):return P.parse(self.read(member)[0],allowed()[member])
    def marker_ready(self,ordinal,part):
        P.need(part in ('REQUEST_READY','REPLY_READY'),'BROKER_FIXED_READY_MARKER')
        self._current();member=name(ordinal,part)
        try:info=os.stat(member,dir_fd=self.fd,follow_symlinks=False)
        except FileNotFoundError:return False
        P.need(stat.S_ISREG(info.st_mode) and info.st_nlink==1 and info.st_size==0
          and info.st_uid==os.geteuid() and stat.S_IMODE(info.st_mode)==0o600,'BROKER_READY_MARKER_CUSTODY')
        P.need(self.read(member)[0]==b'','BROKER_READY_MARKER_BODY');return True
    def request(self,ordinal):
        P.integer(ordinal,0,17)
        phase,kind=PHASES[ordinal//6],KINDS[ordinal%6]
        return dict(schema='dg16.root-tool-broker-request.v1',profile=PROFILE,ordinal=ordinal,phase=phase,kind=kind,
          nonce=self.op['nonce'],operation_sha256=P.sha(P.encode(self.op)),context=self.op['context'],
          artifact_id=self.op['artifact_id'],source_commit=self.binding['source_commit'],source_tree=self.binding['source_tree'],
          carrier_binding_sha256=P.sha(self.binding['_binding_raw']),method='GET',tool=TOOL,
          arguments=dict(url=endpoint(self.op['context'],self.op['artifact_id'],kind)))
    def _request_body(self,ordinal):
        raw,row=self.read(name(ordinal,'REQUEST'));value=P.parse(raw,4096)
        P.need(value==self.request(ordinal) and self.read(name(ordinal,'REQUEST_READY'))[0]==b'',
          'BROKER_REQUEST_EXACT_BINDING')
        return value,row
    def inspect_request(self,ordinal):
        value,row=self._request_body(ordinal)
        for i in range(ordinal):self.joined(i)
        P.need(not any(name(i,'REQUEST') in self.census() for i in range(ordinal+1,18)),'BROKER_REQUEST_ORDER')
        return value,row
    def reserve_dispatch(self,ordinal):
        request,row=self.inspect_request(ordinal);rows=self.census()
        P.need(name(ordinal,'DISPATCH_INTENT') not in rows,'BROKER_UNCERTAIN_RESERVATION_NO_SECOND_FETCH')
        P.need(time.monotonic()<self.deadline,'BROKER_DEADLINE')
        # A maximum sized tool result and all remainder records must fit before GET.
        P.need(sum(r['bytes'] for r in rows.values())+TOOL_MAX+3*8192+END_MAX<=MAX_BYTES,'BROKER_DISPATCH_ALLOCATION')
        intent=dict(schema='dg16.root-tool-broker-dispatch-intent.v1',ordinal=ordinal,nonce=self.op['nonce'],
          request=P.descriptor(P.encode(request)),tool=TOOL,arguments=request['arguments'],
          deadline_monotonic=min(self.deadline,time.monotonic()+self.binding['limits']['command_seconds']),
          automatic_retry=False,external_tool_history_required=True)
        pin=self.write(name(ordinal,'DISPATCH_INTENT'),P.encode(intent))
        return dict(tool=TOOL,arguments=request['arguments'],ordinal=ordinal,nonce=self.op['nonce'],
          intent_sha256=pin['sha256'],request_sha256=row['sha256'],deadline_monotonic=intent['deadline_monotonic'])
    def publish_response(self,ordinal,intent_sha256,actual_tool_result_raw,tool_call_ref):
        request,_=self.inspect_request(ordinal);iraw,_=self.read(name(ordinal,'DISPATCH_INTENT'));intent=P.parse(iraw,8192)
        P.need(P.sha(iraw)==intent_sha256 and intent['request']==P.descriptor(P.encode(request))
          and intent['tool']==TOOL and intent['arguments']==request['arguments'] and intent['nonce']==self.op['nonce']
          and intent['ordinal']==ordinal and intent['automatic_retry'] is False,'BROKER_DISPATCH_JOIN')
        P.need(type(tool_call_ref) is str and re.fullmatch('[A-Za-z0-9_-]{1,160}',tool_call_ref),'BROKER_EXTERNAL_CALL_REFERENCE')
        P.need(type(actual_tool_result_raw) is bytes and 0<len(actual_tool_result_raw)<=TOOL_MAX,'BROKER_TOOL_RESULT_BOUND')
        rows=self.census()
        if name(ordinal,'REPLY_READY') in rows:
            reply=self.reply(ordinal)
            P.need(self.read(name(ordinal,'TOOL_RESULT'))[0]==actual_tool_result_raw
              and reply['tool_call_ref']==tool_call_ref,'BROKER_COMMITTED_RESPONSE_CHANGED')
            return dict(status='RECEIVED_EXISTING_COMMITTED_REPLY',reply=reply,fetch_permitted=False)
        P.need(name(ordinal,'TOOL_RESULT') not in rows and name(ordinal,'REPLY') not in rows,
          'BROKER_UNCERTAIN_PARTIAL_RESPONSE_NO_RETRY')
        self.write(name(ordinal,'TOOL_RESULT'),actual_tool_result_raw)
        reason=None;body=None
        try:body,_=unwrap_tool_result(actual_tool_result_raw,request['arguments']['url'],kind=request['kind'],
          context=self.op['context'],workflow_sha256=self.binding['workflow_sha256'],artifact_id=self.op['artifact_id'])
        except (ValueError,UnicodeError):reason='TOOL_ERROR_TRUNCATION_OR_ENDPOINT_REFUSED'
        if time.monotonic()>=intent['deadline_monotonic']:reason='TOOL_DEADLINE_EXPIRED'
        reply=dict(schema='dg16.root-tool-broker-reply.v1',ordinal=ordinal,nonce=self.op['nonce'],
          request_sha256=P.sha(P.encode(request)),intent_sha256=intent_sha256,tool_call_ref=tool_call_ref,
          tool_result=P.descriptor(actual_tool_result_raw),provider_body=P.descriptor(body) if body is not None else None,
          status='RECEIVED' if reason is None else 'REFUSED',refusal=reason,
          authentication_boundary='ACTUAL_ROOT_TOOL_HISTORY_REQUIRED',authority='NONE')
        self.write(name(ordinal,'REPLY'),P.encode(reply));self.write(name(ordinal,'REPLY_READY'),b'')
        return dict(status='COMMITTED_REPLY',reply=reply,fetch_permitted=False)
    def reply(self,ordinal):
        request,_=self._request_body(ordinal);iraw,_=self.read(name(ordinal,'DISPATCH_INTENT'))
        raw,_=self.read(name(ordinal,'TOOL_RESULT'));r=self.read_json(name(ordinal,'REPLY'))
        P.exact(r,('schema','ordinal','nonce','request_sha256','intent_sha256','tool_call_ref','tool_result','provider_body',
          'status','refusal','authentication_boundary','authority'))
        P.need(r['schema']=='dg16.root-tool-broker-reply.v1' and r['ordinal']==ordinal and r['nonce']==self.op['nonce']
          and r['request_sha256']==P.sha(P.encode(request)) and r['intent_sha256']==P.sha(iraw)
          and r['tool_result']==P.descriptor(raw) and r['authority']=='NONE'
          and r['authentication_boundary']=='ACTUAL_ROOT_TOOL_HISTORY_REQUIRED'
          and self.read(name(ordinal,'REPLY_READY'))[0]==b'','BROKER_REPLY_BODY_JOIN')
        if r['status']=='RECEIVED':
            body,_=unwrap_tool_result(raw,request['arguments']['url'],kind=request['kind'],
              context=self.op['context'],workflow_sha256=self.binding['workflow_sha256'],artifact_id=self.op['artifact_id'])
            P.need(r['provider_body']==P.descriptor(body) and r['refusal'] is None,'BROKER_REPLY_PROVIDER_JOIN')
        else:P.need(r['status']=='REFUSED' and r['refusal'] in ('TOOL_ERROR_TRUNCATION_OR_ENDPOINT_REFUSED','TOOL_DEADLINE_EXPIRED'),
          'BROKER_REPLY_STATUS')
        return r
    def joined(self,ordinal):
        reply=self.reply(ordinal);join=self.read_json(name(ordinal,'JOIN'))
        P.need(join==dict(schema='dg16.root-tool-broker-join.v1',ordinal=ordinal,nonce=self.op['nonce'],
          request_sha256=reply['request_sha256'],reply_sha256=P.sha(P.encode(reply)),tool_result=reply['tool_result'],
          provider_body=reply['provider_body'],status=reply['status'],authentication_boundary='ACTUAL_ROOT_TOOL_HISTORY_REQUIRED'),
          'BROKER_CLIENT_JOIN_CHANGED')
        return join
    def finish(self,complete):
        rows=self.census();P.need('BROKER_END.json' not in rows,'BROKER_ALREADY_TERMINAL')
        sequence=['BROKER_START.json']+[name(i,p) for i in range(18) for p in PARTS]
        present=[n for n in sequence if n in rows]
        P.need(present==sequence[:len(present)] and set(present)==set(rows),'BROKER_EXACT_PARTIAL_POPULATION')
        if complete:
            P.need(set(rows)==set(sequence),'BROKER_INCOMPLETE_POPULATION')
            for i in range(18):P.need(self.joined(i)['status']=='RECEIVED','BROKER_REFUSED_JOIN')
        end=dict(schema='dg16.root-tool-broker-end.v1',authority='NONE',complete=complete,
          nonce=self.op['nonce'],prefix={n:dict(bytes=r['bytes'],sha256=r['sha256']) for n,r in rows.items()},
          prefix_bytes=sum(r['bytes'] for r in rows.values()),prefix_entries=len(rows),original_awards=[])
        self.write('BROKER_END.json',P.encode(end),closing=True);final=self.census()
        self._current();os.close(self.fd);self.closed=True
        return dict(complete=complete,members=final,bytes=sum(r['bytes'] for r in final.values()),entries=len(final),
          authority='NONE',authentication_boundary='ACTUAL_ROOT_TOOL_HISTORY_REQUIRED')
    def close_fd(self):
        if not self.closed:os.close(self.fd);self.closed=True

class Client:
    def __init__(self,store):self.store=store;self.audit=[];self.ordinal=0
    def get(self,kind,identifier):
        i=self.ordinal;P.integer(i,0,17);s=self.store;request=s.request(i)
        expected=s.op['context']['workflow_commit'] if kind=='workflow' else str(s.op['artifact_id']) if kind=='artifact' else s.op['context']['run_id']
        P.need(kind==KINDS[i%6] and identifier==expected,'BROKER_FIXED_READ_SCHEDULE')
        started=time.monotonic();s.write(name(i,'REQUEST'),P.encode(request));s.write(name(i,'REQUEST_READY'),b'')
        deadline=min(s.deadline,started+s.binding['limits']['command_seconds'])
        # Uncommitted TOOL_RESULT/REPLY files may be in the writer's hands.
        # Until the ready marker, observe only that fixed marker, not those bodies.
        while not s.marker_ready(i,'REPLY_READY'):
            remaining=deadline-time.monotonic();P.need(remaining>0,'BROKER_REPLY_DEADLINE')
            time.sleep(min(0.05,remaining))
        reply=s.reply(i);P.need(time.monotonic()<deadline,'BROKER_REPLY_DEADLINE')
        join=dict(schema='dg16.root-tool-broker-join.v1',ordinal=i,nonce=s.op['nonce'],request_sha256=reply['request_sha256'],
          reply_sha256=P.sha(P.encode(reply)),tool_result=reply['tool_result'],provider_body=reply['provider_body'],
          status=reply['status'],authentication_boundary='ACTUAL_ROOT_TOOL_HISTORY_REQUIRED')
        s.write(name(i,'JOIN'),P.encode(join));self.ordinal+=1
        P.need(reply['status']=='RECEIVED','BROKER_ROOT_TOOL_REFUSED')
        raw,_=s.read(name(i,'TOOL_RESULT'));body,value=unwrap_tool_result(raw,request['arguments']['url'],kind=kind,
          context=s.op['context'],workflow_sha256=s.binding['workflow_sha256'],artifact_id=s.op['artifact_id'])
        self.audit.append(dict(kind=kind,bytes=len(body),sha256=P.sha(body),elapsed_ns=int((time.monotonic()-started)*10**9),
          broker_ordinal=i,tool_result_sha256=P.sha(raw),root_tool_call_ref=reply['tool_call_ref']))
        if kind=='artifact':self.audit[-1]['artifact_metadata']=artifact_provenance(raw,request['arguments']['url'],s.op['context'],s.op['artifact_id'])
        return value

def receive_request(binding,context,artifact_id,archive,store):
    api=Client(store);observed=V.snapshot(api,context,artifact_id)
    checked=V.check_snapshot(observed,archive,context,binding['_index'],binding['workflow_sha256'],int(time.time()*1000),
      workflow_representation=V.SUPPORTED_TOOL_WORKFLOW)
    P.need(checked['artifact_id']==artifact_id,'BROKER_ARTIFACT_IDENTIFIER')
    return V.ReceivedRequest(V._RECEIVED,checked,archive,binding,api,observed,
      workflow_representation=V.SUPPORTED_TOOL_WORKFLOW)
