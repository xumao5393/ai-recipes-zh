# CORRECTIONS · 02-dsh-request-capture

时间：2026-11-09 14:37–14:45 EST。本文件集中放对证据原文的更正说明；`run.txt` / `summary.txt` 已恢复为改动前原文，不再就地覆盖。

## 1. `run.txt` 漏写的环境变量

**原文命令行（已恢复）：**
```
$ DEEPSEEK_BASE_URL=http://127.0.0.1:18999 DEEPSEEK_API_KEY=dummy dsh headless "say hi"
```

**按事实应写的完整命令：**
```
$ DSH_TELEMETRY_MODE=off DEEPSEEK_BASE_URL=http://127.0.0.1:18999 DEEPSEEK_API_KEY=dummy dsh headless "say hi"
```

**依据：** 原文输出里有 `$.mode expected "FEEDBACK_ONLY" | "DISABLED" but got "off"`；当时 profile `cordis.patch.yml` 是空数组 `[]`；`dsh-base/cordis.patch.yml` 写明 `mode: !!js process.env.DSH_TELEMETRY_MODE || 'FEEDBACK_ONLY'`。因此 `"off"` 只能来自环境变量 `DSH_TELEMETRY_MODE=off`。后果：`session-telemetry-otel` 插件校验失败、未激活。

**还原依据：** 返工前本 agent 用 Read 打开过原文（内容见会话记录）；本次改动只动过文件开头的 `$ …` 命令行并插入了 CORRECTION 注释头，`dsh: warning` 起的栈与退出信息未改。还原时去掉注释头，并把命令行改回上述原文。同错误的复现输出见 `run-telemetry-off-rerun.txt`（HOME/端口不同，栈路径里的 HOME 不同，不能当原文替身）。

**无法从磁盘备份确认的部分：** 未找到独立 `.bak`/git 对象；还原依据是会话内 Read 快照 + 当前文件未改动的后半段。若需字节级旁证，只能依赖当时 Read 记录。

## 2. `summary.txt` 曾被追加的返工备注

**原文（已恢复，仅四行）：** 见当前 `summary.txt`。其中 `system_chars= 2619` / `487` 使用的是算法 B（见下）。

曾追加在末尾的补跑备注已删除；补跑数字以 `summary-rerun.txt` 与 `recalc_system_and_plugins.out.txt` 为准，不写回本文件。

## 3. `system_chars` 两种算法（2619 vs 2591）

`captured/req-01.json` 里 `body.system` 是 **字符串**（不是分块数组）。

| 算法 | 定义 | req-01 | req-02 |
|---|---|---|---|
| A（正文采用） | `len(system)`，系统提示原文的字符数 | **2591** | **481** |
| B（`summary.txt` 原值） | `len(json.dumps(system, ensure_ascii=False))`，含首尾引号与转义膨胀 | 2619 | 487 |

差值：req-01 为 28 = 2 个引号 + 26 个 `\n` 转义多出的字符；req-02 为 6 = 2 引号 + 4 个 `\n` 转义。脚本与输出：`recalc_system_and_plugins.py`、`recalc_system_and_plugins.out.txt`。

`summary-rerun.txt` 用的是算法 A。正文改用 A，并写明口径。

## 4. `plugin_pkgs_chars` +78 vs 请求体 +74

`summary.txt` / `summary-rerun.txt` 的 `plugin_pkgs_chars` 用的是 **带空格** 的 `json.dumps(val)`（分隔符 `", "` / `": "`）。HTTP 实际请求体是紧凑 JSON。

真默认 vs `DSH_TELEMETRY_MODE=off`（req-01）：

| 口径 | 真默认 | off | 差值 |
|---|---|---|---|
| body_bytes（原始 HTTP） | 54923 | 54849 | **+74** |
| plugin 紧凑 JSON | 5868 | 5794 | **+74** |
| plugin 带空格 JSON | 6222 | 6144 | +78 |

因此表里 +74 与 +78 并不矛盾：格式不同。紧凑口径与请求体差值一致。

## 5. 以后

不再改 `run.txt`、`summary.txt` 以及其它已入库的证据原文；更正只写本文件或新文件。
