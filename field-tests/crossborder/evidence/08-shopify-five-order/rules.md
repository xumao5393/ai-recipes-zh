# 判定规则（文章方法的可执行化）· 2026-11-09 18:35 EST

来源文章：https://whiskerbeacon.com/guides/shopify-automation-with-grok-bot/
标签：方法来自网站文章，没有他人实测数据
说明：文章只给了类别与验收法，没有给出字段级判定。下面是我们为了能离线跑通而写下的本地约定，不是 Shopify 官方规则，也不是他人实测结论。

## 输入
- 本地 JSON 订单列表（本目录 fake-orders.json）
- 参考时间：文件 meta.reference_time_utc

## 异常类别（按文章：地址问题 / 欠货 / 超期发货；另加 incomplete）

按优先级检查（一单只出一行；优先级高的先）：
1. **incomplete**：下列任一为 null/缺失：`fulfillment_status`、`fulfillments`、`promised_ship_by`，或任一 line_item 的 `inventory_status` / `fulfillable_quantity` 为 null。→ 标 incomplete，evidence 只列缺失字段路径，不猜类别。
2. **address_problem**：`shipping_address.address_verification == "failed"`，或 `city`/`zip`/`address1` 为空字符串。
3. **backorder**：存在 line_item 满足 `inventory_status == "backordered"` 且 `fulfillable_quantity > 0`。
4. **late_shipment**：`fulfillment_status` 属于 `unfulfilled` 或 `partial`，且 `promised_ship_by < reference_time`，且不存在 status=success 且覆盖全部数量的履约（本约定：unfulfilled 且无 success fulfillment；或 partial 且仍有 fulfillable_quantity>0 的非 backordered 行——本次样例用 unfulfilled+无 fulfillment）。

若以上都不命中 → **不出表**（正常单）。

## 输出行字段（对齐文章表）
- order: name + admin_url
- customer: display_name
- exception: 上列之一，或 incomplete
- evidence: 触发用到的字段路径与原值（incomplete 只列路径，不填猜值）
- age: 参考时间 − 异常起点（address/backorder 用 updated_at；late 用 promised_ship_by；incomplete 用 updated_at）；单位小时，向下取整
- proposed_next_step: 仅内部动作建议文案，不自动执行
- approval_needed: 固定列出可能涉及的人批动作类别（refund/cancellation/discount/inventory_edit/customer_message 中与建议相关的），脚本永不调用它们

## 禁止
- 不调用任何网络 / Shopify API
- 不编造缺失字段的值
- 不对订单执行写操作
