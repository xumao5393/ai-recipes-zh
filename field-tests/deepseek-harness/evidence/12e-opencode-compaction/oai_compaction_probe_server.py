#!/usr/bin/env python3
"""#12e OpenAI chat-completions replay that reports a chosen usage.prompt_tokens per response,
to find where OpenCode auto-compaction fires. Local only (127.0.0.1), no outbound network.
argv: PORT OUT_DIR STEPS BYTES PROMPT_TOKENS_CSV
 - tool-step responses report prompt_tokens from CSV (index = tool step, last value repeats)
 - env PT_AFTER: once any compaction happened, tool steps report this value instead
 - a request whose last user message contains 'summarize' (case-insens.) is classed 'compaction' and gets a summary text
"""
import http.server, json, sys, os, time, threading
PORT=int(sys.argv[1]); OUT=sys.argv[2]; STEPS=int(sys.argv[3]); BYTES=int(sys.argv[4]); PT=[int(x) for x in sys.argv[5].split(",")]
os.makedirs(OUT,exist_ok=True); RAW=os.path.join(os.path.dirname(OUT),"_raw_"+os.path.basename(OUT)); os.makedirs(RAW,exist_ok=True)
n=0; lock=threading.Lock(); COMPACTED=0; PT_AFTER=int(os.environ["PT_AFTER"]) if os.environ.get("PT_AFTER") else None
def chunk(d): return ("data: "+json.dumps(d)+"\n\n").encode()
def base(model,delta,fin=None): return {"id":"chatcmpl-replay","object":"chat.completion.chunk","created":int(time.time()),"model":model,"choices":[{"index":0,"delta":delta,"finish_reason":fin}]}
def usage(model,pt): return chunk({"id":"chatcmpl-replay","object":"chat.completion.chunk","created":int(time.time()),"model":model,"choices":[],"usage":{"prompt_tokens":pt,"completion_tokens":10,"total_tokens":pt+10}})
def text_stream(model,txt,pt=1):
    return chunk(base(model,{"role":"assistant","content":""}))+chunk(base(model,{"content":txt}))+chunk(base(model,{},"stop"))+usage(model,pt)+b"data: [DONE]\n\n"
def tool_stream(model,k,args,pt):
    a=json.dumps(args)
    return (chunk(base(model,{"role":"assistant","content":None,"tool_calls":[{"index":0,"id":f"call_{k}","type":"function","function":{"name":"shell","arguments":""}}]}))
        +chunk(base(model,{"tool_calls":[{"index":0,"function":{"arguments":a}}]}))+chunk(base(model,{},"tool_calls"))+usage(model,pt)+b"data: [DONE]\n\n")
SUMMARY="## Objective\n- run the steps\n## Requirements\n- (none)\n## Decisions\n- (none)\n## Work State\n- replay\n## Next Move\n- continue\n"
def txt(c): return c if isinstance(c,str) else json.dumps(c,ensure_ascii=False)
class H(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        global n, COMPACTED
        raw=self.rfile.read(int(self.headers.get("content-length") or 0))
        with lock: n+=1; i=n
        open(f"{RAW}/req-{i:02d}.json","wb").write(raw)
        body=json.loads(raw) if raw else {}
        msgs=body.get("messages") or []; tools=body.get("tools") or []
        k=sum(1 for m in msgs if m.get("role")=="tool"); model=body.get("model","x")
        last_user=next((txt(m.get("content")) for m in reversed(msgs) if m.get("role")=="user"),"")
        if "summarize" in last_user.lower() or "consolidated summary" in last_user.lower():
            kind="compaction"; COMPACTED+=1; payload=text_stream(model,SUMMARY,1000)
        elif not tools: kind="title"; payload=text_stream(model,"replay-title")
        elif k>=STEPS: kind="final"; payload=text_stream(model,f"done after {k} steps",PT[min(k,len(PT)-1)])
        else:
            pt=PT[min(k,len(PT)-1)] if not (COMPACTED and PT_AFTER is not None) else PT_AFTER; kind=f"tool#{k+1}(reported_pt={pt})"
            payload=tool_stream(model,k+1,{"command":f"python3 -c \"print('S{k+1}'+'x'*{BYTES})\""},pt)
        meta={"i":i,"ts":time.time(),"path":self.path,"body_len":len(raw),"kind":kind,"n_messages":len(msgs),"tool_msgs":k,
              "roles":[m.get("role") for m in msgs],"tools_n":len(tools),"last_user_head":last_user[:160],"max_tokens":body.get("max_tokens"),
              "extra_keys":sorted(kk for kk in body if kk not in("messages","tools"))}
        json.dump(meta,open(f"{OUT}/req-{i:02d}.meta.json","w"),ensure_ascii=False,indent=1)
        self.send_response(200); self.send_header("content-type","text/event-stream"); self.end_headers(); self.wfile.write(payload)
    def do_GET(self): self.send_response(404); self.end_headers()
    def log_message(self,*a): pass
print("oai-compaction-probe",PORT,OUT,STEPS,BYTES,PT,flush=True)
http.server.ThreadingHTTPServer(("127.0.0.1",PORT),H).serve_forever()
