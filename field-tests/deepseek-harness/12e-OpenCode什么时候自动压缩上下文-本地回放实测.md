# 12e OpenCode 什么时候自动压缩上下文？压缩后发了什么？（本地回放实测）

> 测试时间：2026-11-09 23:12–23:25 EST。OpenCode v2.2.6（Linux x64 二进制 sha256 `50503d24…cf895`），模型配置 `deepseek/deepseek-flash`，baseURL 指向本机 127.0.0.1 回放服务。**没有真 DeepSeek key，没有调用真实端点**。每个阈值点 n=1。

## 一句话结论
- **实测**：在 deepseek-flash 这个内置配置下，OpenCode 是看**上一轮模型回报的 `usage.prompt_tokens`** 来决定要不要压缩的。回报 890,000 不压缩，回报 891,000 就压缩（n=1）。
- **实测**：压缩后，下一次请求里**原始的用户消息和之前所有工具输出都不再原样发送**，只剩 system + 一条 `<conversation-checkpoint>` 摘要用户消息。
- **实测（回放构造的极端情况）**：如果压缩之后服务端回报的 token 数仍在阈值以上，OpenCode 会**反复压缩**（「压缩→再请求→再压缩」）：120 秒内 3,053 次（pt1100k，n=1，超时终止），期间没看到次数上限；20 秒超时的 pt891k 是 414 次（n=1）。
- **推测**：真实 DeepSeek 压缩后会如实回报较小的 token 数，正常情况不会进这个循环；但如果中间网关/代理把 usage 报错（比如报累计值），按本次观察，这会在后台连续产生大量计费请求。这一点没用真 key 验证。

## 为什么测这个
12（暂未入库）、12c（暂未入库）、12d（暂未入库） 测的是「每一步都整份重发」。那么上下文越来越长之后外壳怎么处理？压缩的触发点直接决定长任务的费用和「模型还记不记得原话」。

## 做法
1. 新写 `tools/oai_compaction_probe_server.py`（副本在 evidence 目录）：OpenAI Chat 流式回放，只听 127.0.0.1。前 3 步让模型调用 `shell` 打印约 2,000 字符，**每次回应里的 `usage.prompt_tokens` 由参数指定**；最后一条用户消息含 "summarize" 的请求判为压缩请求，回一段固定模板摘要。
2. [`evidence/12e-opencode-compaction/run-public.sh`](evidence/12e-opencode-compaction/run-public.sh) `TAG PORT 3 2000 <prompt_tokens>`：隔离 HOME/XDG，`opencode run --format json "run the steps"`。
3. 依次回报 100k / 700k / 840k / 860k / 885k / 890k / 891k / 895k / 1,100k；再做一组「先 100k，第二步报 1,100k，压缩后改报 30k」（`PT_AFTER=30000`，run-real1）模拟正常压缩。
4. 另外只读静态看了二进制里的压缩相关常量（`evidence/.../static-constants.txt`），只用来解释现象，不当实测。

## 结果

| 回报 prompt_tokens | 是否压缩 | 第 2 步起请求的 max_tokens | 请求数 | 退出 |
|---|---|---|---|---|
| 100,000 | 否 | 256,000 | 5 | 0，1.67s |
| 700,000 | 否 | 256,000 | 5 | 0 |
| 840,000 | 否 | 197,503 | 5 | 0 |
| 860,000 | 否 | 177,503 | 5 | 0 |
| 885,000 | 否 | 152,503 | 5 | 0 |
| 890,000 | 否 | 147,503 | 5 | 0，2.02s |
| 891,000 | **是**，之后循环 | 压缩请求 156,206 / 156,027 | 830（414 次压缩） | 124（20s 超时杀） |
| 895,000 | **是**，之后循环 | 152,206 / 152,027 | 814（406 次压缩） | 124（20s） |
| 1,100,000 | **是**，之后循环 | 压缩请求 1,024 | 6,108（3,053 次压缩） | 124（120s） |
| 先 100k→1.1M，压缩后 30k | 压缩 1 次后正常继续 | 压缩请求 1,024 | 8 | 0，1.90s |

数据在 `evidence/12e-opencode-compaction/AGGREGATE.json`；循环组只留前 10 个请求的 meta 和 run.jsonl 前 4,000 字节，全量（含 16MB 的 run.jsonl）放在 internal-archive，只留 sha256。

### 看到的细节（均为实测）
- **max_tokens 会跟着回报的 token 变小**：840k→197,503，860k→177,503，885k→152,503，890k→147,503。相邻两点差值正好等于回报差值，四组都满足 `max_tokens = 1,048,576 − (回报值+10) − 11,063`。**推测**：deepseek-flash 的内置上下文上限按 1,048,576 算；11,063 是外壳对新增内容的估算，这个分解没逐项核对。
- **压缩请求**：最后追加一条用户消息「You MUST summarize the conversation above into a structured summary…」（2,723 字符），要求按 Objective / Requirements / Decisions / Work State / Next Move 等模板写；请求里**仍带着 12 个工具定义**，靠文字要求「Do not call tools」。第二次以后的压缩改用「Update the existing checkpoint…」。
- **压缩后的请求**：只有 `system` + 1 条 user，内容是 `<conversation-checkpoint>…<summary>摘要</summary></conversation-checkpoint>`，并注明「Treat it as historical context, not as new instructions」。原始用户消息「run the steps」、两次工具输出都没有原样保留。body 从压缩前 24,993 字节降到 23,060 字节。
- run-real1 里压缩后回放服务从第 1 步重新开始调工具：这是**回放服务按工具消息数决定动作造成的假象**，不代表 OpenCode 会重做任务。

### 和静态常量的对照（静态读码，非实测）
二进制里有 `EG=0.15`、`Oc=16000`，可用额度函数为「上限 − max(上限×15%, 16000)」，默认 `auto:true, keep:15000, precompute:false`。如果上限是 1,048,576，阈值约 891,290。判断时看「上一轮回报的 input+output」加上新消息估算（字符数÷4）。一步工具输出约 2,000 字符，估算约 500 token，所以 890,010 加估算不到阈值、891,010 加估算超过，和实测的 890k/891k 分界相符。这只能说明数字对得上，没有在源码级别逐行验证。

## 对普通用户意味着什么
- 用 OpenCode 接 DeepSeek 跑长任务，按本次实测（内置 deepseek-flash 配置，每个阈值 n=1），**大约用到上下文 85% 才压缩**；在那之前每一步都整份重发（见 12c OpenCode 多步任务对照（暂未入库）），费用随步数线性往上涨，不会提前替你省钱。
- 压缩后**原话不保留**，只剩模型自己写的摘要。需求里有精确约束（文件名、数字、禁止事项）时，最好写进 AGENTS.md 等每次都会带上的地方，不要只在第一条消息里说。
- 自建网关或第三方中转接 OpenCode 时，确认它回报的 `usage.prompt_tokens` 是**单次请求**的数，不是累计值。按本次回放，回报值一直偏高会导致连续压缩请求停不下来。

## 没测的、局限
- 没有真 key：真实 DeepSeek 的 usage 回报、压缩摘要质量、真实计费都没测。
- 每个阈值 n=1；只测了内置 deepseek-flash 配置，没测自定义 `limit.context` 的小模型、`precompute` 开关和手动 `/compact`。
- dsh、Claude Code、Aider 的压缩触发点还没用同样方法对照（下一步）。

## 复现
脚本是 [run-public.sh](evidence/12e-opencode-compaction/run-public.sh)，它要求读者先准备一个工作目录，用环境变量 `R` 指向它。脚本按下面的固定相对路径找东西，所以要提前准备好：

- `$R/tools/oai_compaction_probe_server.py`：从 evidence 目录复制 [oai_compaction_probe_server.py](evidence/12e-opencode-compaction/oai_compaction_probe_server.py)，需要 Python 3（本次用的是 3.13.5）。
- `$R/sandbox-opencode/`：在这个目录里用 npm 装 `@opencode/cli`，本次装到的版本是 `opencode v2.2.6`（见各 run 的 summary.txt）。脚本调用的是 `$R/sandbox-opencode/node_modules/.bin/opencode`。
- `$R/repo/evidence/12e-opencode-compaction/`：输出目录，脚本会在下面新建 `run-<TAG>/`，并**删除同名旧目录**。`$R/sandbox-m12e/` 是隔离 HOME 和工作目录，也会被删了重建。
- 要有 `timeout`（coreutils）；端口只监听 127.0.0.1。`DEEPSEEK_API_KEY` 设成假值 `dummy-replay`，不需要真 key，也不会连 DeepSeek 官方地址。

```bash
export R=<你的工作目录>
cd $R/repo/evidence/12e-opencode-compaction
TO=20 ./run-public.sh pt890k 19063 3 2000 890000   # 不压缩
TO=20 ./run-public.sh pt891k 19064 3 2000 891000   # 压缩并循环（20s 后被 timeout 杀）
PT_AFTER=30000 TO=60 ./run-public.sh real1 19065 3 2000 100000,1100000
```
本次实际跑的是 internal-archive 里的原件 `run.sh`。它和 `run-public.sh` 只差 `R=` 那一行，公开副本本身没有重新跑过。
