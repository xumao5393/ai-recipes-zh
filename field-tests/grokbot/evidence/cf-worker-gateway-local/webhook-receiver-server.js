const http = require("http");
const fs = require("fs");
const path = require("path");
const out = process.env.WAKE_LOG || "/tmp/cf-worker-outside-repo/wake-log.jsonl";
let count = 0;
const server = http.createServer((req, res) => {
  if (req.method === "POST" && req.url === "/wake") {
    let body = "";
    req.on("data", (c) => (body += c));
    req.on("end", () => {
      count += 1;
      const line = JSON.stringify({ n: count, at: new Date().toISOString(), body: JSON.parse(body || "{}") });
      fs.appendFileSync(out, line + "\n");
      res.writeHead(200, { "content-type": "application/json" });
      res.end(JSON.stringify({ ok: true, count }));
    });
    return;
  }
  if (req.url === "/count") {
    res.writeHead(200, { "content-type": "application/json" });
    res.end(JSON.stringify({ count }));
    return;
  }
  res.writeHead(404);
  res.end();
});
server.listen(8788, "127.0.0.1", () => console.log("wake receiver on 127.0.0.1:8788 log="+out));
