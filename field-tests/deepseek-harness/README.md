# DeepSeek harness 实测笔记（2026-11 四天连续实测）

把 DeepSeek 模型当智能体用，目前有两类搭法：
- 官方外壳 [deepseek-ai/deepseek-harness](https://github.com/deepseek-ai/deepseek-harness)（命令 `dsh`）；
- 把 DeepSeek 模型接进 Claude Code、OpenCode、Cline、Aider、Roo Code 等现成外壳。

只记录真测过的东西。每篇注明“实测 / 官方说法 / 他人转述 / 推测”，证据放在 `evidence/`。

| # | 篇目 | 状态 |
|---|---|---|
| 01 | [官方 dsh 安装与无密钥时的行为](01-dsh-安装与无密钥行为.md) | 实测，已过审 |
| 02 | dsh 每次调用模型到底发了什么 | 未完成，暂未入库 |
| 03 | 用本地回放服务测工具循环 | 未完成，暂未入库 |
| 04 | [dsh web 能否起来](04-dsh-web能否起来.md) | 实测，已过审 |
| 05 | Claude Code 接 DeepSeek 风格端点抓包 | 未完成，暂未入库 |
| 06 | [OpenCode 接 DeepSeek 风格端点抓包](06-OpenCode接DeepSeek风格端点抓包.md) | 实测（本地抓包），已过审 |
| 07 | Aider 接 DeepSeek 风格端点抓包 | 未完成，暂未入库 |
| 08 | Cline CLI 接 DeepSeek 风格端点抓包 | 未完成，暂未入库 |
| 09 | dsh 遇到思考死循环会怎样（社区说法核对 + 本地回放复现） | 未完成，暂未入库 |
| 09c | 社区思考循环守卫插件强装到 0.2.2 实测 | 未完成，暂未入库 |
| 09b | 「dsh 比 OpenCode 高 1.6 分」核对 | 未完成，暂未入库 |
| 10 | 各外壳固定请求开销对比（草稿） | 未完成，暂未入库 |
| 11 | [SDR 插件：状态机与审批哈希](11-SDR插件状态机与审批-本地假模型实测.md) | 库级离线实测 + 本地假模型实测，已过审 |
| 12 | dsh 多步任务每轮重发多少 | 未完成，暂未入库 |
| 12b | dsh 截断后的完整输出能不能读回来 | 未完成，暂未入库 |
| 12c | OpenCode 多步对照 | 未完成，暂未入库 |
| 12d | Claude Code 多步对照 | 未完成，暂未入库 |

测试环境：Linux、Node v24.22.1。没有 DeepSeek API key，凡是需要真实模型回答的项目都还没测。

暂未入库的篇目不挂链接、不下结论；过审一篇补一篇。

---

本文以 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh-hans) 协议发布。
