# 10 Project Tango：本地假店铺 MCP，离线测试与最小读取

**一句话结论**：这是一个走 stdio 的 MCP 假电商服务器（商品 / 库存 / 订单 / 补货建议），自带 SQLite 种子数据。源码审查没有发现本仓库的安装期自动脚本；间接依赖 esbuild 的 postinstall 已读过。本机 Node v24.22.1 满足 `>=22.5.0`（n=1）。`npm ci` 时 npm 警告 esbuild postinstall 尚未被 allowScripts 覆盖，但文件层面的硬链接表明这次 postinstall 实际跑过（详见正文 §3）。`npm test` 在断网命名空间里 **287/287 通过**（n=1），与 README 徽章写的 287 一致。用 MCP 客户端连上本地进程后，读到的是**种子数据**：13 个商品、6 条低库存预警、补货建议窗口里 142 单（n=1）；`find_orders` 必须带过滤条件。没有接任何真店或外部模型。这篇只说明能装、能跑、自带测试能过，不是推荐。

- 仓库：[CoderGamerUnknow/Project-Tango](https://github.com/CoderGamerUnknow/Project-Tango)，固定在 commit [`114ca95d`](https://github.com/CoderGamerUnknow/Project-Tango/commit/114ca95dfbda877a7ac2f0a0d75b2e57ec308365)（v3.2.0）。2026-11-09 19:30 EST 查询时 0 星、0 fork（见 [repo-meta.txt](evidence/10-project-tango/repo-meta.txt)）。没有找到别人实际使用的记录。
- README 自己写着：本地优先、无网络监听；DataProvider 可换成 Shopify/Stripe。我们也**没接**真店 API。

## 1. 先审源码（详见 [source-review.txt](evidence/10-project-tango/source-review.txt)）
- 本仓库 `package.json`：**没有** preinstall / install / postinstall / prepare；只有 pretest / prebuild（用户跑 test/build 才触发）。
- 运行时依赖：`@modelcontextprotocol/sdk`、`zod`；开发依赖含 `tsx`（进而带上 `esbuild`）。
- lockfile 里带安装脚本的包：`esbuild@0.28.2`（已 pack 阅读 `install.js`：代码主路径先 `require.resolve` 本机 `@esbuild/<platform>`，失败才回退拉 registry.npmjs.org——这是读代码的结论）、`fsevents`（仅 darwin）。
- 运行时代码：stdio MCP + `node:sqlite`；非测试代码里没有 fetch / 监听端口。
- 结论：**可以 npm ci，然后只做离线测试和本地 stdio 读取。**

## 2. Node 版本
- 要求：`engines.node >=22.5.0`（因为 `node:sqlite`）。
- 本机：v24.22.1，semver 满足（[node-version.txt](evidence/10-project-tango/node-version.txt)，n=1）。**没有**另装系统 Node，也没有动其它 agent 的环境。

## 3. npm ci（装依赖）与 esbuild postinstall
- `npm ci` exit 0，45.4s，185 packages（[run-npm-ci.txt](evidence/10-project-tango/run-npm-ci.txt)，n=1）。日志原文：
  ```
  npm warn install-scripts 1 package has install scripts not yet covered by allowScripts:
  npm warn install-scripts   esbuild@0.28.2 (postinstall: node install.js)
  ```
  `npm install-scripts ls` 事后仍把该包列在 “not yet covered”（n=1）。
- **postinstall 到底跑没跑：** 跑过。依据见 [esbuild-postinstall-check.txt](evidence/10-project-tango/esbuild-postinstall-check.txt)（n=1）：
  - 本轮 `esbuild/bin/esbuild` 与 `@esbuild/linux-x64/bin/esbuild` **同一 inode（硬链接）**、均为 11427952 字节；mtime 落在 npm ci 期间（19:29:54 EST）。
  - 这与 `install.js` 里 `maybeOptimizePackage` 的 `linkSync`+`renameSync` 效果一致。
  - 对照：同 lockfile 在临时目录 `npm ci --ignore-scripts` 后，`esbuild/bin/esbuild` 仍是 **9350 字节的 JS 包装器**，与平台包二进制 inode 不同。
  - 无 `downloaded-*` 落盘标记。
- 断网下 `node_modules/esbuild/bin/esbuild --version` → `0.28.2`（n=1）。
- 读 `install.js` 可知：主路径用已装的 optional 平台包；找不到时才访问 registry。npm ci 日志里也没有 “Trying to download” 字样——但**单凭“日志没有回退字样”不能证明没走回退**；这次是靠硬链接 / ignore-scripts 对照和无 `downloaded-*` 来判断走了主路径。
- npm 提示 14 个漏洞（12 moderate / 2 high）——本轮**没有**逐条核对，只记下有提示。

## 4. npm test（离线）
- `unshare -rn` + 打开回环口后跑 `npm test`（仍无外网）：**tests 287 / pass 287 / fail 0**，duration ≈ 8.1s，总 wall ≈ 11.0s（[run-npm-test.txt](evidence/10-project-tango/run-npm-test.txt)，n=1）。
- 与 README 徽章「tests-287」和正文「287 tests」一致。
- 测试会起临时数据目录，不碰 `~/.project-tango`。测试里的 MCP 子进程 ≠ 已接到外部 Agent。

## 5. 本地假店最小读取（stdio，n=1）
用我们写的 MCP 客户端脚本启动 `tsx src/index.ts`，数据目录指到一次性临时目录（[run-min-read.txt](evidence/10-project-tango/run-min-read.txt)）。下面读到的都是**自带种子数据**，不是真实店铺行为：

| 调用 | 结果 |
|---|---|
| 工具列表 | 8 个：list_all_products、get_low_stock_alerts、analyze_sales_metrics、find_orders、smart_restock_predictor、draft_product_copy、simulate_order_placement、reset_demo_state |
| list_all_products | 13 个商品（含 tech/apparel/home 等） |
| get_low_stock_alerts | alertCount=6，criticalCount=4，thresholdUsed=5；例如键盘 currentStock=0 |
| find_orders（customer_name=a, limit=5） | 返回 5 条；无过滤条件时服务端报错要求至少提供 order_id 或 customer_name |
| smart_restock_predictor | window 内 ordersInWindow=142 / totalOrders=142；6 条补货建议 |

stderr：`Project Tango MCP server running on stdio. State: …/state.db (SQLite, WAL)`。全程无外网。

## 没测的
- 没接 Shopify / Stripe 或任何真店；没换 DataProvider。
- 没接到 Grok Bot / dsh / 其它 Agent 宿主；只做了 SDK 客户端的 stdio 最小读取。
- 没跑 `npm run test:coverage`、`npm run verify`、`npm run inspect`（会拉 inspector）。
- 没测 `simulate_order_placement` / `reset_demo_state` / `draft_product_copy` / `analyze_sales_metrics` 的业务对错（测试套件盖了它们，但我们没有单独手算对照）。
- 没评估 npm audit 列出的 14 个漏洞是否可利用。
