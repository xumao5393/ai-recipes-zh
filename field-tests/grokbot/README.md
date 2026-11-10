# Grok Bot 用法实测笔记（2026-11 四天连续实测）

记录 Grok Bot 各种用法的实际测试过程。只写真测过的内容，没测的会注明“未测”，证据放在 `evidence/`。

| # | 篇目 | 状态 |
|---|---|---|
| 1 | [webhook 触发 routine 实测过程记录](webhook-routine-过程记录.md) | 进行中，未触发 |
| 2 | 让 bot 写脚本调 API，代替抓网页 | 未完成，暂未入库 |
| 3 | 只读查用量：谁在吃额度 | 未完成，暂未入库 |
| 4 | [Gmail/Drive 连接器能做什么：只读边界实测](Gmail和Drive连接器能做什么-只读边界实测.md) | 实测（n=1，仅只读），已过审 |
| 5 | [Cloudflare Worker 网关去重：本地复现](Cloudflare-Worker网关去重-本地复现.md) | 本地复现，已过审 |
| 6 | 连接器体检：已连接不等于能用 | 未完成，暂未入库 |
| 7 | 定时例程准不准：启动延迟实测 | 未完成，暂未入库 |
| 8 | 网页读取：WebFetch 和 curl 怎么选 | 未完成，暂未入库 |
| 9 | WebFetch 会不会给旧内容：缓存实测 | 未完成，暂未入库 |

第 1 篇是**进行中的过程记录，webhook 未测通**，只是过程记录，不能当成“webhook 已测过”或“webhook 可用”的结论。暂未入库的篇目不挂链接、不下结论。实际触发和延迟都还没测。

---

本文以 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh-hans) 协议发布。
