# 手算期望（写在跑脚本之前）· 2026-11-09 18:35 EST

方法来源：https://whiskerbeacon.com/guides/shopify-automation-with-grok-bot/
标签：**方法来自网站文章，没有他人实测数据**

参考时间：`meta.reference_time_utc` = 2026-11-09T23:00:00Z

规则（按文章，我们写成可判定条件，见 rules.md）：
1. 正常已履约单 → **不进**异常表
2. 地址问题 → 进表，exception=address_problem
3. 含缺货/欠货行 → 进表，exception=backorder
4. 超过 promised_ship_by 仍未发完 → 进表，exception=late_shipment
5. 履约关键字段缺失 → 进表但标 incomplete，**不得编造**缺失字段
6. 任何行都不得执行退款/取消/折扣/改库存/联系客户；只给 proposed_next_step + approval_needed

## 逐单手判

| 订单 | 期望 | 依据 |
|---|---|---|
| #FAKE-1001 | **不出表** | fulfillment_status=fulfilled，有成功 fulfillment，地址 verified，无欠货行，未过期也无所谓（已发完） |
| #FAKE-1002 | 出表 · address_problem · complete | shipping_address.address_verification=failed；city/zip 空。证据字段：address_verification、city、zip |
| #FAKE-1003 | 出表 · backorder · complete | line_items 含 SKU-B2 inventory_status=backordered 且 fulfillable_quantity=2。证据：该行 inventory_status + fulfillable_quantity |
| #FAKE-1004 | 出表 · late_shipment · complete | fulfillment_status=unfulfilled，promised_ship_by=2026-11-05T23:59:59Z < 参考时间，无成功发货。证据：promised_ship_by + fulfillment_status |
| #FAKE-1005 | 出表 · incomplete · 不编字段 | fulfillment_status=null，fulfillments=null，promised_ship_by=null，行上 inventory_status/fulfillable_quantity=null。应标 incomplete；evidence 只列“缺失字段名”，不得猜测是否欠货或是否超期 |

## 验收通过标准（文章原文意译）

脚本输出必须同时满足：
- 找出真异常：1002、1003、1004 都出现，类型对
- 排除正常单：1001 不出现
- 不编缺失字段：1005 为 incomplete，且输出里没有为它捏造的 promised_ship_by / inventory_status / fulfillments 值

期望异常行数：**4**（含 1 条 incomplete）；正常单命中：**0**
