# 05 dsh-trade-assistant：外贸询盘规则插件，和我们的关键词脚本放在同一批 22 封上对照

**一句话结论**：这个插件在我们这 22 封询盘上，分类对了 4/14（第一批里有 4 封属于插件没有的类别，它不可能分对；第二批里也有 2 封）和 3/8，诈骗报警抓到 6 封里的 2 封。我们的脚本抓到 4 封，但这 4 封全在写规则时看过的第一批；规则冻结后的第二批有 2 封诈骗，两边都是 0/2。那封冒充同事、带真实订单号的骗局，插件和我们的脚本都没认出来，两边都放进了“无法判断 / 待人工”。这只是在这 22 封上跑了一次的对照（n=1），不代表它在别的邮件上也是这样。

## 测的是什么
- 插件：[xiong18166089606-design/dsh-trade-assistant](https://github.com/xiong18166089606-design/dsh-trade-assistant)，固定在 commit [`ddce5828`](https://github.com/xiong18166089606-design/dsh-trade-assistant/commit/ddce5828517f07899e93d4203490c14b2ffc8002)。这是一个 DeepSeek Harness（dsh）插件，提供 `trade_inquiry_reply` 工具：把询盘原文贴进去，它判断询盘类型（具体采购、比价、样品、代理、泛询价、钓鱼诈骗），提取数量、付款方式等字段，并对诈骗特征分高/中/低危报警。
- **它是 0 星、0 fork、0 issue 的仓库（2026-11-09 17:29 EST 查询，见 [repo-meta.txt](evidence/05-dsh-trade-assistant/repo-meta.txt)），没有找到别人用过的证据。**
- **它是纯规则（正则）引擎，不调用模型**：源码里没有任何网络调用，我们也是在断网环境里跑的。
- 对照组：老板办公 03（boss-office 专题的外贸询盘篇，暂未入库） 已经锁定的关键词脚本 `triage.py`，以及那里的两批虚构询盘：第一批 14 封，第二批 8 封，正确答案是事先标好的。我们没有新编任何询盘，也没有改样例或规则。跑之前先用 `sha256sum -c` 核对过，全部 OK（[run-ours-hash.txt](evidence/05-dsh-trade-assistant/run-ours-hash.txt)）。
- 选在跨境专题，没放老板办公，原因有两个：老板办公 PLAN 里的 04 号已经留给“装修报价”；而这个插件本身是给外贸业务员用的 B2B 询盘工具。编号用 05，是因为跨境 04 已经被同一时段新写的《订单日报》占用了。测试数据和对照脚本直接链接到老板办公 03，没有复制改动。

## 先审源码，再运行
完整记录见 [source-review.txt](evidence/05-dsh-trade-assistant/source-review.txt)，结论如下：
- `package.json` 里**没有 scripts 字段**，也就没有 preinstall、install、postinstall、prepare 这类安装时自动跑的脚本。没有运行时依赖，只有两个 dsh 的 peerDependencies。
- 运行时代码里**没有** fetch、http(s)、net、WebSocket、child_process、eval、文件读写，也没有读环境变量。`index.js` L42/L74 的 `exec` 是宿主传进来的参数名，不是执行子进程。
- 因为 `lib/inquiry.js` 没有任何 import，所以**没有安装这个包，也没有启动 dsh**。我们直接用 node 调它的 `analyzeInquiry`，外面套一层 `unshare -rn`（单独的网络命名空间，任何外连都会失败）。4 次运行都是 exit 0，每次约 0.033–0.035 秒（n=1/次）。
- 上游自带的单测：照 README 写的 `node --test test/` 在 Node v24.22.1 上**失败**，exit 1，原因是 Node 把 `test/` 当成了模块路径，报 Cannot find module（在 clone 根目录照原样跑，见 [run-upstream-test-readme.txt](evidence/05-dsh-trade-assistant/run-upstream-test-readme.txt)；之前从上一级目录用 `src/test/` 跑也是同样的错，见 [run-upstream-test.txt](evidence/05-dsh-trade-assistant/run-upstream-test.txt)）。改成 `node --test test/inquiry.test.js` 后 13/13 通过（[run-upstream-test-file.txt](evidence/05-dsh-trade-assistant/run-upstream-test-file.txt)）。

## 怎么比（跑之前就定好）
- 映射表 [mapping.json](evidence/05-dsh-trade-assistant/mapping.json)：插件的“钓鱼/诈骗”对应我们的“诈骗/钓鱼风险”，“具体采购”对应“真询盘”，“比价”和“泛询价”对应“泛问/低价值”，“无法判断”对应“待人工”。“样品需求”和“代理/分销”在 03 的分类里没有对应，记为“无对应”，算错。
- **插件按设计就没有“老客户跟进”和“广告”这两类，也不看发件人域名。** 所以有 6 封（第一批 E04、E06、E11、E12，第二批 H03、H07）它不可能分对。下面同时给出去掉这 6 封之后的分数。
- 插件算“报警”的条件：类型判成钓鱼/诈骗，或者出现任何一条高危/中危提示；低危不算。我们的脚本算“报警”的条件：分类为诈骗/钓鱼风险。
- 插件的输入是“主题 + 空行 + 正文”，模拟业务员把邮件贴进去。另外跑了一个在最前面加 From 行的变体，只看敏感性，不计入主分数。
- 映射表、调用脚本和对比脚本在运行前都存了哈希（[pre-run-sha256.txt](evidence/05-dsh-trade-assistant/pre-run-sha256.txt)，17:30:01 EST），跑完复核一致。去掉 6 封后的分数和诈骗召回是**跑完才补算的**（[posthoc_subscores.py](evidence/05-dsh-trade-assistant/posthoc_subscores.py)）。

## 结果（每批各跑 1 次，n=1）
逐封表见 [compare-output.txt](evidence/05-dsh-trade-assistant/compare-output.txt)，补算结果见 [posthoc-output.txt](evidence/05-dsh-trade-assistant/posthoc-output.txt)。

| | 插件 | 我们的脚本 |
|---|---|---|
| 第一批分类（14 封） | **4/14** | 14/14（循环验证：写规则时看着这批邮件） |
| 第二批分类（8 封，规则冻结后才写的） | **3/8** | 3/8 |
| 去掉插件没有的两类后：第一批 | 4/10 | 10/10 |
| 去掉插件没有的两类后：第二批 | 3/6 | 2/6 |
| 报警判断对（该报的报了、不该报的没报，第一批） | 12/14 | 14/14 |
| 报警判断对（第二批） | 6/8 | 6/8 |
| 诈骗召回（共 6 封诈骗） | **2/6**（E03、E13） | 4/6（E03、E05、E08、E13，全在第一批，属循环验证） |
| 其中第二批诈骗召回（规则冻结后，2 封） | 0/2 | 0/2 |
| 误报（非诈骗被报警） | 0 | 0 |

逐封看几处差别：
- **E05 仿冒老客户域名改收款账户**：插件判“无法判断”，没有任何风险提示。它不比对发件域名，正文里的“accounts have moved / new account”也不在它的规则里。我们的脚本靠域名相似度抓到了。
- **E08 仿冒 Air Liquide、要 net 60 账期、收货地址待定**：插件判成“具体采购”，也就是当成了最高价值的真询盘，没有报警。
- **E13 交注册费**：插件给出了高危提示（预付费），但类型判“无法判断”。加 From 行的变体里，它又因为发件人里有 agent 一词判成了“代理/分销申请”，高危提示还在。
- **H02 一个 40 尺柜，没写 pcs**：插件判“具体采购”，对；我们的脚本落进“待人工”，错。
- **H03 老客户返单**：插件判“具体采购”，没认出是老客户。
- **H04 “打开附件并启用编辑”**：两边都漏。插件的附件规则只认“attachment”这个词，这封写的是“attached document”。
- 加 From 行的变体：分数和主输入完全一样，只有 E13 的类型变了。

## 冒充同事、带真实订单号的那封（H01）
> 发件人是 outlook 免费邮箱，说“Tom 休假了，我接手 PO#2291，请把发票发到这个邮箱，等我们新的汇款指示”。

- **插件：没认出。** 判“无法判断”，没有提取到任何字段，没有任何风险提示（高/中/低危都没有）。
- **我们的脚本：没认出。** 判“待人工”。
- 两边都没把它误判成真询盘或老客户，都交给了人。但两边都没有发出诈骗警告。插件不看发件人，也不知道老客户名单和在跑的订单号，按它的设计就抓不住这一类。

## 局限
- 这是对这 22 封虚构询盘各跑一次的对照，样本很小。第一批是我们写规则时看过的，所以我们脚本的 14/14 不能算本事。插件对两批都没见过，但这些询盘是我们按自己的分类写的，对插件不一定公平。
- 映射表是我们定的。插件有“样品需求”“代理/分销”两类，在我们的分类里没有对应（E10 因此算错）。
- 只测了 `trade_inquiry_reply` 的分类、字段和报警。**没测**：作为 dsh 插件加载（`dsh plugin add`）、在 dsh 里让模型调用它、它给出的回复大纲质量、`product_copy_multilang` 多语言文案。
- 字段提取只顺带看了，没有打分。例如 E14 的规格提成了“grade: 304. Please send catalog.”，H02 的“一个 40 尺柜”没提出数量。

## 能不能用
- 想拿它当诈骗过滤器，在这 22 封上不够：6 封诈骗只报了 2 封，仿冒老客户域名、冒充同事这两类骗法都没报。
- 它不看发件人，所以老客户名单、域名比对这一步仍然要自己做，或者交给人。
- 所有发出去的回复和收款账户变动，照老板办公 03 的做法，都由老板确认。

## 证据
目录 [evidence/05-dsh-trade-assistant/](evidence/05-dsh-trade-assistant/)。命令、时间戳（EST）和耗时都在各个 `run-*.txt` 里。上游原文件只留了 sha256 和 commit 链接（[UPSTREAM-SHA256.txt](evidence/05-dsh-trade-assistant/UPSTREAM-SHA256.txt)），打码说明见 [MASKING.txt](evidence/05-dsh-trade-assistant/MASKING.txt)。

> 另：上游历史里有一个已删除的凭据类临时文件，我们没读取值，也没用。
