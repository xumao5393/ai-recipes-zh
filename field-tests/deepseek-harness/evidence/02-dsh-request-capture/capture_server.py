# 最小抓包服务：记录 dsh 发往 DEEPSEEK_BASE_URL 的请求（不转发、不联网），回 401 让其结束。
import http.server, json, sys, os, time
OUT = sys.argv[2] if len(sys.argv) > 2 else "captured"
os.makedirs(OUT, exist_ok=True)
n = 0
class H(http.server.BaseHTTPRequestHandler):
    def _h(self):
        global n
        n += 1
        ln = int(self.headers.get("content-length") or 0)
        body = self.rfile.read(ln) if ln else b""
        hdr = {k: ("<redacted>" if k.lower() in ("authorization", "x-api-key") else v) for k, v in self.headers.items()}
        with open(f"{OUT}/req-{n:02d}.json", "w") as f:
            json.dump({"method": self.command, "path": self.path, "headers": hdr, "body_len": len(body),
                       "body": (json.loads(body) if body.startswith(b"{") else body.decode(errors="replace"))}, f, ensure_ascii=False, indent=1)
        self.send_response(401); self.send_header("content-type", "application/json"); self.end_headers()
        self.wfile.write(b'{"type":"error","error":{"type":"authentication_error","message":"capture-only mock"}}')
    do_POST = do_GET = _h
    def log_message(self, *a): pass
http.server.ThreadingHTTPServer(("127.0.0.1", int(sys.argv[1])), H).serve_forever()
