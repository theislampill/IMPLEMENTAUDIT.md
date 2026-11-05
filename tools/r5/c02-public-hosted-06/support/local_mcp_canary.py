#!/usr/bin/env python3
"""Emulated cua_repl MCP endpoint in an isolated Codex home; never invokes CUA."""
import argparse,json,os,sys,time
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--log',type=Path,required=True);a=p.parse_args()
def record(value):
 with a.log.open('a',encoding='utf-8') as f:
  f.write(json.dumps({'ns':time.time_ns(),'emulated_service':'local-cua-turn-ended-canary','request':value},sort_keys=True)+'\n');f.flush();os.fsync(f.fileno())
for line in sys.stdin:
 req=json.loads(line);record(req)
 if 'id' not in req:continue
 m=req.get('method')
 if m=='initialize':result={'protocolVersion':req.get('params',{}).get('protocolVersion','2024-11-05'),'capabilities':{'tools':{}},'serverInfo':{'name':'dg17-local-mcp-canary','version':'1'}}
 elif m=='tools/list':result={'tools':[{'name':'turn_ended','description':'Local deterministic canary acknowledgment. Does not contact or control a browser.','inputSchema':{'type':'object','properties':{'hook_event_name':{'type':'string'},'session_id':{'type':'string'},'turn_id':{'type':'string'}},'additionalProperties':True}}]}
 elif m=='tools/call':result={'content':[{'type':'text','text':json.dumps({'systemMessage':'DG17_LOCAL_MCP_CANARY_ACK'})}],'isError':False}
 elif m=='ping':result={}
 else:
  print(json.dumps({'jsonrpc':'2.0','id':req['id'],'error':{'code':-32601,'message':'Unsupported local canary method'}}),flush=True);continue
 print(json.dumps({'jsonrpc':'2.0','id':req['id'],'result':result}),flush=True)
