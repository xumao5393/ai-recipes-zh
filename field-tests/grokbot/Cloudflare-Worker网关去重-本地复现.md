# Cloudflare Worker 网关去重 · 本地复现

> 来源文章：https://www.woshipm.com/ai/6490752.html（饼干哥哥，2026-11-09）  
> 范围：按 Kumo 安排，**只做本地复现**；无 Cloudflare 账号、不登录、不访问真实 webhook。  
> 证据：`evidence/cf-worker-gateway-local/`  
> 实现说明：文章**没有公开代码**；Worker / 模拟器均为我们自写的最小实现。

## 1. 原文相关说法（作者自报）

摘录存证：`evidence/cf-worker-gateway-local/EXCERPT-woshipm.txt`  
原文 HTML 只存内部存档，不入公开仓库（HTTP 200，sha256 见 SHA256SUMS.txt；摘录见 `EXCERPT-woshipm.txt`）

作者写道（大意）：VPS 每 5 分钟上报给 Cloudflare Worker 过滤去重，真出故障才用 Webhook 叫醒运维 Bot；**每月运行从 8,640 次压到 40 至 60 次**。

- **8640** = 30 天 × 每小时 12 次（每 5 分钟一次）= 单机每月上报次数（算术恒等，非实测）。  
- **40–60**：仅能写作**作者自报**；文章无代码、无复现步骤，本文数字**不是**对作者声明的验证。

## 2. 本地怎么跑

1. 假 webhook 接收器：`127.0.0.1:8788/wake`，只计数写本地 jsonl。  
2. Worker：`npx wrangler dev --local --ip 127.0.0.1 --port 8787`（**未要求登录**，本次成功）。源码：`evidence/.../worker-src/`。  
3. 模拟器：对 `/report` 连发 8640 条假事件；故障按声明的 episode 数注入。

### 叫醒规则（我们自定，须写明）

- 载荷：`{host, status: "ok"|"fault", code?}`  
- **叫醒**：首次 fault；status 在 ok↔fault 之间切换；fault 且 code 变化。  
- **不叫醒**：重复相同 status（含连续 fault 同 code）；首次 ok。  
- 因此：每个隔离的故障 episode ≈ **2 次叫醒**（进入 fault + 恢复 ok）。

## 3. 实测数字（本地，n=1 每次模拟）

| 模拟 | 上报次数 | 注入故障 episode | episode 长度（条） | Worker 报告叫醒 | 本地 wake-log 行数 | 证据 |
|---|---:|---:|---:|---:|---:|---|
| A | 8640 | 50 | 3 | **100** | 100 | sim-result-1host.json；wake-log-sim-a.jsonl |
| B | 8640 | 25 | 2 | **50** | 50 | sim-result-1host-25faults.json；wake-log-sim-b.jsonl |
| C | 8640 | 20 | 3 | **40** | 40 | sim-result-1host-20faults.json；wake-log-sim-c.jsonl（返工重跑，行数仍为 40） |

- 在我们的规则下，叫醒次数 ≈ `2 × episode 数`。作者自报的 40–60，对应大约每月 20–30 次「出故障/恢复」切换——**这是用我们假设反推的说明，不是作者环境的实测**。  
- 若规则改成「只在进入 fault 时叫醒、恢复不叫醒」，同假设下数字会减半。

## 4. 结论口径

- 本地可以用 wrangler `--local` **无登录**跑通「上报 → 去重 → 仅状态变化才叫醒」闭环。  
- **结果完全取决于故障率与叫醒规则假设**；不能用来证明或证伪作者的 8640→40–60。  
- 作者自报 8640→40–60 保持「作者自报」标签；未部署到真实 Cloudflare，未碰真实 Bot webhook。

## 5. 禁止项核对

不注册、不登录 Cloudflare、不付费、不对外发、不把 node_modules 放进 repo。打码说明见同目录 `MASKING.txt`。
