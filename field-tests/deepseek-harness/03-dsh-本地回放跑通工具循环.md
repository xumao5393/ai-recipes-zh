# 03 · 本地 Anthropic 回放服务让 dsh 真跑完一轮工具调用（实测）

状态：已实测（2026-11-09 14:30–14:33 EST；14:43 按审核收窄结论并补证据说明）。证据：`evidence/03-dsh-tool-loop/`。回放脚本：`tools/anthropic_replay_server.py`（副本也在证据目录）。

## 方法
没有 DEEPSEEK_API_KEY，也没有装 ollama/大模型下载。自写最小 **Anthropic Messages SSE** 回放服务（`POST /v1/messages`，`stream: true`）：
- 首轮（有 tools、无 tool_result）→ 回一个 `tool_use`（bash / read / write 可切换）；
- 收到 `tool_result` 后 → 回最终文本；
- 无 tools 的标题请求 → 回短标题。

`DEEPSEEK_BASE_URL=http://127.0.0.1:19001 DEEPSEEK_API_KEY=dummy-replay`，加隐私补丁（关 session-log / plugin-inventory / otel），`HOME=/tmp/dshhome`，在 `evidence/03-dsh-tool-loop/workdir` 下跑 `dsh headless --json ...`。

未叠加 ollama/llama.cpp：避免大下载卡住。**未连接 DeepSeek 官方端点**；下列结论只适用于「dsh ↔ 本回放服务」。

## 证据目录说明
- `captured/`：Run A 与 Run B **混在同一目录**（同一次回放服务连续写入）。归属见 `captured/RUN-MAP.md`：req-01..03=A，req-04..06=B。
- `captured-write/`、`captured-read/`、`captured-outside/`：分别为 C / D / E。
- `captured-outside/req-01.json` 是 **curl 自测**（见该目录 `NOTE.md`），不是 dsh 请求。
- `captured-danger-20261109-1444/F-curl-local/req-03.json` 是工具循环里那条 `curl` 命令自己打到回放服务上的 **GET /**（User-Agent `curl/8.14.1`），不是 dsh 的模型请求（见该目录 `NOTE.md`）。同目录模型请求为 req-01/02/04 共 3 次。

## 实测结果（各条件 n=1）

### A. bash `echo hi` + `--permission-mode danger-full-access --approval-policy never`
- 耗时 **1.765 s**，退出码 **0**（`runA.txt`）。
- 事件：`thinking` → `tool_call bash {command: echo hi}` → `tool_result status=completed result="hi\n"` → 最终文本 → `turn_end completed`。
- 模型侧 3 次 `/v1/messages`（body_len 约 22,599 / 770 / 22,957，隐私补丁已开）。

### B. bash `echo hi`，默认权限（未显式传 permission-mode）
- 耗时 **1.437 s**，退出码 **0**（`runB.txt`）。
- 同样得到 `tool_result completed "hi\n"`。  
- **仅就本次 `echo hi`（n=1）**：未观察到审批通道介入。不能据此推断「所有工作区内 bash 都不审批」。

### C. write → `dsh-replay-probe.txt`（`--permission-mode workspace-write`）
- 耗时 **1.415 s**，退出码 **0**。
- 文件落地，内容 `hi-from-replay\n`（15 字节，模式 `600`）。本次写工作区内该文件未触发审批（n=1）。

### D. read → `package.json`
- 耗时 **1.425 s**，退出码 **0**。
- 返回带行号内容：`1: {"name":"probe"}`。本次读该文件未触发审批（n=1）。

### E. 工作区外 write + `sandbox_permissions: danger-full-access`（`--permission-mode workspace-write --approval-policy ask`）
- 耗时 **1.877 s**，退出码 **0**（循环完成，工具结果为错误）。
- `tool_result status=error`：`Error: sandbox escalation to "danger-full-access" requires approval, but no approval channel is available`。
- `/tmp/dsh-outside-probe.txt` **未创建**。


### F. 补充危险向命令（新目录 `captured-danger-20261109-1444/`，各 n=1，`--permission-mode workspace-write`）
1. **`rm -f deleteme.txt && ls ...`（工作区内）**：`tool_result completed`；`deleteme.txt` 确实被删，`keep.txt` 仍在。**本次未触发审批。**
2. **`curl -sS -m 2 http://127.0.0.1:19011/`（本机回放端口，非外网）**：`tool_result completed`，拿到回放服务的 SSE 文本。**本次未触发审批。** 不是外网访问实测。
3. **`echo outside-bash > /tmp/dsh-bash-outside.txt; ls -la ...`**：工具结果里 `ls` 显示文件存在（13 字节），但命令结束后在宿主机 `/tmp` **找不到该文件**（`F-bash-write-outside/host-ls-after.txt`）。可能是沙箱私有挂载/临时视图，**不能**据此说「已经写进了宿主机 /tmp」；也**没有**出现审批文案。机制未深挖。

## 关键发现（收窄后）
1. **dsh 接受本回放服务返回的标准 Anthropic SSE**（含可选 `thinking` + `tool_use` + `input_json_delta`），并能完成工具循环。**DeepSeek 官方 Messages 端点的真实字节流未测，不能从本实验推出「官方协议就是这样」。**
2. 上述 5 次 headless 端到端耗时约 **1.4–1.9 s**，服务端是假的、每种条件各 n=1，**不能当成真实模型使用时的耗时参考**。
3. 权限（仅实测样本）：`echo hi`、读 `package.json`、写工作区内探针文件、工作区内 `rm`、对本机端口 `curl`，各 n=1 均未出现审批文案；工具 `write` 带 `sandbox_permissions` 升权在 headless 无审批通道时被拒绝。bash 重定向写 `/tmp` 的宿主机可见性未证实（见 F.3）。
4. 隐私补丁下首轮请求体约 **22.6–22.8 KB**（24 个工具），与 #02 对照一致量级。

## 未做
- 未装 ollama / llama.cpp，未跑真本地小模型。
- 未测 TUI 交互式审批。
- 未测真 DeepSeek API key / 官方端点。
- 外网真实 `curl`、TUI 审批点选仍未测。
