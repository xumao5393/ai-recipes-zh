# 06 Xander（早早下班小助手）：亚马逊运营插件，离线审查与计算器核对

**一句话结论**：这是给亚马逊个人卖家用的本地运营插件。源码审查没有发现安装期自动脚本；默认路径不出网，出网的地方都要先配好用户自己的令牌。版本不在范围内：它要求 dsh `^0.2.1-rc.5`，按 semver 默认规则，我们本机的 0.2.2-rc.1 不满足，所以**没装进 dsh，也没做官方最小验收**。它自带的 554 个测试在断网环境里全部通过（n=1）。补货和利润计算器喂了我们自己写的 4 组假数据，结果和手算一致（n=1/组）。手算是照插件源码里的规则写的（例如失销算到到货前一天、安全量=安全天数×日销），所以这只说明代码按它自己写的规则在算，不能说明这套补货和利润规则对真实生意合理。

- 仓库：[gx18391303625-afk/xander-zaozao-xiaban](https://github.com/gx18391303625-afk/xander-zaozao-xiaban)，固定在 commit [`2992a49c`](https://github.com/gx18391303625-afk/xander-zaozao-xiaban/commit/2992a49c036411f6c73d91bd15cf38d58e7ca604)（v2.9.0）。2026-11-09 18:31 EST 查询时有 3 星、1 fork（见 [repo-meta.txt](evidence/06-xander/repo-meta.txt)）。没有找到别人实际使用的记录。
- 作者 README 自己写着：「DSH 适配已覆盖本地加载、只读配置查询和合成计算验收，**仍未完成真店读写验证**」（README L172）。我们也**没测真店读写**：没有接入任何店铺、令牌或广告账户。

## 1. 先审源码（详见 [source-review.txt](evidence/06-xander/source-review.txt)）
- `package.json` 里没有 preinstall、install、postinstall、prepare 这类脚本，也没有任何 npm 依赖，数据库用的是 Node 自带的 `node:sqlite`。
- 所有出网都走 `lib/http.js` L27 的 fetch。调用它的地方会先检查凭证，没有凭证就直接报错，不会发请求。具体位置：
  - 卖家接口：`lib/spapi.js` L17–19
  - 广告接口：`lib/ads.js` L23–26
  - 换令牌：`lib/lwa.js` L8
  - S3 云备份：`lib/sync.js` L66–72，没开云备份就报错
  - 紫鸟：只连本机 127.0.0.1，见 `lib/ziniao.js` L13–16
- `xander_status` 只有在 `check=true` 时才联网测令牌（`server/tools.js` L76）。
- 所有写入都要先打开对应开关，关着的开关在执行前就会被拒绝（`lib/proposals.js` L281）。实测新数据目录里 31 个开关全是关的（[run-count-switches.txt](evidence/06-xander/run-count-switches.txt)）。
- 子进程只用在两处：调用系统密钥工具存取它自己的凭证，以及面板打开浏览器。面板只监听 127.0.0.1。
- 结论：**默认路径不出网，可以继续做离线部分。**

## 2. 版本：不在范围内
- 用本机 npm 自带的 semver 7.8.5 实际计算，在断网环境里跑（[semver-result.txt](evidence/06-xander/semver-result.txt)，n=1）：
  - `satisfies('0.2.2-rc.1', '^0.2.1-rc.5')` 结果是 **false**。原因是 semver 默认只允许同一个 0.2.1 版本的预发布号；0.2.2 的预发布版不算在范围内。
  - 加上 `includePrerelease: true` 才是 true。这个开关不是 npm 的默认行为，我们不拿它来当兼容。
- 所以按 Kumo 的要求：**版本不在范围内，没装进 dsh，没做官方最小验收**（docs/dsh.md 第 3 节）。我们也没有用 --force 强装，没有改它的 package.json。

## 3. 包外直接调用（补充，不是官方验收）
docs/dsh.md 第 3 节要求的是在 dsh 里调这两个工具，我们没做。下面是在 dsh 外用 node 直接调插件自带的工具函数：用全新的空数据目录，不接入任何店铺，断网（[run-offline-handlers.txt](evidence/06-xander/run-offline-handlers.txt)，n=1，exit 0，0.075s）。
- `xander_status` 传 `{"check":false}`：返回版本 2.9.0，没有接入的店铺，没有打开的开关；凭证存储显示“本地文件（权限 600，未加密）”，因为本机没有 secret-tool；云备份未开启。这个数据目录先后跑过计算器和这两个工具，结束后里面只有 4 个空子目录（reports、proposals、exports、backups），没有生成配置文件或数据库（[data-dir-after.txt](evidence/06-xander/data-dir-after.txt)）。
- `xander_switches` 传 `{}`：31 个开关，打开的 0 个。
- 技能：`skills/` 下有 7 个 SKILL.md，和文档列的 7 个技能同名。**这只是静态读取文件，不等于 dsh 能发现这些技能**，dsh 里的技能发现没测。

## 4. npm test（离线）
- 第 1 次：在 `unshare -rn` 里直接跑 `npm test`，跑了约 6.8 分钟后我手动停掉了。新网络命名空间里的回环口默认是关的，测试自带的本地假亚马逊服务连不上 127.0.0.1，大量用例超时。这次不作结论（[run-npm-test-attempt1-lo-down.txt](evidence/06-xander/run-npm-test-attempt1-lo-down.txt)）。
- 第 2 次：在 `unshare -rn` 里先打开回环口再跑（仍然没有外网），**554/554 通过**，exit 0，3.694 秒（[run-npm-test.txt](evidence/06-xander/run-npm-test.txt)，n=1）。
- 注意：测试里的 `test/dsh.test.js` 用的是模拟的 dsh 宿主，不等于真装进 dsh 跑过。

## 5. 计算器核对（假数据，手算在运行前写好并存了哈希）
输入见 [fake-input.json](evidence/06-xander/fake-input.json)，手算见 [hand-calc.md](evidence/06-xander/hand-calc.md)，哈希见 [pre-run-sha256.txt](evidence/06-xander/pre-run-sha256.txt)，输出见 [run-offline-calc.txt](evidence/06-xander/run-offline-calc.txt)（exit 0，n=1/组）。

| 组 | 手算 | 计算器 | 一致 |
|---|---|---|---|
| 补货 FAKE-A（日销 10、可售 200、30 天后到货、覆盖 30 天、安全 7 天、每箱 24） | 第 21 天断货；到货前失销 90；需要 370 件 → 16 箱共 384 件；采购 1344；有“早于到货断货”提醒 | 相同 | 是 |
| 补货 FAKE-B（日销 8、可售 100、第 10 天到 120、20 天后到货、MOQ 300、每箱 50） | 第 28 天断货；需要 252 件 → 6 箱共 300 件；采购 600；没有提醒 | 相同 | 是 |
| 利润 1（收入 1000，各项扣减齐全） | 280.00，状态 COMPLETE_INPUTS | 280，状态 COMPLETE_INPUTS | 是 |
| 利润 2（缺退款，仓储费未知，含估算项） | 已知小计 177.50，不给利润 | 177.5，经营利润 null，状态 KNOWN_SUBTOTAL_ONLY，缺“退款”，未知“仓储费” | 是 |

利润计算器在缺核心项时只给“已知收支小计”，不叫利润，这一点和源码 profitBridge（lib/calc.js L277–313）的口径一致。

注意：上面的手算是照插件源码里的规则写的（例如失销算到到货前一天、安全量=安全天数×日销）。“一致”只证明代码按它自己源码写的规则在算，不证明这套补货和利润规则对真实生意合理。

## 没测的
- 没装进 dsh，没做 dsh 里的最小只读验收，也没测 dsh 能不能发现技能（版本不在范围内）。
- 没测真店读写，没接任何令牌，没跑 `xander setup`、`xander doctor`、`check=true`、面板、紫鸟、S3 备份。
- 没测广告经济计算器（`adEconomics`）和各技能里的 Python 脚本。
- 全程没有启动 dsh，也没有接任何模型，所以没有模型请求，没碰 DeepSeek 官方地址。
