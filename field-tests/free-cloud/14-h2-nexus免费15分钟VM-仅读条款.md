# [h2.nexus](https://h2.nexus/) 免费 15 分钟浏览器 VM — 仅读条款

> 状态：**不开**。本轮只读条款，**未打开任何 VM**，也未抓取免费机入口 `/cli`。  
> 时间：2026-11-09（America/New_York）  
> 证据：`evidence/14-h2-nexus/`  
> 优先级：Kumo 标低优先级。

## 读到的页面
| 页面 | URL | HTTP |
|---|---|---|
| 首页 | https://h2.nexus/ | 200 |
| Terms of Service | https://h2.nexus/terms-of-use/ | 200 |
| Privacy Policy | https://h2.nexus/privacy-policy/ | 200 |
| 独立 AUP URL | `/aup` 等 | 404（AUP 在 Terms §8） |

HTML 原件：`internal-archive/14-h2-nexus/pages/`（与抓取时 sandbox 副本逐字节相同；校验见 `evidence/14-h2-nexus/SHA256SUMS.txt`）。

## 判定（详见 TERMS-DECISION.txt）
按 **Kumo**：条款读全，且登录/邮箱/禁止匿名/禁止自动化等条件**无一适用、也无不清之处**才可开；**任一条款不清则不开**；条款读不到当不允许；**产品页文案不能当动手依据**。

**不开**，因为至少以下不清（依据是上条规矩，不是把营销页当成反证）：
- Terms 3.1「To use **certain** Services, the Client must create an account」——未点名 15 分钟免费机是否属于 certain Services。
- 邮箱：Terms/Privacy 把 email 绑在 account/Client Area；免费流程是否要邮箱未写清。
- 匿名：Terms 无明确授权匿名免费机；FAQ「no registration or card」只是产品页说法，不能当动手依据。
- 自动化：AUP 禁规避限额/反滥用，无清晰「允许脚本」绿灯。

范围条款清楚：「…accessing or using the Services…」即视为接受条款。

旁证（准确读法，不作主依据）：Terms 17.3 写营销/网站描述是善意提供的信息，**超出 Terms 与 SLA 的具体保证须书面约定**——也就是不构成额外保证；它本身没有写成「营销描述一律不能算许可」。不开仍只靠 Kumo 的规矩。

产品页 FAQ 原文（不作放行）：「free server for 15 minutes, with no registration or card」。链接指向 `/cli`（本轮未打开）。

## 没做的
- 未打开 `/cli` 或任何 VM / SSH / 浏览器会话。
- 未注册、未填邮箱、未付费。
