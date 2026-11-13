# 08 Cline CLI 接 DeepSeek：实测记录（2026-11-09 15:06–15:12 EST；第10轮返工 15:28–）

> 标注：**实测**＝本机跑过并有 evidence；**推断**＝未直接抓到、依旁证判断。全部 n=1，无真实 DeepSeek key，未产生任何费用。本轮不再向真实端点发请求。

## 结论先说
1. **实测**：Cline 已有独立命令行版 `cline`（npm 包 `cline@3.0.74`）。本机已装目录 `sandbox-cline/node_modules`（26,009 个文件）：`du -sb sandbox-cline/node_modules` → **345,897,602 字节**（文件实际大小合计，约 346MB / 330MiB）。磁盘占用 **416M**（`du -sh`；按磁盘块算，`du -sk` = 425,404 KiB，小文件多所以比文件大小多）（命令与输出见 `evidence/08-cline-cli/node_modules-du-r11.txt`，2026-11-09 15:31 EST，n=1）。另一次装到临时前缀 `/tmp/cline-install-timing`（`npm i ./cline-3.0.74.tgz --prefer-offline`，n=1）墙钟 **real 4.301s**（见 `npm-install-timing.txt`）。旧稿「8.7s」无安装日志可复核，已废弃。「Cline 只能在 VS Code 里测」不成立。Roo Code 在 npm 上没有 `@roo-code/cli`（404），本轮未测。
2. **实测**：内置 `deepseek` 提供方的地址写死为 `https://api.deepseek.com/v1`，默认模型 `deepseek-v4-flash`，读 `DEEPSEEK_API_KEY`；`cline auth deepseek -b <地址>` 报错 “base URL is only supported for OpenAI and OpenAI-compatible providers”（`source-deepseek-snippet.txt`、`auth-20261109-1507.txt`）。想换地址（中转、本地代理、抓包）只能用 `openai-compatible` 提供方。
3. **推断**（依据：运行输出报错文本与无 key 的 curl 对照一致；本地抓包目录对该次运行为空）：在 auth 未配成可改地址、`-P deepseek` 跑「say hi」时，Cline 打到了官方端点。证据：`run-sayhi-20261109-1507.txt` 出现 `Authentication Fails (governor)`，`durationMs=440`；`capture-sayhi-20261109-1507/EMPTY-NOTE.txt` 说明本地假服务未收到包；`curl-real-endpoint-nokey.txt` 对 `api.deepseek.com/v1/chat/completions` 无 key 直连得同一句与 HTTP 401。按同一次「say hi」、改用 `openai-compatible` 指向本地假服务时抓到的正式包（含 system + 用户句「say hi」），**推断**误发内容同类；**本地没有该次发往官方的请求体抓包**，故不能实测写出具体字段。当时无有效密钥、curl 对照为 401、未见计费；**不会再向真实端点复现**。
4. **实测**：`openai-compatible` + 本地抓包，「say hi」只发 **1 个** `POST /v1/chat/completions`，`body_len` **21,820**，`stream: true`，`tool_choice: auto`，**25 个工具**，system **4,257** 字符。工具定义在 internal-archive 原件上按 #10 同口径重算：`json.dumps(tools, ensure_ascii=False, separators=(',',':'))` → **17,323**（`tools-recalc.json` / `_tools_meta.tools_json_compact_chars`）。同对象默认 `json.dumps`（带空格）→ **18,174**（旧 `tools_summary.length`）。25 个里 **18 个 `team_*`**，其余 7 个：`read_files` / `search_codebase` / `run_commands` / `fetch_web_content` / `editor` / `ask_question` / `spawn_agent`（7+18=25）。
5. **实测**：请求头只有常规字段，User-Agent 为 `ai-sdk-openai-compatible/3.0.67 ai-sdk-provider-utils/5.0.58 bun/1.4.2`；没看到 dsh 那种会话日志字段或 OpenCode 的 x-opencode-* / traceparent 头。
6. **实测**：本次测试写入的假 key 以明文落在 `<HOME>/data/settings/providers.json`（本机隔离目录实际为 `/tmp/clinehome/data/settings/providers.json`），权限 `-rw-------`（mode 600）。字段 `$.providers.openai-compatible.settings.apiKey`：length=18，sha256 与测试输入假 key 的 sha256 相同，字节级比较 **true**（`key-storage-check.txt`；**不存值本身、不存假 key 字符串**）。同文件里当前 `providers.deepseek.settings` 无 `apiKey` 字段（仅 provider/model）。
7. **实测**：遇 401 时 Cline 直接结束（`finishReason=error`，exit 1），没有像 Claude Code 那样反复重试。计时以证据为准：openai-compatible 抓包这次 `durationMs=46`（agent 迭代），整进程 `time real=0m1.248s`（`run-sayhi-openai-compatible.txt`）；内置 deepseek 那次 `durationMs=440` / `real 0m1.748s`（`run-sayhi-20261109-1507.txt`）。旧稿「运行 1.25s」来自前者墙钟，易与 `durationMs` 混淆，正文改为同时写明两套数字。

## 和其他外壳对比
不要在本篇重抄对比表。统一口径与各外壳数字见草稿 **[10-各外壳固定请求开销对比-草稿.md](./10-各外壳固定请求开销对比-草稿.md)**（`evidence/10-compare-draft/recalc_compare.py`）。本篇 Cline 自己的数字（上表第 4 条）可与之对照；**不要**再把 dsh 默认写成 54,849，也**不要**把 Aider 写成「0 个工具」（Aider 是无 `tools` 字段）。

## 过程（命令都可复现；重测只用本地假服务）
```bash
mkdir sandbox-cline && cd sandbox-cline && npm init -y && npm i cline@3.0.74
# 体积：du -sb node_modules；du -sh node_modules
# 耗时重测（n=1）：装到 /tmp/cline-install-timing，time npm i ./cline-3.0.74.tgz --prefer-offline
export HOME=/tmp/clinehome   # 隔离，不碰真实家目录
python3 tools/capture_server.py 19018 <抓包目录> &   # 只记录，回 401，不转发
# 第一次：内置 deepseek（不可改 base URL）——已发生过一次误打官方；不再复现
# 第二次：openai-compatible → 127.0.0.1:19018
cline auth openai-compatible -k '<FAKE_KEY>' -m deepseek-v4-flash -b http://127.0.0.1:19018/v1 --data-dir $D
cline --data-dir $D -P openai-compatible -m deepseek-v4-flash --json -t 90 "say hi"
```
失败与绕法：内置提供方不能改地址 → 换 openai-compatible。

## 证据（evidence/08-cline-cli/）
- `node_modules-du.txt`、`npm-install-timing.txt`：体积与重装耗时（n=1）
- `auth-*.txt`、`run-sayhi-*.txt`：命令原始输出
- `capture-sayhi-openai-compatible/req-01.summary.json`：请求摘要（system 留 first_line；tools 只留 name/length/sha256）
- `tools-recalc.json`：在 `internal-archive/08-cline-cli/req-01.raw.json` 上按 #10 口径重算
- `capture-sayhi-20261109-1507/EMPTY-NOTE.txt`：内置 deepseek 那次本地未收到包
- `curl-real-endpoint-nokey.txt`：无 key 直连官方的 401 对照
- `source-deepseek-snippet.txt`：包内 deepseek 提供方配置片段
- `key-storage-check.txt`：明文存储旁证（路径/权限/字段/length/sha256/比较结果）
- `MASKING.txt`、`REDACTION-CHECK.txt`

## 没测的
真实 key 下的工具循环、费用、缓存命中；Roo Code；VS Code 插件版 Cline 是否与 CLI 同一套提示和工具。
