# 07 · Aider 指向 DeepSeek 风格端点的请求形状（本地抓包实测）

状态：已实测（2026-11-09 14:49 EST）。证据：`evidence/07-aider/capture-sayhi-20261109-1449/`（n=1）。  
**不是真 DeepSeek key**：`DEEPSEEK_API_BASE` / `OPENAI_API_BASE` 指到本机抓包（回 401）。

## 方法
- 安装绕法：系统 Python 3.13 下 `aider-chat` 拉 `numpy==1.26.4` 需编译且无 g++，失败（`uv-install.txt`）。改用 `uv` 下载 **CPython 3.12.16** 建 venv 后 `uv pip install aider-chat` 成功（`uv_pip_exit=0 elapsed_s=0.64`；`du` 显示 **543M** `.venv`；`aider 0.86.2`）。出处：`evidence/07-aider/uv-install-py312.txt`。
- `HOME=/tmp/aiderhome`；工作区 `git init` 后提交一个 `hello.py`。
- 环境：`DEEPSEEK_API_KEY=dummy-capture`，`DEEPSEEK_API_BASE=http://127.0.0.1:19017/v1`，`OPENAI_API_BASE` 同值。
- 命令：`aider --yes-always --no-check-update --no-show-model-warnings --model deepseek/deepseek-chat --message "say hi"`
- 抓包：`tools/capture_server.py`（只记录、回 401）

## 实测结果（n=1）
1. **3.798 s**，进程 exit **0**（`capture-sayhi-20261109-1449/runA.txt`：`elapsed_s=3.798`），但输出 `litellm.AuthenticationError` / `capture-only mock`（预期）。
2. **1** 次 `POST /v1/chat/completions`（OpenAI 兼容）：`body_len=11,046`；`model=deepseek-chat`；`stream=true`；`max_tokens=8192`；`temperature` 有设置。
3. **无 `tools` 字段**（不是空数组 `[]`；本模式为 diff edit format，规则写在 system 里）。
4. **system 长度口径**：对所有 `role=="system"` 的 `content` 字符串 `len("".join(...))` = **9,644**（两段：主说明 6,605 + SEARCH/REPLACE 规则 3,039）。  
   另：`say hi` 之前已有一段固定的 user/assistant 铺垫对话（约 7,399 字符的前置 messages 内容），不算进上述 system_chars。
5. **请求头**：`Authorization`（已打码）、`User-Agent: litellm/1.81.10`；未见 `x-opencode-*` / `anthropic-*` / `traceparent`。
6. **遥测**：本抓包仅覆盖 API base；是否另有外发 **未测**。

## 失败与绕法
- Py3.13 + 无 g++ → numpy 源码构建失败；绕法：`uv python install 3.12` + venv 再装（有 wheel）。

## 未做
- 未连官方 DeepSeek；未测 `--deepseek` 快捷开关与弱模型；未跑通实际改文件循环。

## 抓包打码说明（第7轮）
system 原文在 `internal-archive/`；repo 为摘要。`system_chars=9,644` 在打码前原件上统计。见 `evidence/07-aider/MASKING.txt`。
