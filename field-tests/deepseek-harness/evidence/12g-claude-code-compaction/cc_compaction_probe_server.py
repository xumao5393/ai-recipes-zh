#!/usr/bin/env python3
"""#12g Claude Code compaction probe: Anthropic Messages SSE replay (127.0.0.1 only, no outbound network).
argv: PORT OUT_DIR STEPS BYTES PT_CSV
 - tool step k (k = tool_results in history) reports usage.input_tokens=PT[k] (last value repeats)
 - env PT_AFTER: after any compaction request, report this instead
 - env CT: value returned for /v1/messages/count_tokens (default 1000)
 - compaction request = no Bash tool use expected: detected when last user text mentions 'summary' and
   (no tools or text contains 'summar'); returns a summary text. Every request's meta is recorded.
"""
import http.server, json, sys, os, time, uuid, threading
PORT=int(sys.argv[1]); OUT=sys.argv[2]; STEPS=int(sys.argv[3]); BYTES=int(sys.argv[4]); PT=[int(x) for x in sys.argv[5].split(",")]
PT_AFTER=int(os.environ["PT_AFTER"]) if os.environ.get("PT_AFTER") else None
CT=int(os.environ.get("CT","1000"))
os.makedirs(OUT,exist_ok=True); RAW=os.path.join(os.path.dirname(OUT),"_raw_"+os.path.basename(OUT)); os.makedirs(RAW,exist_ok=True)
n=0; lock=threading.Lock(); COMPACTED=0
def sse(evs): return "".join(f"event: {e}\ndata: {json.dumps(d,ensure_ascii=False)}\n\n" for e,d in evs).encode()
def start(model,pt): return ("message_start",{"type":"message_start","message":{"id":"msg_"+uuid.uuid4().hex[:12],"type":"message","role":"assistant","content":[],"model":model,"stop_reason":None,"stop_sequence":None,"usage":{"input_tokens":pt,"output_tokens":1,"cache_read_input_tokens":0,"cache_creation_input_tokens":0}}})
def end(stop,pt,out): return [("message_delta",{"type":"message_delta","delta":{"stop_reason":stop,"stop_sequence":None},"usage":{"input_tokens":pt,"output_tokens":out,"cache_read_input_tokens":0,"cache_creation_input_tokens":0}}),("message_stop",{"type":"message_stop"})]
def stream_text(model,text,pt):
    return sse([start(model,pt),("content_block_start",{"type":"content_block_start","index":0,"content_block":{"type":"text","text":""}}),
        ("content_block_delta",{"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":text}}),("content_block_stop",{"type":"content_block_stop","index":0})]+end("end_turn",pt,max(1,len(text)//4)))
def stream_tool(model,k,cmd,pt):
    return sse([start(model,pt),("content_block_start",{"type":"content_block_start","index":0,"content_block":{"type":"tool_use","id":"toolu_"+uuid.uuid4().hex[:10],"name":"Bash","input":{}}}),
        ("content_block_delta",{"type":"content_block_delta","index":0,"delta":{"type":"input_json_delta","partial_json":json.dumps({"command":cmd,"description":f"step {k}"})}}),
        ("content_block_stop",{"type":"content_block_stop","index":0})]+end("tool_use",pt,32))
SUMMARY="<summary>\n1. Primary Request: run the steps.\n2. Current Work: replay steps.\n3. Next Step: continue running the remaining steps.\n</summary>"
def blocks_text(c):
    if isinstance(c,str): return c
    return "\n".join(b.get("text","") for b in c or [] if isinstance(b,dict) and b.get("type")=="text")
def count_tr(msgs): return sum(1 for m in msgs if isinstance(m.get("content"),list) for b in m["content"] if isinstance(b,dict) and b.get("type")=="tool_result")
class H(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        global n,COMPACTED
        raw=self.rfile.read(int(self.headers.get("content-length") or 0))
        with lock: n+=1; i=n
        open(f"{RAW}/req-{i:04d}.json","wb").write(raw)
        body=json.loads(raw) if raw else {}
        msgs=body.get("messages") or []; tools=body.get("tools") or []; model=body.get("model","x")
        k=count_tr(msgs)
        last_user=next((blocks_text(m.get("content")) for m in reversed(msgs) if m.get("role")=="user"),"")
        all_user=" ".join(blocks_text(m.get("content")) for m in msgs if m.get("role")=="user")
        has_bash=any(t.get("name")=="Bash" for t in tools)
        after=(COMPACTED>0 and PT_AFTER is not None)
        if "count_tokens" in self.path:
            kind="count_tokens"; payload=json.dumps({"input_tokens":CT}).encode(); ctype="application/json"
        else:
            ctype="text/event-stream"
            if ("summary" in last_user.lower() and "conversation" in last_user.lower()) :
                COMPACTED+=1; kind="compaction"; payload=stream_text(model,SUMMARY,1000)
            elif not has_bash: kind="aux"; payload=stream_text(model,"replay-aux",12)
            elif k>=STEPS:
                pt=PT_AFTER if after else PT[min(k,len(PT)-1)]; kind=f"final(pt={pt})"; payload=stream_text(model,f"done after {k} steps",pt)
            else:
                pt=PT_AFTER if after else PT[min(k,len(PT)-1)]; kind=f"tool#{k+1}(pt={pt})"
                payload=stream_tool(model,k+1,f"python3 -c \"print('S{k+1}'+'x'*{BYTES})\"",pt)
        meta={"i":i,"ts":time.time(),"path":self.path,"body_len":len(raw),"kind":kind,"n_messages":len(msgs),"tool_results_in_history":k,
              "roles":[m.get("role") for m in msgs],"tools_n":len(tools),"max_tokens":body.get("max_tokens"),
              "compacted_so_far":COMPACTED,"last_user_head":last_user[:160],"first_user_head":(blocks_text(msgs[0].get("content"))[:160] if msgs else ""),"top_keys":sorted(body.keys()),"anthropic_beta":self.headers.get("anthropic-beta")}
        json.dump(meta,open(f"{OUT}/req-{i:04d}.meta.json","w"),ensure_ascii=False,indent=1)
        self.send_response(200); self.send_header("content-type",ctype); self.end_headers(); self.wfile.write(payload)
    def do_GET(self):
        with lock: open(f"{OUT}/GET.log","a").write(self.path+"\n")
        self.send_response(404); self.end_headers()
    def log_message(self,*a): pass
print("cc-compaction-probe",PORT,os.path.basename(OUT),STEPS,BYTES,PT,"PT_AFTER=",PT_AFTER,"CT=",CT,flush=True)
http.server.ThreadingHTTPServer(("127.0.0.1",PORT),H).serve_forever()
