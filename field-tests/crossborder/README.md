# 跨境电商自动化实测笔记（2026-11 四天连续实测）

记录能在本地跑起来的跨境店铺自动化工具：装没装上、卡在哪、有没有证据。

只记录真测过的东西。每篇注明“实测 / 官方说法 / 他人转述 / 推测”，证据放在 `evidence/`。

| # | 篇目 | 状态 |
|---|---|---|
| 01 | [vibe-seller 安装到登录前](01-vibe-seller-安装到登录前.md) | 实测，已过审 |
| 05 | [dsh-trade-assistant 询盘规则插件对照](05-dsh-trade-assistant-询盘规则插件对照.md) | 实测（22 封，n=1），已过审 |
| 06 | [Xander 亚马逊运营插件：离线审查与计算器核对](06-Xander亚马逊运营插件-离线审查与计算器核对.md) | 源码审查 + 离线实测（未装进 dsh，n=1），已过审 |
| 08 | [Shopify 五单验收法：Grok Bot 离线判本地假订单](08-Shopify五单验收法-本地假订单异常清单.md) | 实测（本地假订单，n=3，冻结脚本正式分 1/3），已过审 |
| 09 | [外贸工作台 DSH 插件：离线审查与装柜计算核对](09-外贸工作台DSH插件-离线审查与装柜计算核对.md) | 源码审查 + 离线实测（n=1/组），已过审 |
| 10 | [Project Tango：本地假店铺 MCP，离线测试与最小读取](10-Project-Tango假店铺MCP-离线测试与最小读取.md) | 离线实测（n=1），已过审 |
| 13 | [Listing Guard：本地自托管上架前合规检查](13-Listing-Guard本地自托管上架前合规检查.md) | 本机实测（未用 Docker，假 listing 各 n=1，只测跑没跑通、不评准确度），已过审 |
| 15 | [mcp-store-tools：只读 Shopify 目录审计 MCP，离线实测](15-mcp-store-tools-只读Shopify目录审计MCP离线实测.md) | 离线实测（自带假 Storefront，n=1；mock.shop 条款读不到，没连），已过审 |

测试环境：Linux。没有模型 Key，不注册、不登录任何店铺或紫鸟账号。

复审通过后，篇目才会加上链接。

---

本文以 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.zh-hans) 协议发布。
