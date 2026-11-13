# 02 · dsh 每次调用模型到底发了什么（本地抓包实测）

状态：已实测（2026-11-09 14:07 EST 初测；14:34 EST 补跑对照；14:37–14:45 EST 按第 2 轮复审返工）。证据：`evidence/02-dsh-request-capture/`（抓包脚本同目录 `capture_server.py` / 专题 `tools/capture_server.py`，匿名用户 ID 已打码）。证据原文的更正说明见 `CORRECTIONS.md`（更正记录，暂未入库）（不就地改 `run.txt` / `summary.txt`）。

## 方法
`dsh` 支持用 `DEEPSEEK_BASE_URL` 换接口地址（`dsh-llm-deepseek` 的类型说明写明）。我在本机起了一个只记录、不转发、直接回 401 的假服务，再用假 key 跑。不花钱；**模型请求指向本地，遥测是否外联未验证**。

**重要更正（返工，详见 `CORRECTIONS.md`（更正记录，暂未入库））**：14:07 那次被标成“默认”的抓包，运行环境里实际设了 `DSH_TELEMETRY_MODE=off`。依据：`run.txt` 原文出现 `$.mode expected "FEEDBACK_ONLY" | "DISABLED" but got "off"`，同时 profile 的 `cordis.patch.yml` 是空数组 `[]`，所以这个 `"off"` 只能来自环境变量（`dsh-base/cordis.patch.yml` 里是 `process.env.DSH_TELEMETRY_MODE || 'FEEDBACK_ONLY'`）。`run.txt` 原文命令行漏写了该变量（原文已恢复保留）；完整命令应为：

```bash
DSH_TELEMETRY_MODE=off DEEPSEEK_BASE_URL=http://127.0.0.1:18999 DEEPSEEK_API_KEY=dummy dsh headless "say hi"
```

后果：`session-telemetry-otel` 插件因配置校验失败**没有激活**。

加补丁组（`run-patched.txt`；补丁本身也 disable 了遥测插件）：

```bash
DEEPSEEK_BASE_URL=http://127.0.0.1:18999 DEEPSEEK_API_KEY=dummy dsh headless --patch privacy.patch.yml "say hi"
```

## 实测发现
1. **协议是 Anthropic 风格的 `POST /v1/messages`**（带 `anthropic-version: 2023-06-01`、`x-api-key`）。换成别的兼容服务理论上能接，但还没实测。
2. **一句“say hi”会发 2 个模型请求**：一个是正式回答，一个是生成会话标题（`max_tokens: 4096`，关思考）。标题这次调用也会计费，属于推测，没拿真 key 核过。
3. **正式请求的固定开销**（原“默认”组，n=1）：
   - **系统提示 2,591 字符**（口径：`body.system` 是字符串，取 `len(system)`；见 `recalc_system_and_plugins.out.txt`）。
   - 说明：`summary.txt` 里的 `system_chars= 2619` / `487` 用的是另一种算法 `len(json.dumps(system))`（含 JSON 引号与 `\n` 转义膨胀），分别对应 2,619 与 487；**正文以原文字符数为准（2,591 / 481）**，不沿用 summary 的 2619/487。
   - 工具定义 24 个；`summary.txt` 记 `tools_json_chars= 19787`（带空格的 `json.dumps`）；紧凑 JSON 为 19,154（同脚本）。
   - 默认 `max_tokens: 256000`、开思考、`effort: high`。
4. **请求体里还额外带了两段 DeepSeek 专用字段**（原“默认”组，n=1）：
   - `dsh_session_log`：`summary.txt` 记 27,188 字符（带空格 `json.dumps`）；紧凑 JSON 26,279。
   - `dsh_plugin_packages`：`summary.txt` 记 6,144 字符（带空格）；紧凑 JSON 5,794。
   请求头还带 `x-deepseek-harness-user-id`（本机匿名 ID，证据里已打码）和会话 ID。

   **出处（插件包自带 README，版本 0.2.2-rc.1）**：
   - `sandbox/node_modules/@deepseek-ai/dsh-session-log-deepseek/README.md`（包 `@deepseek-ai/dsh-session-log-deepseek@0.2.2-rc.1`）：描述为 “Incremental canonical session-log upload for deployments enabling official DeepSeek request metadata.”；摘要写明注入 `dsh_session_log` 请求字段。摘录见 `plugin-readme-excerpts/`。
   - `sandbox/node_modules/@deepseek-ai/dsh-plugin-package-inventory-deepseek/README.md`（包 `@deepseek-ai/dsh-plugin-package-inventory-deepseek@0.2.2-rc.1`）：原文 “Shipped profiles use the default, so every official DeepSeek request carries the package inventory when preparation succeeds.” 摘录同上。
   - 说明：本篇以已安装包内 README 为准。
   会不会算 token、对方怎么用，我测不了，不下结论。
5. **一个补丁就能关掉这两段**（`privacy.patch.yml`）：

```yaml
- id: session-log-deepseek
  disabled: true
- id: plugin-package-inventory-deepseek
  disabled: true
- id: session-telemetry-otel
  disabled: true
```

用 `dsh headless --patch privacy.patch.yml "..."` 实测（每组 n=1）：

| 请求 | 原“默认”组（实为 `DSH_TELEMETRY_MODE=off`，遥测插件未激活） | 加补丁 |
|---|---|---|
| 正式回答 | 54,849 字节 | 22,680 字节 |
| 会话标题 | 32,923 字节 | 754 字节 |

加补丁后这两个字段都没了，请求照常发到本地假服务并收到 401（`run-patched.txt`）。这只说明请求发出去了；**模型能不能正常回答并没有测**，不能读成“打了补丁也不影响使用”。匿名 ID 请求头仍在。补丁关掉 `session-telemetry-otel` 以后，遥测到底停没停，这次抓包抓不到（遥测默认地址是 `dsh-otel-collector.deepseeksvc.com`，与模型请求不是同一通道），**遥测是否停止未验证**。

## 补跑：真默认 vs `DSH_TELEMETRY_MODE=off`（模型请求指向本地；遥测是否外联未验证）

2026-11-09 14:34 EST，各 n=1（`run-true-default.txt`、`run-telemetry-off-rerun.txt`、`summary-rerun.txt`、`recalc_system_and_plugins.out.txt`）。

真默认组**未**设置 `DSH_TELEMETRY_MODE`，遥测插件按默认 `FEEDBACK_ONLY` **激活**；其 OTLP 上报地址是 DeepSeek 的真实服务器 `dsh-otel-collector.deepseeksvc.com`。本次只把 `DEEPSEEK_BASE_URL` 指到本地，**没有**把 `DSH_TELEMETRY_OTLP_URL` 指到本地，也没有断网，因此**遥测是否外联未验证**。

| 条件 | 正式回答 body_bytes | 标题 body_bytes | plugin 紧凑 JSON | plugin 带空格 JSON | 遥测插件 |
|---|---|---|---|---|---|
| 真默认（unset `DSH_TELEMETRY_MODE`） | 54,923 | 32,997 | 5,868 | 6,222 | 激活（无 ValidationError） |
| `DSH_TELEMETRY_MODE=off`（复现原条件） | 54,849 | 32,923 | 5,794 | 6,144 | 未激活（got "off"） |
| 差值（真默认 − off） | +74 | +74 | +74 | +78 | — |

表下说明：请求体 `body_bytes` 来自原始 HTTP（紧凑 JSON）。上一轮表里 plugin 列用的是带空格的 `json.dumps`，所以显示 +78；按紧凑 JSON 复算是 5,868 − 5,794 = **+74**，与请求体差值一致。两种算法差在 JSON 分隔符空格，不是测错了。

结论：`DSH_TELEMETRY_MODE=off` 对**模型请求体大小**影响很小（+74 字节/请求），主要是插件清单里多了已激活的 `session-telemetry-otel`。原“默认”组 vs 加补丁的数量级对比（54,849→22,680）仍然成立；把原组改称为“遥测插件未激活的对照”更准确。

## 值得思考
- 只说“DeepSeek 便宜”不够：工具外壳每轮都会带近 2 万字符的工具定义，还会多一次标题调用。真实花费要用真 key 跑同一任务才能比，这一项列为下一步。
- 在意隐私的人，可以用上面的补丁少发本地路径和会话日志。这只是降低外发量，不保证不留痕；真默认配置下遥测插件会指向官方 OTLP 地址，本次未验证是否真的外发。
