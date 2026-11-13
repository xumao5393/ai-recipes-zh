#!/usr/bin/env python3
"""#12f Anthropic Messages SSE replay reporting a chosen usage.input_tokens per tool step,
to find where dsh auto-compaction fires. Local only (127.0.0.1), no outbound network.
argv: PORT OUT_DIR STEPS BYTES PT_CSV
 - tool-step k (k = tool_results already in history) reports input_tokens=PT[k] (last repeats)
 - env PT_AFTER: once any compaction happened, tool/final steps report this instead
 - request whose last user text contains 'compaction engine' -> kind=compaction, returns summary text
"""
import http.server, json, sys, os, time, uuid, threading
PORT=int(sys.argv[1]); OUT=sys.argv[2]; STEPS=int(sys.argv[3]); BYTES=int(sys.argv[4]); PT=[int(x) for x in sys.argv[5].split(",")]
PT_AFTER=int(os.environ["PT_AFTER"]) if os.environ.get("PT_AFTER") else None
os.makedirs(OUT,exist_ok=True); RAW=os.path.join(os.path.dirname(OUT),"_raw_"+os.path.basename(OUT)); os.makedirs(RAW,exist_ok=True)
n=0; lock=threading.Lock(); COMPACTED=0
def sse(evs): return "".join(f"event: {e}\ndata: {json.dumps(d,ensure_ascii=False)}\n\n" for e,d in evs).encode()
def start(model,pt): return ("message_start",{"type":"message_start","message":{"id":"msg_"+uuid.uuid4().hex[:12],"type":"message","role":"assistant","content":[],"model":model,"stop_reason":None,"stop_sequence":None,"usage":{"input_tokens":pt,"output_tokens":1}}})
def stream_text(model,text,pt):
    return sse([start(model,pt),("content_block_start",{"type":"content_block_start","index":0,"content_block":{"type":"text","text":""}}),
        ("content_block_delta",{"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":text}}),("content_block_stop",{"type":"content_block_stop","index":0}),
        ("message_delta",{"type":"message_delta","delta":{"stop_reason":"end_turn","stop_sequence":None},"usage":{"input_tokens":pt,"output_tokens":max(1,len(text)//4)}}),("message_stop",{"type":"message_stop"})])
def stream_tool(model,k,cmd,pt):
    return sse([start(model,pt),("content_block_start",{"type":"content_block_start","index":0,"content_block":{"type":"tool_use","id":"toolu_"+uuid.uuid4().hex[:10],"name":"bash","input":{}}}),
        ("content_block_delta",{"type":"content_block_delta","index":0,"delta":{"type":"input_json_delta","partial_json":json.dumps({"description":f"step {k}","command":cmd})}}),
        ("content_block_stop",{"type":"content_block_stop","index":0}),
        ("message_delta",{"type":"message_delta","delta":{"stop_reason":"tool_use","stop_sequence":None},"usage":{"input_tokens":pt,"output_tokens":32}}),("message_stop",{"type":"message_stop"})])
SUMMARY="## Objective\n- run the steps\n## Pending Jobs\n- (none)\n## Current Work\n- replay\n## Next Step\n- continue\n"
def blocks_text(c):
    if isinstance(c,str): return c
    return "\n".join(b.get("text","") for b in c or [] if isinstance(b,dict) and b.get("type")=="text")
def count_tr(msgs): return sum(1 for m in msgs if isinstance(m.get("content"),list) for b in m["content"] if isinstance(b,dict) and b.get("type")=="tool_result")
class H(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        global n,COMPACTED
        raw=self.rfile.read(int(self.headers.get("content-length") or 0))
        with lock: n+=1; i=n
        open(f"{RAW}/req-{i:03d}.json","wb").write(raw)
        body=json.loads(raw) if raw else {}
        msgs=body.get("messages") or []; tools=body.get("tools"); model=body.get("model","x")
        k=count_tr(msgs)
        last_user=next((blocks_text(m.get("content")) for m in reversed(msgs) if m.get("role")=="user"),"")
        all_user=" ".join(blocks_text(m.get("content")) for m in msgs if m.get("role")=="user")
        after=(COMPACTED>0 and PT_AFTER is not None)
        if "compaction engine" in last_user:
            COMPACTED+=1; kind="compaction"; payload=stream_text(model,SUMMARY,1000)
        elif not tools: kind="title"; payload=stream_text(model,"replay-title",12)
        elif k>=STEPS:
            pt=PT_AFTER if after else PT[min(k,len(PT)-1)]; kind=f"final(reported_pt={pt})"; payload=stream_text(model,f"done after {k} steps",pt)
        else:
            pt=PT_AFTER if after else PT[min(k,len(PT)-1)]; kind=f"tool#{k+1}(reported_pt={pt})"
            payload=stream_tool(model,k+1,f"python3 -c \"print('S{k+1}'+'x'*{BYTES})\"",pt)
        meta={"i":i,"ts":time.time(),"path":self.path,"body_len":len(raw),"kind":kind,"n_messages":len(msgs),"tool_results_in_history":k,
              "roles":[m.get("role") for m in msgs],"tools_n":len(tools or []),"max_tokens":body.get("max_tokens"),
              "has_checkpoint":"<compacted-summary>" in all_user,"last_user_head":last_user[:120],"top_keys":sorted(body.keys())}
        json.dump(meta,open(f"{OUT}/req-{i:03d}.meta.json","w"),ensure_ascii=False,indent=1)
        self.send_response(200); self.send_header("content-type","text/event-stream"); self.end_headers(); self.wfile.write(payload)
    def do_GET(self):
        with lock: open(f"{OUT}/GET.log","a").write(self.path+"\n")
        self.send_response(404); self.end_headers()
    def log_message(self,*a): pass
print("anthropic-compaction-probe",PORT,os.path.basename(OUT),STEPS,BYTES,PT,"PT_AFTER=",PT_AFTER,flush=True)
http.server.ThreadingHTTPServer(("127.0.0.1",PORT),H).serve_forever()
