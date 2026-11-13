#!/usr/bin/env python3
"""Minimal Anthropic Messages SSE replay for dsh tool-loop tests.
No outbound network. Records requests. Scripted responses:
  - no tools  -> short title text
  - has tool_result in messages -> final text answer
  - else -> one bash tool_use (echo hi)  [or read/write via ?mode=]
Env/CLI: PORT OUT_DIR [tool_name]
"""
import http.server, json, sys, os, time, uuid, threading

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 19001
OUT = sys.argv[2] if len(sys.argv) > 2 else "captured-replay"
TOOL = sys.argv[3] if len(sys.argv) > 3 else "bash"
os.makedirs(OUT, exist_ok=True)
n = 0
lock = threading.Lock()

def redacted_headers(h):
    return {k: ("<redacted>" if k.lower() in ("authorization", "x-api-key") else v) for k, v in h.items()}

def has_tool_result(messages):
    for m in messages or []:
        c = m.get("content")
        if isinstance(c, list):
            for b in c:
                if isinstance(b, dict) and b.get("type") == "tool_result":
                    return True
        elif isinstance(c, dict) and c.get("type") == "tool_result":
            return True
    return False

def tool_input(name):
    if name == "bash":
        return {"description": "Echo hi to stdout", "command": "echo hi"}
    if name == "read":
        return {"file_path": "package.json"}
    if name == "write":
        return {"file_path": "dsh-replay-probe.txt", "content": "hi-from-replay\n"}
    return {"description": "Echo hi", "command": "echo hi"}

def sse(events):
    buf = []
    for ev, data in events:
        buf.append(f"event: {ev}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n")
    return "".join(buf).encode()

def stream_text(model, text, stop="end_turn"):
    mid = f"msg_{uuid.uuid4().hex[:12]}"
    return sse([
        ("message_start", {"type":"message_start","message":{"id":mid,"type":"message","role":"assistant","content":[],"model":model,"stop_reason":None,"stop_sequence":None,"usage":{"input_tokens":12,"output_tokens":1}}}),
        ("content_block_start", {"type":"content_block_start","index":0,"content_block":{"type":"text","text":""}}),
        ("content_block_delta", {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":text}}),
        ("content_block_stop", {"type":"content_block_stop","index":0}),
        ("message_delta", {"type":"message_delta","delta":{"stop_reason":stop,"stop_sequence":None},"usage":{"output_tokens":max(1,len(text)//4)}}),
        ("message_stop", {"type":"message_stop"}),
    ])

def stream_tool_use(model, name, inp, with_thinking=True):
    mid = f"msg_{uuid.uuid4().hex[:12]}"
    tid = f"toolu_{uuid.uuid4().hex[:10]}"
    events = [
        ("message_start", {"type":"message_start","message":{"id":mid,"type":"message","role":"assistant","content":[],"model":model,"stop_reason":None,"stop_sequence":None,"usage":{"input_tokens":40,"output_tokens":1}}}),
    ]
    idx = 0
    if with_thinking:
        events += [
            ("content_block_start", {"type":"content_block_start","index":idx,"content_block":{"type":"thinking","thinking":""}}),
            ("content_block_delta", {"type":"content_block_delta","index":idx,"delta":{"type":"thinking_delta","thinking":"I will call the tool once."}}),
            ("content_block_stop", {"type":"content_block_stop","index":idx}),
        ]
        idx += 1
    partial = json.dumps(inp, ensure_ascii=False)
    events += [
        ("content_block_start", {"type":"content_block_start","index":idx,"content_block":{"type":"tool_use","id":tid,"name":name,"input":{}}}),
        ("content_block_delta", {"type":"content_block_delta","index":idx,"delta":{"type":"input_json_delta","partial_json":partial}}),
        ("content_block_stop", {"type":"content_block_stop","index":idx}),
        ("message_delta", {"type":"message_delta","delta":{"stop_reason":"tool_use","stop_sequence":None},"usage":{"output_tokens":32}}),
        ("message_stop", {"type":"message_stop"}),
    ]
    return sse(events)

class H(http.server.BaseHTTPRequestHandler):
    def _handle(self):
        global n
        ln = int(self.headers.get("content-length") or 0)
        raw = self.rfile.read(ln) if ln else b""
        with lock:
            n += 1
            i = n
        body = None
        try:
            body = json.loads(raw) if raw else None
        except Exception:
            body = raw.decode(errors="replace")
        meta = {
            "ts": time.time(),
            "method": self.command,
            "path": self.path,
            "headers": redacted_headers(self.headers),
            "body_len": len(raw),
            "body": body,
        }
        with open(f"{OUT}/req-{i:02d}.json", "w") as f:
            json.dump(meta, f, ensure_ascii=False, indent=1)
        # decide response
        model = (body or {}).get("model") if isinstance(body, dict) else "deepseek-flash"
        tools = (body or {}).get("tools") if isinstance(body, dict) else None
        messages = (body or {}).get("messages") if isinstance(body, dict) else []
        thinking = (body or {}).get("thinking") if isinstance(body, dict) else None
        want_stream = bool((body or {}).get("stream")) if isinstance(body, dict) else True

        if not tools:
            payload = stream_text(model or "deepseek-flash", "replay-title")
            kind = "title"
        elif has_tool_result(messages):
            payload = stream_text(model or "deepseek-flash", "tool loop done: saw tool_result")
            kind = "final"
        else:
            with_th = True
            if isinstance(thinking, dict) and thinking.get("type") == "disabled":
                with_th = False
            payload = stream_tool_use(model or "deepseek-flash", TOOL, tool_input(TOOL), with_thinking=with_th)
            kind = f"tool_use:{TOOL}"

        with open(f"{OUT}/resp-{i:02d}.meta.json", "w") as f:
            json.dump({"kind": kind, "bytes": len(payload), "stream": want_stream}, f, indent=1)
        with open(f"{OUT}/resp-{i:02d}.sse", "wb") as f:
            f.write(payload)

        self.send_response(200)
        self.send_header("content-type", "text/event-stream")
        self.send_header("cache-control", "no-cache")
        self.send_header("x-replay-kind", kind)
        self.end_headers()
        self.wfile.write(payload)

    do_POST = do_GET = _handle
    def log_message(self, fmt, *args):
        sys.stderr.write(f"[replay] {self.command} {self.path} {fmt%args}\n")

print(f"anthropic_replay on 127.0.0.1:{PORT} out={OUT} tool={TOOL}", flush=True)
http.server.ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
