# Order exception queue for merchant review

**As of:** 2026-11-09 23:00 UTC (6:00 PM EST)
**Scope:** I checked 5 orders from the local JSON export. This is a report only. Nothing was refunded, cancelled, discounted or changed in inventory, and no customer was contacted.

| Order | Customer | Exception | Evidence | Age | Proposed next step | Approval needed |
|---|---|---|---|---|---|---|
| #FAKE-1004 | Morgan Diaz | **Late shipment** | `fulfillment_status: unfulfilled`; `fulfillments: []`; `promised_ship_by: 2026-11-05T23:59:59Z`, so it is about 3d 23h overdue. Item SKU-5162 is `in_stock`, `fulfillable_quantity: 1`. Address is `confirmed`. | 8d 15h (created 2026-11-01 08:00 UTC) | Merchant checks why an in-stock order with a confirmed address hasn't shipped, then fulfills it first. Merchant decides whether to tell the customer about the delay. | Yes. Any customer message, shipping upgrade or compensation needs merchant approval. |
| #FAKE-1003 | Riley Chen | **Backorder (partial shipment)** | `fulfillment_status: partial`. SKU-3381 shipped 2026-11-08 (tracking 1Z84A0003). SKU-7720 Water Bottle ×2 is `backordered` with `fulfillable_quantity: 2` and isn't in any fulfillment. `promised_ship_by: 2026-11-12T23:59:59Z`, so it isn't late yet. | 2d 14h (created 2026-11-07 09:00 UTC) | Merchant confirms the restock date for SKU-7720. If it lands after Nov 12, merchant chooses: wait, substitute, or partial refund or cancel. | Yes. Any refund, cancellation, substitution or customer message needs merchant approval. |
| #FAKE-1002 | Sam Patel | **Address problem** | `address_verification: failed`; `address1: "??? Apt"`; `city: ""`; `zip: ""` (province CA, country US). `fulfillment_status: unfulfilled`; SKU-2093 is `in_stock`. `promised_ship_by: 2026-11-11T23:59:59Z`. | 1d 11h (created 2026-11-08 12:00 UTC) | Hold fulfillment. Merchant gets a corrected address from the customer before Nov 11 so the order doesn't also become late. | Yes. Contacting the customer and editing the address need merchant approval. |
| #FAKE-1005 | Taylor Kim | **INCOMPLETE: can't classify** | `fulfillment_status: null`; `fulfillments: null`; `promised_ship_by: null`; SKU-6045 has `fulfillable_quantity: null` and `inventory_status: null`. Address is `confirmed` and the order is `paid`. | 1d 3h (created 2026-11-08 20:00 UTC) | No exception assigned, since there isn't enough data to judge. Merchant checks this order's fulfillment, stock and ship-by date in admin (https://example.invalid/admin/orders/9005). | Yes, for merchant review. No action proposed until the missing data is filled in. |

**Not queued:** #FAKE-1001 (Jordan Lee). It shipped 2026-11-06 09:30 UTC (tracking 1Z84A0001), before its ship-by date of 2026-11-07. The address is confirmed and it's in stock, so there's no exception.

**Sorted by:** Late first, then backorder, then address, then incomplete.

**Status:** I didn't write this queue to a file, because this task allowed no tool use. The table above is the queue for merchant review. I'm stopping here and won't take any further action.