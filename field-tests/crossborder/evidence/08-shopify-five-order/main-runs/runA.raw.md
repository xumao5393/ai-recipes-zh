# Order exception queue for merchant review, as of Nov 9, 2026, 6:00 PM EST

Three orders need attention and one is marked incomplete. All times below are EST, converted from the UTC timestamps in the export. Age is counted from when the order was created.

| Order | Customer | Exception | Evidence | Age | Proposed next step | Approval needed |
|---|---|---|---|---|---|---|
| #FAKE-1004 | Morgan Diaz | Late shipment | Status is `unfulfilled` and there are no fulfillments. It was due to ship by Nov 5, 6:59 PM EST and is now about 4 days overdue. The Phone Stand (SKU-5162) is `in_stock`, with 1 left to fulfill. The address is confirmed. | about 8 days 15 hours (placed Nov 1, 3:00 AM EST) | Merchant checks why it hasn't shipped and fulfills it if nothing is blocking it. Merchant decides whether to tell the customer about the delay. | Yes: to fulfill it and to contact the customer. |
| #FAKE-1002 | Sam Patel | Address problem | Address check is `failed`. Street line reads "??? Apt", and city and ZIP are blank. Only state (CA) and country (US) are filled in. Status is `unfulfilled`; ship-by is Nov 11, 6:59 PM EST, so it is not late yet. The Desk Lamp is `in_stock`. | about 1 day 11 hours (placed Nov 8, 7:00 AM EST) | Merchant holds fulfillment and gets a corrected address before Nov 11. | Yes: to contact the customer and to edit the address. |
| #FAKE-1003 | Riley Chen | Backorder (partly shipped) | Status is `partial`. The Notebook Set (SKU-3381) shipped Nov 8, 10:00 AM EST, tracking 1Z84A0003. The Water Bottle (SKU-7720) is `backordered`, with 2 still to fulfill. Ship-by is Nov 12, 6:59 PM EST, so it is not late yet. | about 2 days 14 hours (placed Nov 7, 4:00 AM EST) | Merchant confirms when SKU-7720 will be back in stock. Merchant then decides whether to wait, split the shipment or tell the customer. | Yes: to contact the customer, and for any cancellation, refund or inventory change. |
| #FAKE-1005 | Taylor Kim | **INCOMPLETE**: can't tell from the data | Fulfillment status, fulfillments, ship-by date, fulfillable quantity and inventory status (Wall Clock, SKU-6045) are all missing. Payment is `paid` and the address is confirmed. I can't tell whether this is a backorder or a late shipment, so I haven't guessed. | about 1 day 3 hours (placed Nov 8, 3:00 PM EST) | Merchant pulls the missing fulfillment and inventory details from the store admin, then sorts the order into the right category. | Merchant review is needed before anything else happens. |

#FAKE-1001 (Jordan Lee) is left off the queue. It shipped Nov 6, 4:30 AM EST, before its Nov 7 ship-by date (tracking 1Z84A0001). Its address is confirmed and the item is in stock.

I didn't refund, cancel, discount, change inventory or contact any customer. Every next step above is only a suggestion for you to decide on.

The queue hasn't been saved yet because I was told not to use any tools. It needs to be saved for merchant review, and that is where this task ends.