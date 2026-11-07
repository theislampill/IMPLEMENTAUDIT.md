#!/usr/bin/env python3
"""Deterministic local Responses API seam. This is NOT model inference."""
import hashlib,http.server,json,os,queue,threading,time
from pathlib import Path
class Provider:
 def __init__(self,root):
  self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True);self.steps=queue.Queue();self.requests=[];self.lock=threading.Lock();self.seen=threading.Event();self.release=threading.Event();self.release.set();outer=self
  class Handler(http.server.BaseHTTPRequestHandler):
   def log_message(self,*args):pass
   def do_POST(self):
    raw=self.rfile.read(int(self.headers.get('Content-Length','0')))
    obj=json.loads(raw)
    with outer.lock:
     n=len(outer.requests)+1;outer.requests.append(obj)
     (outer.root/f'request-{n:03}.json').write_text(json.dumps({'path':self.path,'request':obj,'header_names':sorted(self.headers.keys()),'body_sha256':hashlib.sha256(raw).hexdigest()},sort_keys=True,indent=2)+'\n')
    outer.seen.set()
    try:step=outer.steps.get(timeout=2)
    except queue.Empty:step={'type':'error','status':503,'message':'No armed canary response'}
    if step.get('wait'):outer.release.wait(timeout=20)
    if step.get('type')=='error':
     data=json.dumps({'error':{'message':step.get('message','DG17 deterministic provider error'),'type':'invalid_request_error','code':'canary_error'}}).encode();self.send_response(step.get('status',400));self.send_header('Content-Type','application/json');self.send_header('Content-Length',str(len(data)));self.end_headers();self.wfile.write(data);return
    rid='resp_dg17_'+str(n);itemid='msg_dg17_'+str(n);text=step.get('text','DG17 native yield observed.')
    if step.get('type')=='function':
     item={'type':'function_call','id':'fc_'+str(n),'call_id':'call_'+str(n),'name':step['name'],'arguments':json.dumps(step['arguments'])}
    else:item={'type':'message','id':itemid,'role':'assistant','status':'completed','content':[{'type':'output_text','text':text,'annotations':[]}]}
    events=[('response.created',{'response':{'id':rid,'object':'response','status':'in_progress','output':[]}}),('response.output_item.added',{'output_index':0,'item':item})]
    if step.get('type')!='function':events += [('response.content_part.added',{'item_id':itemid,'output_index':0,'content_index':0,'part':{'type':'output_text','text':'','annotations':[]}}),('response.output_text.delta',{'item_id':itemid,'output_index':0,'content_index':0,'delta':text}),('response.output_text.done',{'item_id':itemid,'output_index':0,'content_index':0,'text':text})]
    events += [('response.output_item.done',{'output_index':0,'item':item}),('response.completed',{'response':{'id':rid,'object':'response','status':'completed','output':[item],'usage':step.get('usage',{'input_tokens':1,'output_tokens':1,'total_tokens':2})}})]
    self.send_response(200);self.send_header('Content-Type','text/event-stream');self.send_header('Cache-Control','no-cache');self.send_header('Connection','close');self.end_headers()
    try:
     for typ,val in events:self.wfile.write(('event: '+typ+'\ndata: '+json.dumps({'type':typ,**val})+'\n\n').encode());self.wfile.flush()
    except (BrokenPipeError,ConnectionResetError):pass
  self.server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);self.server.daemon_threads=True
  self.thread=threading.Thread(target=self.server.serve_forever,name='dg17-local-responses',daemon=True);self.thread.start()
  (self.root/'LISTENER.json').write_text(json.dumps({'address':'127.0.0.1','port':self.server.server_port,'owner_pid':os.getpid(),'scope':'DETERMINISTIC_EMULATED_MODEL'},indent=2)+'\n')
 @property
 def url(self):return f'http://127.0.0.1:{self.server.server_port}/v1'
 def arm(self,*steps):
  self.seen.clear()
  for step in steps:self.steps.put(step)
 def close(self):
  self.release.set();self.server.shutdown();self.server.server_close();self.thread.join(timeout=3)
  return {'provider_thread_joined':not self.thread.is_alive(),'port':self.server.server_port,'request_count':len(self.requests),'remaining_armed_steps':self.steps.qsize()}
