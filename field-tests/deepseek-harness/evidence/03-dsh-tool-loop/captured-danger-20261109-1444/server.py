import http.server, json, os, uuid, threading
OUT=os.environ['OUT']; PORT=int(os.environ['PORT'])
os.makedirs(OUT, exist_ok=True)
n=0; lock=threading.Lock()
def sse(events):
  return ''.join(f"event: {ev}\ndata: {json.dumps(data,ensure_ascii=False)}\n\n" for ev,data in events).encode()
def stream_text(model,text):
  mid=f"msg_{uuid.uuid4().hex[:12]}"
  return sse([
    ("message_start",{"type":"message_start","message":{"id":mid,"type":"message","role":"assistant","content":[],"model":model,"stop_reason":None,"stop_sequence":None,"usage":{"input_tokens":12,"output_tokens":1}}}),
    ("content_block_start",{"type":"content_block_start","index":0,"content_block":{"type":"text","text":""}}),
    ("content_block_delta",{"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":text}}),
    ("content_block_stop",{"type":"content_block_stop","index":0}),
    ("message_delta",{"type":"message_delta","delta":{"stop_reason":"end_turn","stop_sequence":None},"usage":{"output_tokens":8}}),
    ("message_stop",{"type":"message_stop"}),
  ])
def stream_bash(model, command, description):
  mid=f"msg_{uuid.uuid4().hex[:12]}"; tid=f"toolu_{uuid.uuid4().hex[:10]}"
  partial=json.dumps({"description":description,"command":command},ensure_ascii=False)
  return sse([
    ("message_start",{"type":"message_start","message":{"id":mid,"type":"message","role":"assistant","content":[],"model":model,"stop_reason":None,"stop_sequence":None,"usage":{"input_tokens":40,"output_tokens":1}}}),
    ("content_block_start",{"type":"content_block_start","index":0,"content_block":{"type":"thinking","thinking":""}}),
    ("content_block_delta",{"type":"content_block_delta","index":0,"delta":{"type":"thinking_delta","thinking":"call"}}),
    ("content_block_stop",{"type":"content_block_stop","index":0}),
    ("content_block_start",{"type":"content_block_start","index":1,"content_block":{"type":"tool_use","id":tid,"name":"bash","input":{}}}),
    ("content_block_delta",{"type":"content_block_delta","index":1,"delta":{"type":"input_json_delta","partial_json":partial}}),
    ("content_block_stop",{"type":"content_block_stop","index":1}),
    ("message_delta",{"type":"message_delta","delta":{"stop_reason":"tool_use","stop_sequence":None},"usage":{"output_tokens":32}}),
    ("message_stop",{"type":"message_stop"}),
  ])
def has_tool_result(messages):
  for m in messages or []:
    c=m.get('content')
    if isinstance(c,list):
      for b in c:
        if isinstance(b,dict) and b.get('type')=='tool_result': return True
  return False
class H(http.server.BaseHTTPRequestHandler):
  def _h(self):
    global n
    ln=int(self.headers.get('content-length') or 0); raw=self.rfile.read(ln) if ln else b''
    with lock: n+=1; i=n
    body=json.loads(raw) if raw.startswith(b'{') else None
    open(f'{OUT}/req-{i:02d}.json','w').write(json.dumps({"method":self.command,"path":self.path,"headers":{k:('<redacted>' if k.lower() in ('authorization','x-api-key') else v) for k,v in self.headers.items()},"body_len":len(raw),"body":body},ensure_ascii=False,indent=1))
    model=(body or {}).get('model') or 'deepseek-flash'
    tools=(body or {}).get('tools'); messages=(body or {}).get('messages') or []
    if not tools: payload=stream_text(model,'title'); kind='title'
    elif has_tool_result(messages): payload=stream_text(model,'done'); kind='final'
    else: payload=stream_bash(model, os.environ['DSH_REPLAY_BASH'], os.environ.get('DSH_REPLAY_DESC','cmd')); kind='bash'
    open(f'{OUT}/resp-{i:02d}.meta.json','w').write(json.dumps({"kind":kind,"cmd":os.environ.get('DSH_REPLAY_BASH')},indent=1))
    self.send_response(200); self.send_header('content-type','text/event-stream'); self.end_headers(); self.wfile.write(payload)
  do_POST=do_GET=_h
  def log_message(self,*a): pass
http.server.ThreadingHTTPServer(('127.0.0.1',int(os.environ['PORT'])),H).serve_forever()
