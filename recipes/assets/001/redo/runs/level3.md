# Level 3：Agent + 上网工具 + Skill

执行方式：同一当前大型语言模型代理，手动阅读并遵循 `skill/compare-subscriptions/SKILL.md`。没有另开独立会话；没有测试自动安装或加载 Skill。按检查单再读三个价格页，补查 OpenAI 官方帮助页和公告。

下表是公开英文美元页在本次抓取中能支持的记录，不是登录后的当地报价。未购买任何付费档。

| 产品 | 档位 | 美元月付及年付说明 | 比免费版多什么（一句话） | 官方价格原文与出处 |
|---|---|---|---|---|
| ChatGPT | Go | **11月现价本次未获取**；1月官方公告曾为美国 $8/月 | 更多工具、图像和文件用量。 | “In the US, Go is available for $8 per month.” [1月公告](https://openai.com/index/introducing-chatgpt-go/)；[当前帮助页](https://help.openai.com/en/articles/11989085-what-is-chatgpt-go)未列金额。旧公告不能单独核定11月价。 |
| ChatGPT | Plus | $20/月；无年付 | 更高模型限额及推理、文件和研究功能。 | “Price: $20/month (billed monthly).” [官方帮助](https://help.openai.com/en/articles/6950777-what-is-chatgpt-plus) |
| ChatGPT | Pro 100 | $100/月；无年付 | Pro 模型和更高工具用量。 | “Pro 100 | $100 | Not included” [官方 Pro 表](https://help.openai.com/en/articles/9793128-about-chatgpt-pro-tiers)，表头为 Monthly price (USD)。 |
| ChatGPT | Pro 200 | $200/月；无年付 | Pro 系列功能，用量高于 Pro 100。 | “Pro 200 | $200 | Not included” [同一官方表](https://help.openai.com/en/articles/9793128-about-chatgpt-pro-tiers) |
| ChatGPT | Pro 500 | $500/月；无年付 | Pro 系列最高用量，含 Ultrafast。 | “Pro 500 | $500 | Included” [同一官方表](https://help.openai.com/en/articles/9793128-about-chatgpt-pro-tiers) |
| Claude | Pro | $20/月；也可 $200/年预付，官网显示约 $17/月 | 更多用量、更多模型与 Claude Code。 | “Per month with annual subscription discount ($200 billed up front). $20 if billed monthly.” [定价页](https://www.anthropic.com/pricing) |
| Claude | Max | $100/月；月付 | Pro 的 5 倍用量。 | “Max” / “$100” / “5x Pro usage every 5 hours and every week*”；FAQ：“Both plans are billed monthly.” [定价页](https://www.anthropic.com/pricing) |
| Claude | Ultra | $200/月；月付 | Pro 的 10 倍每周用量，已验证账户无 5 小时限制。 | “Ultra” / “$200” / “10x Pro usage every week*”；“No 5-hour limit for verified accounts.” [定价页](https://www.anthropic.com/pricing) |
| Gemini | Google AI Plus | $4.99/月；本次未取得年付信息 | 更高 AI 用量及云存储。 | “Google AI Plus $4.99/mo” [定价表](https://one.google.com/about/google-ai-plans/) |
| Gemini | Google AI Pro | $19.99/月；也可 $199.99/年，月均约 $16.67（计算值） | 扩展 Gemini 用量及 5 TB 存储。 | “Monthly ($19.99)” / “Annual ($199.99)”；“Google AI Pro $19.99/mo” [定价页](https://one.google.com/about/google-ai-plans/) |
| Gemini | Google AI Ultra 5x | $99.99/月；本次未取得年付信息 | Pro 的 5 倍 Gemini 用量及 20 TB 存储。 | “Google AI Ultra 5x $99.99/mo” [定价表](https://one.google.com/about/google-ai-plans/) |
| Gemini | Google AI Ultra 20x | $199.99/月；本次未取得年付信息 | Pro 的 20 倍 Gemini 用量及 30 TB 存储。 | “Google AI Ultra 20x $199.99/mo” [定价表](https://one.google.com/about/google-ai-plans/) |

## 自检
- 覆盖：当前页面可识别的 12 个个人档位/用量子档；未列 API、团队或企业版。
- 周期：Claude 的 $17 是年付显示月均，不是月付。$200/12 约为 $16.67，官网把展示金额取整，不把两者伪称完全相等。
- 出处：11 项当前月费可追溯到本次抓取的官方价格或帮助文字。Go 只有1月公告历史价，**当前月费及其当前价格证据仍缺两格**，不宣称查全。
- 地区与税费：Go 公告明确是美国价、部分市场本地化；其他公开美元页也不能代表所有地区、App Store、账号促销或税后价。Claude 明说金额不含适用税；其余页面未取得完整税费说明，不作统一税前/税后断言。
- 能力：本期只查公开价格和权益说明，没实测这些付费功能，不据此判断哪家“最强”“最值”。
- 查询窗口：2026-11-07T23:59:56.846800-05:00 至 2026-11-08T00:01:16.267709-05:00（均 EST）；WebFetch 可能有缓存，不是用户账户结账核验。
