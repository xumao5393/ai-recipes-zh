I've built the review queue for the merchant from the 5 orders in the export, but it is **not saved anywhere**. This task allowed no tools, so the table below is the output. Nothing was refunded, cancelled, discounted, changed in inventory, or sent to a customer.

Age is counted from when the order was placed (`created_at`) to the export's reference time, 2026-11-09 23:00 UTC (6:00 PM EST). A row marked incomplete means the evidence is missing, not that the order is fine.

**Order exception queue (pending merchant review)**

| Order | Customer | Exception | Evidence | Age | Proposed next step | Approval needed |
|---|---|---|---|---|---|---|
| #FAKE-1002 | Sam Patel | Address problem | `address_verification: "failed"`; `address1: "??? Apt"`; `city` and `zip` are empty; unfulfilled and paid; must ship by 2026-11-11 23:59:59 UTC | 1d 11h | Hold fulfillment. The merchant reviews the address and decides whether to ask the customer for a corrected one. | Yes. Any customer contact or address edit needs the merchant. |
| #FAKE-1003 | Riley Chen | Backorder | Partially fulfilled. SKU-3381 shipped 2026-11-08 (tracking 1Z84A0003). SKU-7720 Water Bottle (qty 2) is `backordered`, with fulfillable_quantity 2 still unshipped. Must ship by 2026-11-12 23:59:59 UTC, so it isn't late yet. | 2d 14h | The merchant confirms when SKU-7720 will be restocked, then decides whether to wait or take another action. | Yes. Any customer notice, cancellation, refund or inventory change needs the merchant. |
| #FAKE-1004 | Morgan Diaz | Late shipment | Unfulfilled with no fulfillments, though the item is in stock. Must-ship date was 2026-11-05 23:59:59 UTC, so it is about 3d 23h overdue. Address confirmed; paid. | 8d 15h | The merchant finds out why the order didn't ship and fulfills it if nothing is blocking. Make it the top priority. | Yes. Any customer contact, discount or refund for the delay needs the merchant. |
| #FAKE-1005 | Taylor Kim | **INCOMPLETE**: status can't be determined | `fulfillment_status`, `fulfillments`, `promised_ship_by`, `fulfillable_quantity` and `inventory_status` are all null. The address is confirmed, so it isn't an address problem. Without the other fields there's no way to tell whether it is backordered or late. | 1d 3h | Don't guess. The merchant checks the order in admin (https://example.invalid/admin/orders/9005) or re-exports with these fields filled in. | Yes. Merchant review is needed before any classification. |

**Left out of the queue:**
- **#FAKE-1001 (Jordan Lee):** no exception. It was fulfilled on 2026-11-06 09:30 UTC, before the must-ship date of 2026-11-07, with tracking 1Z84A0001. The address is confirmed and the item was in stock.

**Order of attention:** #FAKE-1004 first (overdue), then #FAKE-1002 (address must be fixed before 11-11), then #FAKE-1003 (backorder, due 11-12), then #FAKE-1005 (needs its data checked).

I've stopped here as the instruction says. If the queue should be kept, it still needs to be saved somewhere the merchant can find it.