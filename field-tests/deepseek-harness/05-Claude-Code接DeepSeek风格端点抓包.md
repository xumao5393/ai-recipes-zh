# 05 · Claude Code 指向 DeepSeek 风格端点的请求形状（本地抓包实测）

状态：已实测（2026-11-09 14:36–14:37 EST）。证据：`evidence/05-claude-code/`。  
**不是真 DeepSeek key**：`ANTHROPIC_BASE_URL` 指到本机抓包服务（回 401），只看发出去的请求。

## 方法
- 安装：`npm install @anthropic-ai/claude-code@2.1.321`（独立目录 `sandbox-claude-code/`，约 3 s，`node_modules` ≈ **327 MB**；npm 未跑 postinstall，但 `claude --version` 可用）。
- `HOME=/tmp/cchome`
- `ANTHROPIC_BASE_URL=http://127.0.0.1:19005`
- `ANTHROPIC_API_KEY=dummy-capture`
- `ANTHROPIC_MODEL=deepseek-chat`（模拟社区接 DeepSeek Anthropic 兼容端点时常用的模型名）
- 命令：`claude -p --dangerously-skip-permissions "say hi"`
- 抓包脚本同 #02 的 `tools/capture_server.py`（只记录、回 401）。

## 实测结果
1. stderr 警告：`Claude Code doesn't recognize the model "deepseek-chat", so it assumes a context window of 200k tokens`（`[claude-code:unrecognized_model]`）。
2. 对抓包服务发出 **8 次完全相同** 的 `POST /v1/messages?beta=true`（401 后自动重试）；约 75 s 后仍未自行退出，实测进程被杀掉结束。**单次请求体 body_len = 46,907 字节**。
3. 协议仍是 Anthropic Messages：`anthropic-version: 2023-06-01`，`x-api-key`，`stream: true`，`User-Agent: claude-cli/2.1.321 (external, sdk-cli)`。
4. 额外头：很长的 `anthropic-beta`（含 `claude-code-20250219`、`interleaved-thinking-2025-05-14` 等）、`X-Claude-Code-Session-Id`、一串 `X-Stainless-*`。
5. 请求体要点：
   - `model: deepseek-chat`，`max_tokens: 32000`，`thinking: {type: adaptive, display: omitted}`，`output_config.effort: high`
   - `system`：3 个 text block，正文合计约 **若干千字符**（含 `x-anthropic-billing-header` 与长系统提示）
   - **12 个工具**：Agent, Bash, Edit, ListAgents, Read, ReportFindings, ScheduleWakeup, Skill, ToolSearch, Workflow, DeferredToolPlaceholder, Write；工具 JSON 约 **29,995** 字符
   - 有 `metadata.user_id`（含 device_id / session_id JSON 字符串）、`context_management`
   - **没有** dsh 那种 `dsh_session_log` / `dsh_plugin_packages` 顶层字段

## 与 dsh（#02/#03）对照（同一本地抓包思路）
| 项 | dsh 0.2.2-rc.1（#02 默认） | Claude Code 2.1.321（本篇） |
|---|---|---|
| 路径 | `/v1/messages` | `/v1/messages?beta=true` |
| “say hi” 请求次数 | 2（回答+标题） | 同形状重试多次（本测 8×，因 401） |
| 首包 body_len | 54,849（补丁后 22,680） | 46,907 |
| 工具数 | 24 | 12 |
| 专用外发字段 | `dsh_session_log` + `dsh_plugin_packages` | 无；有 `metadata` / `context_management` |
| 思考字段 | `thinking: {type: enabled}` | `thinking: {type: adaptive, ...}` |

## 未做
- 未连 `api.deepseek.com/anthropic`（无真 key，规则禁止假装测了）。
- 未让 Claude Code 跑完工具循环（401 重试占住进程；可用回放服务再测，留待有空时）。

## 抓包打码说明（第7轮）
`evidence/05-claude-code/captured/req-*.json` 的 system / tools 原文已移至 `deepseek-harness/internal-archive/`（不随仓库发布）。repo 内为摘要（length/sha256/first_line）。文中 **system_chars=6,674**、tools 紧凑长度等数字均在**打码前原件**上统计（见 `MASKING.txt` 与 #10 `numbers.json`）。
