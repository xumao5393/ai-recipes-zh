# 06 · OpenCode 指向 DeepSeek 风格端点的请求形状（本地抓包实测）

状态：已实测（2026-11-09 14:47 EST）。证据：`evidence/06-opencode/capture-sayhi-20261109-1447/`（n=1）。  
**不是真 DeepSeek key**：`providers.deepseek.settings.baseURL` 指到本机抓包服务（回 401）。

## 方法
- 已装 `@opencode/cli@2.2.6`（`sandbox-opencode/`，**992M**（`evidence/06-opencode/npm-install.txt` 中 `du` 行）；先前一轮）。
- `HOME=/tmp/ochome`
- 配置 `~/.config/opencode/opencode.json`（副本在证据目录）：
  - `model: deepseek/deepseek-flash`（列表里没有 `deepseek-chat`，改用已列出的 flash）
  - `providers.deepseek.settings.baseURL: http://127.0.0.1:19016/v1`
  - `headerTimeout`/`chunkTimeout`: 5000（缩短失败等待）
- `DEEPSEEK_API_KEY=dummy-capture`
- 命令：`opencode --standalone run --format json --auto --model deepseek/deepseek-flash "say hi"`
- 抓包：`tools/capture_server.py`（只记录、回 401）

## 实测结果（n=1）
1. **0.985 s** 退出码 **1**（`capture-sayhi-20261109-1447/run.txt`：`elapsed_s=0.985`）（预期：401 `provider.auth` / `capture-only mock`）。
2. 共 **3** 次 `POST /v1/chat/completions`（OpenAI Chat Completions，不是 Anthropic Messages）：
   - **req-01** 正式回答：`body_len=22,803`；`model=deepseek-flash`；`stream=true`；`max_tokens=256000`；**12** 个工具
   - **req-02 / req-03** 会话标题（无 tools；req-03 与 req-02 同形状，疑似标题重试）：`body_len=2,148` / `2,117`
3. **system 长度口径**：对 `messages` 里所有 `role=="system"` 的 `content` 字符串做 `len("".join(...))`（Python）。  
   - 正式请求：**8,799** 字符（来源：项目过程记录 LOG.md 第9行，未入库；原样摘录见 [`evidence/06-opencode/LOG-line9-excerpt.txt`](evidence/06-opencode/LOG-line9-excerpt.txt)；仅有记录、无原件）  
   - 标题请求：**1,806** 字符
4. **工具定义**：12 个（edit, glob, grep, question, read, shell, skill, subagent, webfetch, websearch, write, execute）；`json.dumps(tools, ensure_ascii=False, separators=(',',':'))` 紧凑长度 **13,600** 字符（带空格 dumps 为 14,057）。
5. **额外请求头**（值已打码）：`Authorization`；`User-Agent: opencode/latest/2.2.6/cli`；`traceparent`（W3C trace）；`x-opencode-client/cli`；`x-opencode-project`；`x-opencode-session` / `x-opencode-session-id`；`x-session-affinity`；`x-session-id`。
6. **遥测**：抓包只覆盖 `baseURL` 上的模型请求；是否另有 OTLP/分析上报 **未测**。请求头里的 `traceparent` 表明具备分布式追踪上下文，不等于已外发。
7. 无 dsh 的 `dsh_session_log` / `dsh_plugin_packages` 顶层字段。有 `stream_options`；标题请求带 `thinking`。

保存时对 session/project/trace 头与工作区绝对路径做了打码（见 `CORRECTIONS.md`）。LOG.md（14:47 EST）曾记 **system_chars=8,799**（system-role join）；**仅有记录、无原件可复核**。当前 internal-archive / #10 表为 **8,697**（归档前已做路径打码的版本）。差异**推测**来自路径打码，**无未打码原件可复核**。

## 绕法 / 失败
- 配置里写 `deepseek-chat` 时，`opencode models` 未列出该 ID；改用列表中的 `deepseek/deepseek-flash`。
- 401 后未长时间空转（`elapsed_s=0.985` 结束），比 Claude Code 友好。

## 未做
- 未连官方 `api.deepseek.com`，未跑通工具循环。

## 抓包打码说明（第7轮）
system / tools 原文在 `internal-archive/`；repo 为摘要。口径说明：internal-archive 里的 06 原件在更早一轮已把工作区路径打码，所以不是完全未打码的版本。#10 表 `system_chars=8,697` 是在这个「路径已打码、system 未摘要」的版本上算的；第23行的 8,799 是路径打码前的最早记录。推测差异来自路径打码，无未打码原件可复核。见 `evidence/06-opencode/MASKING.txt`。
