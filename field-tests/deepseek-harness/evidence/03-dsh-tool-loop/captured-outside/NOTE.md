# captured-outside 说明（补记，2026-11-09 14:43 EST）

- `req-01.json`：**curl 自测**（启动回放服务后的 smoke），User-Agent 为 curl，body_len=113，tools 仅 1 个占位；**不是** dsh 发出的请求。
- `req-02` 起才是 Run E（dsh headless 工作区外 write + sandbox_permissions 升权）。
