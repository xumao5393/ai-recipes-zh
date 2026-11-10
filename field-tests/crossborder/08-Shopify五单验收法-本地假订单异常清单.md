# 08 Shopify 五单验收法：Grok Bot 离线判本地假订单

实测时间（正式组）：2026-11-09 19:26:33 EST 派出，3 次并行。环境：本机 Linux。不登录、不注册、不接任何 Shopify 店、不调用店铺 API、不对外发消息。

**一句话结论**：正式组把中性名假订单和原文 first-task instruction 交给 Grok Bot 新开的后台子任务（不带本对话上下文）离线判异常清单，跑了 3 次（n=3）。**冻结打分器正式分数是 1/3 PASS**（A PASS，B/C FAIL）。按同一份打分文件，3 次的分类都对：都排除了正常单，第 5 单都标 incomplete、没猜类型。这只覆盖这一条提示词、这一组 5 单假订单、n=3，不能外推成「Grok Bot 能稳定分拣订单」。

**方法标签：方法来自网站文章，没有他人实测数据。来源是在推销自家套件的网站。**

## 测的是什么
- 来源：[Whisker Beacon · How to use Grok Bot for Shopify](https://whiskerbeacon.com/guides/shopify-automation-with-grok-bot/)。页面标注 Reviewed 1 Sep 2026。作者署站点名，无个人署名。页面末尾在推销自家的 Full Front Office Kit，并引导读者看自家「Grok Bot + Shopify」页。
- 文章主张：不要一上来让 Bot 管店；先做一份**不能**退款/取消/折扣/改库存/联系客户的「履约异常」日清单；缺证据标 incomplete，不许猜。
- 验收法（文章原文意译）：准备 5 单——1 正常已履约、1 地址问题、1 欠货、1 超期、1 缺履约信息；通过标准是找出真异常、排除正常单、不编缺失字段。
- **正式组测的对象是 Grok Bot**：新开的后台子任务，不带本对话上下文；只给中性名假订单 JSON 和原文那段 first-task instruction 的原样摘录（表格字段名与原文一致）。没有给参考答案，没有给 `rules.md`，也没有另加 `missing:` 约定或类别标签提示。

## 编号与目录
本篇编号 **08**（登记见 `crossborder/PLAN.md`）。

## 主结论（正式组，n=3）

### 相对预试改了什么
- 客户名、商品标题、SKU 全部换成中性字样（如 Jordan Lee / Ceramic Mug / SKU-4417），不再用 Alice Normal、Bob Address、Eve Incomplete、Mystery Widget 这类提示答案的名字。
- 提示词里**不再**另加输出格式段：只保留原文表格字段名；没有 `missing:<path>` 约定，也没有把 4 个异常类别写成枚举提示。
- 取值核对写进冻结打分器 `score_main.py`（跑前就哈希冻结），不再事后另写核对脚本。

### 冻结与派出
- 冻结时间 **2026-11-09 19:25:28 EST**，见 `main-runs/FROZEN.sha256`：
  - `orders-neutral.json` → `c651d504…7503`
  - `prompt-main.txt` → `573637e8…709d`
  - `score_main.py` → `a62c66e6…63b3`
- 核对方式：`head -3 FROZEN.sha256 | sha256sum -c` 对上述三文件均 OK。文件末尾多了一行 `frozen at …` 说明文字，所以对整份文件跑 `sha256sum -c` 会多一条 format warning；这不是哈希失败。
- 派出时间 **19:26:33 EST**（见 `main-runs/dispatch-log.txt`）：3 个互不相通的新开后台子任务，同一份冻结提示词。

### 打分器自检（跑正式组之前）
- 好样本 `selftest-answer.md`：OVERALL PASS。
- 坏样本 `selftest-bad.md`：OVERALL FAIL；第 5 单 value check 报 not found：`2026-11-10`、`in stock`（故意编进 incomplete 行的假值）。

### 工具调用
3 次均为 **0 次工具调用**（见 `main-runs/tool-use-check.txt`）。但提示词第一句就是 "Do NOT use any tools"，所以这只说明它照指令做了，不说明它在能用工具时会怎么做。离线测试这个设定是我们自己加的，原文里没有。

### 冻结打分器正式结果：**1/3 PASS**
| 次 | OVERALL | 来源 |
|---|---|---|
| runA | PASS | `score-runA.txt` |
| runB | FAIL | `score-runB.txt` |
| runC | FAIL | `score-runC.txt` |

正式 FAIL 条目（共 4 条，原句出处见人工复核记录）：

1. **runB · #FAKE-1003 value check** not found `fulfilled` ← 原文短语 `"Partially fulfilled"`（数据里是 `fulfillment_status=partial`）。
2. **runB · #FAKE-1005 value check** not found `backordered` ← 原文短语 `"whether it is backordered or late"`（Exception 格仍是 incomplete）。
3. **runB · 禁止动作检查** 命中 `refunded` ← 原文短语 `"Nothing was refunded"`。
4. **runC · 禁止动作检查** 命中 `refunded` ← 原文短语 `"Nothing was refunded"`。

### 事后人工复核（不改正式分数）
看过输出之后做的人工通读（`manual-review-runB.txt`、`manual-review-runC.txt`），**不改动**上面的 1/3 正式分数。4 条 FAIL 都是关键词误报：改写（paraphrase）或否定句。**「0 条编造字段值」来自这次人工通读，不是脚本算出来的。** 打分器局限：关键词匹配不懂否定和改写。

### 分类（3 次相同；取自打分文件）
| 订单 | 期望 | 3 次正式组 |
|---|---|---|
| #FAKE-1001 正常已履约 | 不出表 | 均未进表 |
| #FAKE-1002 | 出一行 address_problem | 均 address problem |
| #FAKE-1003 | 出一行 backorder | 均 backorder |
| #FAKE-1004 | 出一行 late_shipment | 均 late shipment |
| #FAKE-1005 | 出一行 incomplete，不填 evidence 以外的字段 | 均 incomplete；Exception 格未再匹配其他类别 |

异常行数：3 次都是 4 行。

## 预试（n=3，不算数）
更早有一组预试（19:21–19:22 EST，证据在 `agent-runs/`）。客户名和商品标题会提示答案；提示词里还加了含 `missing:` 约定和类别标签的输出格式；取值核对脚本是看过输出之后才写的。所以预试**不算正式结果**，只保留作对照。预试原打分也是 1/3 PASS，原因与正式组不同（incomplete 行多列了真实存在的字段，旧脚本一律当编造）。

另有一次自写确定性脚本按 `rules.md` 跑假订单的自检（n=1），只用来确认参考答案和对照脚本能跑通，不是对 Agent 的实测。

## 没测的
- 真实 Shopify 店、Shopify Admin / 自定义 App / 任何 OAuth 或 API 调用。
- Grok Bot 连接器、routine、或把异常清单交给真人审批的闭环。
- 文章后半的低库存报告、供应商跟进草稿、客服草稿、评论回复。
- 退款/取消/折扣/改库存/联系客户（按文章本就不该由 Bot 自动做）。
- 用真实历史订单或别人的数据复现；**没有他人实测数据**。

## 局限
- 3 次是同一产品、同一配置、同一提示词（底层用什么模型我们不知道），不是彼此独立的评测人；n=3 也偏小。
- 本结果只覆盖**这一条提示词、这一组 5 单假订单、n=3**，不能外推成「Grok Bot 能稳定分拣订单」。
- 没有接真实 Shopify 店、连接器、routine 或审批闭环。
- 字段级期望和打分规则是我们写的；文章没有给字段级定义。
- 冻结打分器用关键词匹配，不懂否定和改写（见上「事后人工复核」）。

## 证据
`evidence/08-shopify-five-order/`：
- **正式组** `main-runs/`：orders-neutral.json、prompt-main.txt、score_main.py、FROZEN.sha256、selftest-answer.md、selftest-bad.md、dispatch-log.txt、runA/B/C.raw.md、score-runA/B/C.txt、manual-review-runB/C.txt、tool-use-check.txt、SUMMARY.txt、raw-outputs.sha256（三次原始输出，可直接 `sha256sum -c raw-outputs.sha256` 验）、transcripts-not-public.sha256（未公开 transcript 的哈希，仅作对照，公开侧无法验）。
- **预试** `agent-runs/`（不算数）。
- 旧自检与假订单原稿：fake-orders.json、hand-expected.md、rules.md、compare_to_hand.py 等；method-label.txt、MASKING.txt、REDACTION-CHECK.txt。

提示词里引用了原文 5 句短句（来源链接见上），整页摘录和改写前副本只留内部档案；三次的 transcript 原件也不公开，只在 `transcripts-not-public.sha256` 里留哈希。
