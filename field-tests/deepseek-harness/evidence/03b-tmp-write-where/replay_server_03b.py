#!/usr/bin/env python3
"""03b replay: first bash=diag write+sleep; after tool_result -> second bash=read; then text."""
import http.server, json, sys, os, uuid, threading

PORT = int(sys.argv[1])
OUT = sys.argv[2]
MARKER = sys.argv[3]
SLEEP_S = sys.argv[4] if len(sys.argv) > 4 else "12"
os.makedirs(OUT, exist_ok=True)
n = 0
lock = threading.Lock()
tool_rounds = 0  # how many tool_result rounds seen in current... actually count tool_results in messages

def redacted_headers(h):
    return {k: ("<redacted>" if k.lower() in ("authorization", "x-api-key") else v) for k, v in h.items()}

def count_tool_results(messages):
    c = 0
    for m in messages or []:
        content = m.get("content")
        if isinstance(content, list):
            for b in content:
                if isinstance(b, dict) and b.get("type") == "tool_result":
                    c += 1
        elif isinstance(content, dict) and content.get("type") == "tool_result":
            c += 1
    return c

def has_tools(body):
    return bool(body.get("tools"))

CMD1 = (
    f"MARK='{MARKER}'; "
    f"F=/tmp/dsh03b-$MARK.txt; "
    f"echo \"$MARK\" > \"$F\"; "
    f"echo HOST_PID=$$; "
    f"echo NS_MNT=$(readlink /proc/self/ns/mnt 2>/dev/null || echo NA); "
    f"echo TMPDIR_VAL=${{TMPDIR:-UNSET}}; "
    f"echo ID=$(id); "
    f"echo DF_TMP; df -h /tmp 2>&1 | sed -n '1,3p'; "
    f"echo MOUNTINFO_TMP; "
    f"awk '$5==\"/tmp\" || $5 ~ /^\\/tmp\\// {{print}}' /proc/self/mountinfo 2>/dev/null || true; "
    f"echo LS; ls -la \"$F\"; "
    f"echo REALPATH=$(readlink -f \"$F\" 2>/dev/null || echo NA); "
    f"echo SLEEP; sleep {SLEEP_S}; "
    f"echo AFTER_SLEEP; ls -la \"$F\""
)

CMD2 = (
    f"MARK='{MARKER}'; F=/tmp/dsh03b-$MARK.txt; "
    f"echo READBACK; ls -la \"$F\" 2>&1; "
    f"echo CONTENT; cat \"$F\" 2>&1; "
    f"echo NS_MNT=$(readlink /proc/self/ns/mnt 2>/dev/null || echo NA); "
    f"echo HOST_PID=$$"
)

def sse(events):
    buf = []
    for ev, data in events:
        buf.append(f"event: {ev}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n")
    return "".join(buf).encode()

def stream_text(model, text):
    mid = f"msg_{uuid.uuid4().hex[:12]}"
    return sse([
        ("message_start", {"type":"message_start","message":{"id":mid,"type":"message","role":"assistant","content":[],"model":model,"stop_reason":None,"stop_sequence":None,"usage":{"input_tokens":12,"output_tokens":1}}}),
        ("content_block_start", {"type":"content_block_start","index":0,"content_block":{"type":"text","text":""}}),
        ("content_block_delta", {"type":"content_block_delta","index":0,"delta":{"type":"text_delta","text":text}}),
        ("content_block_stop", {"type":"content_block_stop","index":0}),
        ("message_delta", {"type":"message_delta","delta":{"stop_reason":"end_turn","stop_sequence":None},"usage":{"output_tokens":8}}),
        ("message_stop", {"type":"message_stop"}),
    ])

def stream_tool(model, name, inp):
    mid = f"msg_{uuid.uuid4().hex[:12]}"
    tid = f"toolu_{uuid.uuid4().hex[:10]}"
    partial = json.dumps(inp, ensure_ascii=False)
    return sse([
        ("message_start", {"type":"message_start","message":{"id":mid,"type":"message","role":"assistant","content":[],"model":model,"stop_reason":None,"stop_sequence":None,"usage":{"input_tokens":40,"output_tokens":1}}}),
        ("content_block_start", {"type":"content_block_start","index":0,"content_block":{"type":"thinking","thinking":""}}),
        ("content_block_delta", {"type":"content_block_delta","index":0,"delta":{"type":"thinking_delta","thinking":"probe"}}),
        ("content_block_stop", {"type":"content_block_stop","index":0}),
        ("content_block_start", {"type":"content_block_start","index":1,"content_block":{"type":"tool_use","id":tid,"name":name,"input":{}}}),
        ("content_block_delta", {"type":"content_block_delta","index":1,"delta":{"type":"input_json_delta","partial_json":partial}}),
        ("content_block_stop", {"type":"content_block_stop","index":1}),
        ("message_delta", {"type":"message_delta","delta":{"stop_reason":"tool_use","stop_sequence":None},"usage":{"output_tokens":32}}),
        ("message_stop", {"type":"message_stop"}),
    ])

class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass
    def do_POST(self):
        global n
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length)
        try:
            body = json.loads(raw.decode() or "{}")
        except Exception:
            body = {}
        with lock:
            n += 1
            i = n
            open(f"{OUT}/req-{i:02d}.json","w").write(json.dumps({
                "method":"POST","path":self.path,
                "headers": redacted_headers(dict(self.headers)),
                "body_len": len(raw), "body": body
            }, ensure_ascii=False, indent=1))
        model = body.get("model") or "deepseek-flash"
        if not has_tools(body):
            payload = stream_text(model, "title")
        else:
            tr = count_tool_results(body.get("messages"))
            if tr == 0:
                payload = stream_tool(model, "bash", {"description":"03b diag write sleep","command": CMD1})
            elif tr == 1:
                payload = stream_tool(model, "bash", {"description":"03b readback","command": CMD2})
            else:
                payload = stream_text(model, "03b-done")
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

if __name__ == "__main__":
    http.server.ThreadingHTTPServer(("127.0.0.1", PORT), H).serve_forever()
