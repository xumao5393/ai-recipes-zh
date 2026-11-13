# F-curl-local 抓包说明（补记，2026-11-09 14:50 EST America/New_York）

本目录共 4 个 `req-*.json`，**其中 `req-03.json` 不是 dsh 的模型请求**。

## req-03.json
- 来源：dsh 工具循环里执行的 bash 命令 `curl -sS -m 2 http://127.0.0.1:19011/ || true` 打到本机回放服务上的 **GET**。
- 证据字段（原文）：
  - `method`: `GET`
  - `path`: `/`
  - `headers.User-Agent`: `curl/8.14.1`
  - `body_len`: `0`
- 因此它是 **curl 客户端**对回放端口的探测，不是 `POST /v1/messages`。

## 其余请求（模型侧）
| 文件 | method | path | 说明 |
|---|---|---|---|
| req-01.json | POST | /v1/messages | dsh 首轮（含 tools） |
| req-02.json | POST | /v1/messages | dsh 续轮（tool_result 前/中） |
| req-04.json | POST | /v1/messages | dsh 收到 tool_result 后的续轮 |

合计：**3 次** dsh 模型请求 + **1 次** curl GET，不是 4 次模型请求。
