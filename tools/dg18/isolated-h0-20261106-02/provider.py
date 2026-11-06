"""Closed loopback Responses transport; all response content is emulated."""
import http.server
import json
import queue
import threading
import time
from pathlib import Path

class Provider:
 def __init__(self,root):
  self.root=Path(root);self.root.mkdir(mode=0o700);self.steps=queue.Queue();self.requests=[];self.lock=threading.Lock();self.handlers=set();self.closed=False
  self.route=lambda request:self.steps.get(timeout=10)
  outer=self
  class Handler(http.server.BaseHTTPRequestHandler):
   def log_message(self,*args):pass
   def do_POST(self):
    thread=threading.current_thread()
    with outer.lock:outer.handlers.add(thread)
    try:
     self.connection.settimeout(240)
     size=self.headers.get('Content-Length','')
     if not size.isdecimal() or not 0<int(size)<=2*1024*1024 or self.path!='/v1/responses':raise ValueError('PROVIDER_REQUEST_BOUND')
     raw=self.rfile.read(int(size));request=json.loads(raw)
     with outer.lock:
      if outer.closed or len(outer.requests)>=32:raise ValueError('PROVIDER_REQUEST_POPULATION')
      outer.requests.append(request);number=len(outer.requests)
      (outer.root/('request-%03d.json'%number)).write_bytes(raw)
     step=outer.route(request)
     if type(step) is not dict or step.get('type','text') not in ('text','function'):raise ValueError('PROVIDER_STEP_SHAPE')
     rid='resp_h0_mechanical_'+str(number);itemid='msg_h0_mechanical_'+str(number)
     if step.get('type')=='function':
      if set(step)!={'type','namespace','name','arguments'}:raise ValueError('PROVIDER_FUNCTION_SHAPE')
      item={'type':'function_call','id':'fc_'+str(number),'call_id':'call_'+str(number),'namespace':step['namespace'],'name':step['name'],'arguments':json.dumps(step['arguments'])}
     else:
      text=step['text']
      if type(text) is not str or len(text.encode())>256*1024:raise ValueError('PROVIDER_TEXT_BOUND')
      item={'type':'message','id':itemid,'role':'assistant','status':'completed','content':[{'type':'output_text','text':text,'annotations':[]}]}
     events=[('response.created',{'response':{'id':rid,'object':'response','status':'in_progress','output':[]}}),('response.output_item.added',{'output_index':0,'item':item})]
     if step.get('type')!='function':
      events += [('response.content_part.added',{'item_id':itemid,'output_index':0,'content_index':0,'part':{'type':'output_text','text':'','annotations':[]}}),('response.output_text.delta',{'item_id':itemid,'output_index':0,'content_index':0,'delta':text}),('response.output_text.done',{'item_id':itemid,'output_index':0,'content_index':0,'text':text})]
     events += [('response.output_item.done',{'output_index':0,'item':item}),('response.completed',{'response':{'id':rid,'object':'response','status':'completed','output':[item],'usage':{'input_tokens':1,'output_tokens':1,'total_tokens':2}}})]
     wire=''.join('event: '+name+'\ndata: '+json.dumps({'type':name,**value})+'\n\n' for name,value in events).encode()
     if len(wire)>2*1024*1024:raise ValueError('PROVIDER_RESPONSE_BOUND')
     self.send_response(200);self.send_header('Content-Type','text/event-stream');self.send_header('Connection','close');self.end_headers();self.wfile.write(wire);self.wfile.flush()
    except Exception:
     try:self.send_error(503,'Closed emulated provider refused')
     except (BrokenPipeError,ConnectionResetError,OSError):pass
    finally:
     with outer.lock:outer.handlers.discard(thread)
  self.server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);self.server.daemon_threads=True
  self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
 @property
 def url(self):return 'http://127.0.0.1:'+str(self.server.server_port)+'/v1'
 def arm(self,*steps):
  for step in steps:self.steps.put(step)
 def close(self):
  self.closed=True;self.server.shutdown();self.server.server_close();self.thread.join(timeout=3);deadline=time.monotonic()+3
  for thread in tuple(self.handlers):thread.join(timeout=max(0,deadline-time.monotonic()))
  return {'listener_closed':not self.thread.is_alive(),'handlers_joined':not self.handlers,'request_count':len(self.requests),'emulated_provider':True}
