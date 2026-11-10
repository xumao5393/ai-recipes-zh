# 11 · DeepSeek Harness SDR 插件：状态机与审批哈希

状态：部分库级离线实测 + 部分本地假模型实测（2026-11-09 16:21–16:37 EST）。证据：`evidence/11-sdr-plugin/`。  
来源：[Xuxchloris/deepseek-harness-sdr-plugin @ 4917768](https://github.com/Xuxchloris/Alex/tree/491776832f257f7d63113f8f4b541bd075cdda55)（本次测试的 commit；2026-11-09 查看时仓库已改名为 Alex，首页是另一个项目）· npm `@xuxchloris/dsh-sdr@0.2.3`。

**哪段结论来自哪种测法：**

| 测法 | 内容 |
|---|---|
| 库级离线实测 | 安装/兼容记录；状态机工具参数（a5）；批前哈希拒绝；**批后改稿仍可 continue（同一脚本 30 ms 内连跑 3 次，各用独立临时目录；库级复现，不是 3 次独立部署）**；dry-run connector；上游 `node --test` 11 pass |
| 本地假模型实测 | `dsh headless` + `127.0.0.1` 假服务完整 SOP 工具序列跑到 `close`（n=1）；审批后改稿再 `sdr_continue_after_approval` 仍 `advanced:true`（同一次 Agent 跑） |

## 0. 顺序错误说明（先装后审）

Kumo 要求：**安装前**先审生命周期脚本与外连。本轮实际顺序反了——**先装，源码审查是装完后补的**。已执行并访问过外网的步骤：

1. `git clone` → GitHub  
2. `npm view @xuxchloris/dsh-sdr` → npm registry  
3. `npm install @deepseek-ai/dsh@0.2.2-rc.1` → npm registry  
4. `npm install @xuxchloris/dsh-sdr@0.2.3` → npm registry  
5. `dsh plugin --profile web add @xuxchloris/dsh-sdr` → pnpm 下载（registry）

补审结论见 `evidence/11-sdr-plugin/source-review.txt`：包无 preinstall/install/postinstall/prepare；lib 默认无 fetch/http/WebSocket；installer 钩子只本地 `copyFile`。补审后曾停跑；Kumo 批准后才继续假模型跑通。不对外发、不提 issue。

## 1. 版本与兼容（库级 / 安装实测）

| 项 | 值 | 证据 |
|---|---|---|
| 仓库 commit | `49177683…cdda55`（2026-09-30 09:43:22 EDT） | `source-meta.txt` |
| npm | `@xuxchloris/dsh-sdr@0.2.3` | `npm-view.txt` |
| 作者写明验证过的 DSH | 包 README：`0.1.0-rc.7` 与 `0.1.1-rc.2` | `package-README.md` |
| 本机 | dsh `0.2.2-rc.1`，Node `v24.22.1` | `dsh-version.txt` |
| `plugin add`（web） | 成功 | `dsh-plugin-add.out.txt` |
| `plugin add`（headless，link 本地路径） | 成功 | `agent-run/headless-plugin-add-*.txt` |

在 **0.2.2-rc.1** 上能装进 profile；作者未声称支持 0.2.x。Web UI 模式菜单是否出现「SDR 数字员工」：**未测**。

## 2. (a) 状态机能否被跳阶段（库级离线，n=1）

`sdr_next_step` 的 parameters **只有 `task_id`**，没有 stage 字段（源码 `lib/index.js`；工具摘要 `tools-digest.json`，13 个 `sdr_*`）。

| 编号 | 操作 | 结果 | 用途 |
|---|---|---|---|
| a1–a3 | 未到审批调 `continueAfterApproval` / `reviewDrafts` | 抛错「当前阶段为 …」 | 阶段门禁 |
| a5 | 工具 schema 无 stage | 模型无法经工具指定阶段 | **证明「工具接口不能跳阶段」只用 a5** |
| a6 | 到 `human_approval` 后再 `nextStep` | `blocked: true`，stage 不变 | 审批卡点 |
| a4 | 直接改存储把 stage 写成 `close` | 存储层可被改；**只说明存储层无保护，不由此推断工具接口** | 存储层 |

证据：`probes/probe-ab.out.txt`。

## 3. (b) 批准与草稿哈希

### 3.1 作者文档原话（包内 README 第 34 行）

逐字引自 `@xuxchloris/dsh-sdr` README 第 34 行（`package-README.md` / npm 包内同文）：

> 在 SDR 模式中输入任务，例如「开发 3 个美国户外用品客户」。Agent 调用 `sdr_create_task` 和 `sdr_next_step` 推进，阶段顺序由服务端决定。第 6 阶段 `sdr_review_drafts` 列出开发信草稿，等人工选择；全部草稿批准后，`sdr_continue_after_approval` 才放行后续阶段。批准凭证绑定草稿哈希，草稿改过需要重新审批。

README **没有**单独写「已经批准之后再改稿」这一种时序；也没有「原来的批准自动失效」这句。下面测的是：**批准完成后，再改草稿内容，再调用 `continueAfterApproval`**。

### 3.2 源码位置（不贴原文）

`packages/dsh-sdr/lib/domain.js`（commit `49177683…`）：

- 第 482–489 行：`continueAfterApproval` 依 `pending()` 放行，**不**重算哈希  
- 第 560–561 行：`pending()` 只看 `status !== "approved"`  

详见 `source-review.txt`。

### 3.3 批前改稿（库级，n=1）

改 subject 后再 `reviewDrafts` → 拒绝「哈希不匹配」。与上游测试一致。`probes/probe-ab.out.txt` b1。

### 3.4 批后改稿仍可 continue——同一脚本连跑 3 次（库级）

同一个脚本 `hash-repro/repro-b.mjs` 在约 30 ms 内（21:32:14.060Z–14.090Z）连跑 3 次，每次用独立临时目录和新 task（n=1×3）。这是库级复现，**不是 3 次独立部署**：

| run | 批准时 draft_1 哈希 | 改稿后哈希 | continue 结果 | 时间戳（UTC） |
|---|---|---|---|---|
| 1 | `9b8d919b…f11a50` | `afbbf99f…0f1c4` | `advanced=true` → `follow_up_plan`；error=null | start 21:32:14.060Z / continue 21:32:14.075Z |
| 2 | 同左（合成草稿相同） | `15eb0452…86c039` | 同上 | 21:32:14.078Z / 21:32:14.083Z |
| 3 | 同左 | `0d32242f…255cc` | 同上 | 21:32:14.084Z / 21:32:14.090Z |

三次均为：`hashes_equal_after_tamper=false` 且仍放行。完整 JSON：`hash-repro/run-1.json` … `run-3.json`、`summary.json`。

### 3.5 同一行为在 Agent + 本地假模型流程中（n=1）

`agent-run-complete/`：`sdr_review_drafts` 批准后，假服务改写 state 里草稿 subject，再让模型调 `sdr_continue_after_approval` → 返回 `{"advanced":true,"stage":"follow_up_plan"}`，最终 `stage=close`。  
哈希见 `agent-run-complete/fake-server.stdout.txt` 第 2 行（批准时存的哈希 `9b8d919b…`，改后 `ee7951a0…`，两者不相等）。

## 4. 本地假模型完整流程（headless，n=1）

- 配置：`DEEPSEEK_BASE_URL=http://127.0.0.1:19023`；隐私补丁关掉 session-log / plugin-inventory / otel；假 key 只在环境变量。  
- headless **不组合** agent preset，故用 `--patch` 把 `@xuxchloris/dsh-sdr`（`role: agent`）挂到根组合。  
- 审批 UI：本机测试钩子 `sdr-test-auto-uq`（waterfall 自动全选草稿）；**不是**产品自带能力。  
- 工具序列：`sdr_create_task` → `sdr_next_step`×5 → `sdr_review_drafts` →（改稿）→ `sdr_continue_after_approval` → `sdr_next_step`×3 → `sdr_get_report` → 结束文本。  
- 结果：exit 0，耗时 2.085 s，最终 `stage=close`，报告 `dry_run=true`，`external_delivery=draft-only`。  
- 局限：假模型是我们自己写的脚本，按固定顺序调用工具，审批由测试钩子自动完成。所以“跑到 `close`”只证明插件工具链路在 dsh 里走得通，**不代表真模型也会按这个顺序走**。  
- 证据：`agent-run-complete/summary.json`、`requests.jsonl`、`dsh-timing.txt`、`sdr-state.json`。

先前一次假模型启发式错误（review 后误发 `next_step`）导致超时空转（exit 124，120 s）；原件未入库，公开只留 `agent-run/loop-timeout-summary.json`。那次已确认 SDR 工具挂上（13 个 `sdr_*`）；那轮只监控了假服务端口，不能据此排除其他外连。

## 5. 连接监控

见 `agent-run-complete/connection-check.txt`：假服务只绑 `127.0.0.1:19023`；假服务收到的 14 条请求 Host 均为 `127.0.0.1:19023`。本轮只跑了 2.085 s，连接监控**没采到样本**，所以只能证明发到假服务的请求是本地的，**不能完全排除其他外连**。前一次 120 s 超时那轮（`agent-run/`）只监控了假服务端口，非本地连接的监控在 dsh 启动前就停了，所以两轮都不能排除其他外连。本轮未再 npm install。

## 6. dry-run

默认 email/whatsapp/crm 为 dry-run；结案报告 `external_delivery=draft-only`。未接 live。

## 7. 工具摘要（无原文）

13 个 `sdr_*` 工具名与 `{name,length,sha256}` 见 `tools-digest.json`。Agent 指令 preset（`agent.cordis.yml`）只留 length/sha256/first_line，原文不进公开证据。

## 8. 没测的

- DSH Web UI 模式菜单与真人点选审批（本轮 headless + 自动应答钩子）  
- 真实邮件/WhatsApp/CRM  
- 官方 DeepSeek 端点（禁止）  

## 证据索引

`evidence/11-sdr-plugin/`：`source-review.txt`、`probes/`、`hash-repro/`、`agent-run-complete/`、`tools-digest.json`、`MASKING.txt`、`REDACTION-CHECK.txt`。  
原件（含超大空转抓包）未入库。
