# DeepSeek harness 实测笔记（2026-11 四天连续实测）

把 DeepSeek 模型当智能体用，目前有两类搭法：
- 官方外壳 [deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness)（命令 `dsh`）；
- 把 DeepSeek 模型接进 Claude Code、OpenCode、Cline、Aider、Roo Code 等现成外壳。

只记录真测过的东西。每篇注明“实测 / 官方说法 / 他人转述 / 推测”，证据放在 `evidence/`。

| # | 篇目 | 状态 |
|---|---|---|
| 01 | [官方 dsh 安装与无密钥时的行为](01-dsh-安装与无密钥行为.md) | 实测，已过审 |
| 02 | [dsh 每次调用模型到底发了什么](02-dsh-每次请求到底发了什么.md) | 实测（本地抓包，n=1），已过审 |
| 03 | [用本地回放服务测工具循环](03-dsh-本地回放跑通工具循环.md) | 实测（本地 SSE 回放），已过审 |
| 03b | [dsh 的 bash 写文件到底落在哪](03b-dsh的bash写文件到底落在哪.md) | 实测（本地回放），已过审 |
| 04 | [dsh web 能否起来](04-dsh-web能否起来.md) | 实测，已过审 |
| 05 | [Claude Code 接 DeepSeek 风格端点抓包](05-Claude-Code接DeepSeek风格端点抓包.md) | 实测（本地抓包），已过审 |
| 06 | [OpenCode 接 DeepSeek 风格端点抓包](06-OpenCode接DeepSeek风格端点抓包.md) | 实测（本地抓包），已过审 |
| 07 | [Aider 接 DeepSeek 风格端点抓包](07-Aider接DeepSeek风格端点抓包.md) | 实测（本地抓包），已过审 |
| 08 | [Cline CLI 接 DeepSeek 风格端点抓包](08-Cline-CLI接DeepSeek风格端点抓包.md) | 实测（本地抓包），已过审 |
| 09 | dsh 遇到思考死循环会怎样（社区说法核对 + 本地回放） | 未完成，暂未入库 |
| 09c | 社区思考循环守卫插件强装到 0.2.2 | 未完成，暂未入库 |
| 09b | 「dsh 比 OpenCode 高 1.6 分」核对 | 未完成，暂未入库 |
| 10 | [各外壳固定请求开销对比（草稿）](10-各外壳固定请求开销对比-草稿.md) | 草稿，已过审（仍为草稿） |
| 11 | [SDR 插件：状态机与审批哈希](11-SDR插件状态机与审批-本地假模型实测.md) | 库级离线实测 + 本地假模型实测，已过审 |
| 12 | dsh 多步任务每轮重发多少 | 未完成，暂未入库 |
| 12b | dsh 截断后的完整输出能不能读回来 | 未完成，暂未入库 |
| 12c | OpenCode 多步任务对照 | 未完成，暂未入库 |
| 12d | Claude Code 多步任务对照 | 未完成，暂未入库 |
| 12e | [OpenCode 什么时候自动压缩：回报 89.1 万 token 才压，压缩后原话不留；usage 报高时反复压缩：120 秒内 3,053 次（n=1，超时终止）](12e-OpenCode什么时候自动压缩上下文-本地回放实测.md) | 实测（本地回放，n=1），已过审 |
| 12f | [dsh 什么时候自动压缩：727,040 token 一个不差；先把工具输出剪成头尾，再压掉用户原话；usage 偏高每步多 2 次摘要](12f-dsh什么时候自动压缩上下文-本地回放实测.md) | 实测（本地回放，边界 n=1），已过审 |
| 12g | [Claude Code 接 DeepSeek 时约 16.7 万就压缩（当成 20 万窗口）；只有 CLAUDE_CODE_MAX_CONTEXT_TOKENS 能调大；加 [1m] 后到 200 万都不压；usage 偏高压 3 次就停](12g-Claude-Code什么时候自动压缩上下文-接DeepSeek时的窗口误判.md) | 实测（本地回放，边界 n=1），已过审 |
| 12h | OpenCode 手动设小 limit.context 以后的压缩 | 未完成，暂未入库 |
| 12i | Aider 接 DeepSeek 的聊天记录摘要 | 未完成，暂未入库 |
| 12j | Claude Code 交互模式接 DeepSeek | 未完成，暂未入库 |
| 12k | Claude Code 自动模式接 DeepSeek 的安全检查请求 | 未完成，暂未入库 |
| 12l | Claude Code 的 /context 与 /compact 接 DeepSeek | 未完成，暂未入库 |
| 12n | Claude Code /context 里的 System tools 怎么算 | 未完成，暂未入库 |
| 12m | 真 DeepSeek 端点：count_tokens 与思考模式 | 未完成，暂未入库 |

测试环境：Linux、Node v24.22.1。没有 DeepSeek API key，凡是需要真实模型回答的项目都还没测。

暂未入库的篇目不挂链接、不下结论。

---

本文以 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh-hans) 协议发布。
