# 09 外贸工作台 DSH 插件：离线审查与装柜计算核对

**一句话结论**：这是一个挂进 DeepSeek Harness Web 侧栏的离线外贸工作台（装柜计算 + 报价/PI/装箱单等 A4 预览）。源码和 npm 1.0.1 包都没有安装期自动脚本，也没有运行时外连。它**没有声明**支持的 dsh 版本；我们在本机 dsh 0.2.2-rc.1 上用本地 link 装进 web profile 成功（n=1），`dump-config` 能看到面板条目，真实 `dsh web` 同源路由返回的 `workbench.html` 与包内文件字节一致（n=1）。装柜计算：在 node 里用 vm 加载 workbench.html 自带的装柜 IIFE（未改字节），调用插件暴露的 `LG.calc`（即 lgCalc），对 3 组假货物的 totalCbm / totalGw / nEst 与事先写好的手算一致（n=1/组）。手算是照插件源码里的规则写的，所以这只说明插件代码按它自己的规则在算，不能说明柜型容积表或装载算法对真实装柜合理。没有测单证 PDF 打印、卖方信息迁移，也没有在浏览器里点侧栏图标做完整 UI 验收。

- 仓库：[southcul/demian-trade-suite-dsh-plugin](https://github.com/southcul/demian-trade-suite-dsh-plugin)，固定在 commit [`e4c909ec`](https://github.com/southcul/demian-trade-suite-dsh-plugin/commit/e4c909ecd13beb7eba118815f61ba5b4eb15afaa)（npm `dsh-plugin-demian-trade-suite@1.0.1`）。2026-11-09 19:23 EST 查询时 0 星、0 fork（见 [repo-meta.txt](evidence/09-demian-trade-suite/repo-meta.txt)）。没有找到别人实际使用的记录。
- README 自己写着：插件只负责 UI 入口；Agent 出单技能需另装 demian-trade-suite。我们也**没测** Agent 出单。

## 1. 先审源码（详见 [source-review.txt](evidence/09-demian-trade-suite/source-review.txt)）
- `package.json` 的 scripts 只有自定义 `package`（打 zip），**没有** preinstall / install / postinstall / prepare / prepack。
- **没有任何 npm 依赖**（dependencies / peerDependencies 皆无）；也没有 engines。
- 宿主半 `index.js`：只读包内 `assets/workbench.html`，注册到本机 Web 服务的 exact 路径 `/plugins/demian-trade-suite/workbench.html`。
- 客户端半 `client.js`：侧栏入口 + 中间栏 iframe，指向上述同源路径。
- `workbench.html`：单文件工作台。检索未发现 fetch / XHR / WebSocket / CDN script；只用 localStorage、本机 Blob 导出和 `window.print()`。
- npm 1.0.1 tarball 与 git 对应文件 sha256 全部一致（[UPSTREAM-SHA256.txt](evidence/09-demian-trade-suite/UPSTREAM-SHA256.txt)）。
- 结论：**默认路径不出外网，可以继续加载和离线核对。**

## 2. 版本：未声明
- package.json 无 engines、无 peerDependencies（[semver-result.txt](evidence/09-demian-trade-suite/semver-result.txt)，n=1）。
- 按本轮规则：未声明版本且源码审查干净 → 允许尝试加载。我们没有改它的 package.json，也没有用 allow-version / --force。

## 3. 装进本机 dsh web（隔离 HOME）
- `dsh plugin --profile web add <本地源码目录>`，在 `unshare -rn` 断网命名空间里跑，**exit 0**，pnpm link 成功（[run-plugin-add.txt](evidence/09-demian-trade-suite/run-plugin-add.txt)，n=1，0.749s）。
- `dsh --profile web --dump-config` 末尾出现 `id: demian-trade-suite-panel` / `name: dsh-plugin-demian-trade-suite`（[run-dump-config-demian.txt](evidence/09-demian-trade-suite/run-dump-config-demian.txt)，n=1）。
- 真实启动：`dsh --profile web --no-open --host 127.0.0.1 --port 0`（同样断网 + 回环口），对 `/plugins/demian-trade-suite/workbench.html` 发 GET → **HTTP 200**，正文 **375618 字节**，sha256 与包内 `assets/workbench.html` **完全一致**（[run-dsh-web-workbench.txt](evidence/09-demian-trade-suite/run-dsh-web-workbench.txt)，n=1）。启动后立刻结束进程；未开浏览器，未发模型请求。
- 补充：不启 dsh、只 `import index.js` 的 mock 路由也能 200/405（[run-mock-route.txt](evidence/09-demian-trade-suite/run-mock-route.txt)，n=1）——验证的是同一段 handler，不是完整 UI。

## 4. 装柜计算核对（假数据；跑的是插件自己的 lgCalc）
输入见 [fake-input.json](evidence/09-demian-trade-suite/fake-input.json)，手算见 [hand-calc.md](evidence/09-demian-trade-suite/hand-calc.md)，哈希见 [pre-run-sha256.txt](evidence/09-demian-trade-suite/pre-run-sha256.txt)（**19:24:55 EST 写好后未再改**；返工复跑 19:37:46 EST 仍用同一对哈希）。

**怎么跑的：** 从 `assets/workbench.html` 切出装柜 IIFE 的连续未改字节（53098 字节，sha256 `0e8c197a…`，与 git/npm 包内同文件同偏移切片逐字节一致，见 [lg-iife-extract-meta.txt](evidence/09-demian-trade-suite/lg-iife-extract-meta.txt)），在 node `vm` 里加载，DOM/`localStorage`/canvas 用最小桩代替（桩让 `lgInit` 因没有 `#lgCanvas` 提前返回，不改 IIFE 源码）。然后调用插件暴露的 `window.LG.calc`（即源码里的 `lgCalc`）。桩与驱动见 [run_vm_lgcalc.mjs](evidence/09-demian-trade-suite/run_vm_lgcalc.mjs)，输出见 [run-vm-lgcalc.txt](evidence/09-demian-trade-suite/run-vm-lgcalc.txt)（exit 0，n=1/组）。

提取件本身不入库；读者可自行从 commit [`e4c909ec`](https://github.com/southcul/demian-trade-suite-dsh-plugin/commit/e4c909ecd13beb7eba118815f61ba5b4eb15afaa) 的 `assets/workbench.html` 按字节切出并核对（本机复跑见 [extract-howto-verify.txt](evidence/09-demian-trade-suite/extract-howto-verify.txt)，n=1）：

```bash
# 0-based 起点 322489 → tail -c +322490；长度 53098
tail -c +322490 workbench.html | head -c 53098 | sha256sum
# 期望：0e8c197a088f6148a388ca2cabcf23e5b4780c392d018049d4e5e8f9ee7c535f
```

返工前曾用过我们改写的 `run_offline.mjs`（var→const、函数抽出），那次**不算**对插件代码的核对，结果仅作历史对照留在 evidence。

| 组 | 手算 totalCbm / totalGw / nEst(20GP,40HQ) | 插件 LG.calc | 一致 |
|---|---|---|---|
| A 50×40×30×100 无包装 | 6.000000 / 1100 / 1,1 | 相同 | 是 |
| B 同上 packThick=2 | 8.078400 / 1100 / 1,1 | 相同 | 是 |
| C 源码 demoItems 三货 | 38.409600 / 12465 / 2,1 | 相同 | 是 |

插件 lgCalc 还给出了装载率 usage（排布引擎输出，手算未猜）：C@20GP usage≈79.68% 且只装下 480/810 箱，C@40HQ usage≈50.51% 全装下——与 nEst=2 / 1 的方向一致，但 usage 本身没有独立手算对照。

注意：上面的手算是照插件源码里的规则写的（eff 尺寸、totalCbm、nEst 公式）。“一致”只证明**插件自己的 lgCalc**按它源码写的规则在算，不证明柜型容积表或装载算法对真实装柜合理。

## 没测的
- 没有在浏览器里点侧栏「外贸工作台」做完整 UI 验收（图标、iframe 卸载/恢复、主题）。
- 没测单证 A4 预览/打印、金额大写、定金尾款、导出 PDF/JSON、卖方信息 localStorage 迁移。
- 没测装柜动画、堆码/承压/间隙/整托等高级选项的逐项正确性（只跑了无包装主路径的闭合量）。
- 没装、没测作者说的 Agent 出单技能库 demian-trade-suite。
- 全程没有接任何模型，没有请求打到 DeepSeek 官方地址。
