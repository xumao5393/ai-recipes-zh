# 12g Claude Code 接 DeepSeek 时什么时候自动压缩？（本地回放实测）

> 测试时间：2026-11-10 01:10–01:35 EST。Claude Code 2.1.321（`claude -p --output-format json --allowedTools Bash`），`ANTHROPIC_BASE_URL` 指向本机 127.0.0.1 的 Anthropic Messages 回放服务，`ANTHROPIC_MODEL=deepseek-v4-flash`。**没有真 DeepSeek key，没有调用真实端点**。回报的 token 数是回放服务故意写的，不是真实计数。每个配置的边界点 n=1。

## 一句话结论
- **实测**：模型名写 `deepseek-v4-flash` 时，Claude Code 不认识这个模型（启动时打印 `unrecognized_model`），按 **20 万窗口**算。回报 input 166,300 不压缩，166,301 就压缩。也就是说 DeepSeek 的长上下文只用到了约 1/6，过了约 16.7 万 token 就开始摘要。（DeepSeek 实际窗口这里没有用真 key 测；dsh 和 OpenCode 的内置配置都写的是 1,048,576，见 [12e](12e-OpenCode什么时候自动压缩上下文-本地回放实测.md)、[12f](12f-dsh什么时候自动压缩上下文-本地回放实测.md)。）
- **实测**：设 `CLAUDE_CODE_MAX_CONTEXT_TOKENS=1000000` 后，阈值变成 966,300 不压、966,301 压。设 `CLAUDE_CODE_AUTO_COMPACT_WINDOW=1000000` **没用**，回报 30 万、90 万照样压缩。
- **实测**：模型名写成 `deepseek-v4-flash[1m]` 时，发出去的 `model` 字段会去掉 `[1m]`，但请求头多了 `context-1m-2025-08-07`。在回放里，回报 100 万、105 万、120 万、200 万都**完全不压缩**，任务照常完成。换到真端点，这样跑下去大概率会撞上下文上限报错（推测，没测）。
- **实测**：压缩后回报 usage 还是很高时，Claude Code 压到第 3 次就停下，报 `autocompact_thrashing`，exit 1。这和 OpenCode 反复压缩不停（120 秒内 3,053 次，n=1，超时终止；[12e](12e-OpenCode什么时候自动压缩上下文-本地回放实测.md)）、dsh 每步固定多 2 次摘要（[12f](12f-dsh什么时候自动压缩上下文-本地回放实测.md)）都不一样，是三家里唯一有「止损」的。
- **实测**：压缩后，用户最初那句话不再单独保留，换成摘要加完整对话记录文件的路径。**最近一对工具调用和结果原样保留**（OpenCode 压缩后只剩 system 和摘要）。

## 怎么测的
1. 新写回放服务 [cc_compaction_probe_server.py](evidence/12g-claude-code-compaction/cc_compaction_probe_server.py)（只监听 127.0.0.1，不连外网）。脚本让模型每一步调一次 `Bash` 打印固定长度的字符串，第 1 步回报 `input_tokens=1000`，之后各步回报指定值。最后一句用户消息里同时有 `summary` 和 `conversation` 的请求算作压缩请求，回一段固定摘要；压缩之后改报 30,000（`PT_AFTER`），看任务能不能接着跑。
2. 每次运行用独立 HOME，命令见 [run-public.sh](evidence/12g-claude-code-compaction/run-public.sh)。每个请求的摘要信息（种类、消息角色、工具数、`max_tokens`、`anthropic-beta` 头）存成 `run-*/req-*.meta.json`。原始请求体里有 Claude Code 系统提示，**没有入库**。
3. 先粗扫 5 万 / 15 万 / 18 万 / 20 万 / 30 万 / 90 万，再在 15 万到 18 万之间二分（[bisect.txt](evidence/12g-claude-code-compaction/bisect.txt)）。

## 结果

### 1. 默认（不认识的模型）：约 16.7 万就压缩
| 回报 input_tokens（第 2 步后） | 是否压缩 | 证据 |
|---|---|---|
| 50,000 / 150,000 | 否 | run-pt50k、run-pt150k |
| 180,000 / 200,000 / 300,000 / 900,000 | 是 | run-pt180k … run-pt900k |
| 166,300 | 否 | run-bis-166300 |
| 166,301 | 是 | run-bis-166301 |

工具输出长度变一下，边界也跟着移（[bisect-bytes.txt](evidence/12g-claude-code-compaction/bisect-bytes.txt)，中间运行目录测完已删，只留结论行）。202 和 20,002 这两行的运行目录已经删了，读者没法复核，只能看结论行；2,002 那一行可以用上面二分的 run-bis-* 目录复核：

| 每步打印字符数 | 不压缩的最大回报值 | 167,000 − 回报值 − 32（output） |
|---|---|---|
| 202 | 166,900 | 68 |
| 2,002 | 166,300 | 668 |
| 20,002 | 160,300 | 6,668 |

最右一列都约等于「工具输出字符数 ÷ 3」。所以判断式可以写成：**上轮回报 input + output + 新工具结果约每 3 字符 1 token ≥ 167,000 就压缩**。（这是用 3 个长度拟合出来的，不是从源码里读到的。）167,000 正好等于 200,000 − 20,000 − 13,000，**推测**是窗口减输出预留再减缓冲，没在源码里确认。

### 2. 能不能调大：三个开关结果不一样
| 设置 | 结果 | 证据 |
|---|---|---|
| `CLAUDE_CODE_AUTO_COMPACT_WINDOW=1000000` | 30 万、90 万照样压缩，没调大 | run-win1m-300k、run-win1m-900k |
| `CLAUDE_CODE_MAX_CONTEXT_TOKENS=1000000` | 966,300 不压、966,301 压（加上 699 正好是 967,000 = 1,000,000 − 33,000） | run-maxctx-966300、run-maxctx-966301、bisect-1m.txt |
| 模型名 `deepseek-v4-flash[1m]` | 100 万、105 万、120 万、200 万都不压；30 万到 99.9 万之间二分也一次没压 | run-sfx-hi-*、run-suffix1m-300k、bisect-1m.txt |
| `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE=50` | 89,300 不压、89,301 压（加 699 = 90,000 = 50% × 180,000），只能调小 | run-pct50-89300、run-pct50-89301、bisect-1m.txt |
| `DISABLE_AUTO_COMPACT=1` + 回报 30 万 | 不压缩，第 3 步前本地直接报 `Prompt is too long`，exit 1，请求没发出去 | run-noauto-300k |

`[1m]` 那组的请求头对照（run-hdr-sfx / run-hdr-plain）：`anthropic-beta` 多了 `context-1m-2025-08-07`，`model` 字段还是 `deepseek-v4-flash`。DeepSeek 端怎么处理这个头，没有测。

### 3. usage 一直偏高：压 3 次就停
run-stuck300k：压缩后仍回报 30 万。一共 8 个请求（工具 5、压缩 3）。最后 Claude Code 输出 `"api_error":"autocompact_thrashing"`，原文是 "Autocompact is thrashing: the context refilled to the limit within 3 turns of the previous compact, 3 times in a row."，exit 1，用时 0.633 秒。

### 4. 压缩请求和压缩后留下什么
- 压缩请求（run-pt180k 第 3 个）：带着完整历史和 12 个工具定义，最后一条用户消息是一段 6,361 字符的压缩指令模板，作用是要求模型只用文字写摘要、不要调用工具（Claude Code 内置提示词，原文不转载），`max_tokens` 还是 32,000。
- 压缩后的第一个请求（第 4 个）一共 5 条消息：
  1. 一条用户消息，先说明这是接着之前一段因上下文用完而中断的对话（Claude Code 内置提示词，原文不转载），里面放了摘要、完整记录 `.jsonl` 的本地路径，还写着「后面几条是压缩前最近的消息，原样保留」；
  2. 日期；
  3. 最近一次 `Bash` 调用和它的结果（`S2xxx…` 原样保留，`S1` 那一步没了）；
  4. 一段 ToolSearch 的提示。
- 用户原话 "run the steps" 不再单独保留。这次能在摘要里看到这几个字，是因为回放服务的固定摘要里本来就写了。

## 对比三家（都是本地回放，回报值是造的）
| | 触发点（接 DeepSeek 默认配置） | 压缩前先做什么 | 压缩后留什么 | usage 一直偏高 |
|---|---|---|---|---|
| OpenCode 2.2.6（[12e](12e-OpenCode什么时候自动压缩上下文-本地回放实测.md)） | 891k | 无 | system + 摘要 | 反复压缩，120 秒内 3,053 次（n=1，超时终止） |
| dsh 0.2.2-rc.1（[12f](12f-dsh什么时候自动压缩上下文-本地回放实测.md)） | 727,040 | 先剪大工具输出 | 摘要 + 最近约 12.7 万 | 每步多 2 次摘要，继续走 |
| Claude Code 2.1.321（本篇） | **约 167k**（当成 20 万窗口） | 无 | 摘要 + 记录路径 + 最近一对工具调用 | 3 次后停，exit 1 |

## 能拿去用的
- 用 Claude Code 接 DeepSeek 跑长任务，默认约 16.7 万 token 就会开始摘要。如果想用满长上下文，本次实测**只有 `CLAUDE_CODE_MAX_CONTEXT_TOKENS` 真正把阈值调到了 96.7 万**。`CLAUDE_CODE_AUTO_COMPACT_WINDOW` 往大调没用。
- 不建议在模型名后面加 `[1m]`：回放里到 200 万都不压缩，等于失去了自动压缩；还会多发一个 Anthropic 专用的 beta 头。
- 摘要以后，Claude Code 会把完整记录文件的路径写给模型，留了一条读回原文的路。这只是看到了这段提示，模型会不会真的去读，没有测。

## 没测的、要注意的
- 没有真 key，DeepSeek 实际回报的 usage 和上下文上限都没验证；结论只说明 Claude Code 怎么**根据回报值**做决定。
- 交互模式（不加 `-p`）没测，只测了 `-p` 非交互模式。
- 1M 情况只测了 `1000000` 这个值，`1048576` 没测。
- 每个边界 n=1；回放服务是自己写的，判断压缩请求靠关键词。
- 「约 3 字符 1 token」是 3 个点拟合出来的。

## 复现
脚本是 [run-public.sh](evidence/12g-claude-code-compaction/run-public.sh)，它要求读者先准备一个工作目录，用环境变量 `R` 指向它。脚本按下面的固定相对路径找东西，所以要提前准备好：

- `$R/tools/cc_compaction_probe_server.py`：从 evidence 目录复制 [cc_compaction_probe_server.py](evidence/12g-claude-code-compaction/cc_compaction_probe_server.py)，需要 Python 3（本次用的是 3.13.5）。
- `$R/sandbox-claude-code/`：在这个目录里用 npm 装 `@anthropic-ai/claude-code`，本次装到的版本是 2.1.321。脚本调用的是 `$R/sandbox-claude-code/node_modules/.bin/claude`。
- `$R/repo/evidence/12g-claude-code-compaction/`：输出目录，脚本会在下面新建 `run-<TAG>/`，并**删除同名旧目录**。`$R/sandbox-m12g/` 是隔离 HOME 和工作目录，也会被删了重建。
- 要有 `timeout`（coreutils）；回放服务只监听 127.0.0.1，端口选一个空闲的就行。`ANTHROPIC_API_KEY` 设成假值 `dummy-replay`，不需要真 key，也不会连真实端点。

```bash
export R=<你的工作目录>
cd $R/repo/evidence/12g-claude-code-compaction
# 参数：TAG PORT STEPS BYTES PT_CSV [TIMEOUT]，端口 19100 只是举例
PT_AFTER=30000 ./run-public.sh bis-166300 19100 3 2000 1000,166300   # 本次结果：不压缩
./run-public.sh stuck300k 19101 4 2000 1000,300000                    # 本次结果：压缩 3 次后停，exit 1
```
本次实际跑的是 internal-archive 里的原件 `run.sh`。它和 `run-public.sh` 只差 `R=` 那一行，公开副本本身没有重新跑过。各次运行的实际参数见每个 `run-*/summary.txt`。

## 证据
- [evidence/12g-claude-code-compaction/](evidence/12g-claude-code-compaction/)：`AGGREGATE.json`（40 次运行的请求种类计数）、`bisect*.txt`、每次运行的 `summary.txt` / `run.json` / `run.err` / `server.log` / `req-*.meta.json`。
- 原始请求体（含 Claude Code 系统提示）和打码前的副本在 internal-archive/12g-claude-code-compaction/，不入库。公开脚本 `run-public.sh` 只把原件里的工作目录改成环境变量 `R`，原件 sha256 见 [MASKING-public.txt](evidence/12g-claude-code-compaction/MASKING-public.txt)。
