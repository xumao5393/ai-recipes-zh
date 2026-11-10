#!/usr/bin/env python3
"""Offline fulfilment-exception queue from local JSON.
Method label: 方法来自网站文章，没有他人实测数据
Source: https://whiskerbeacon.com/guides/shopify-automation-with-grok-bot/
No network. No Shopify API. No side effects on orders.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def parse_dt(s):
    if s is None:
        return None
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    return datetime.fromisoformat(s)


def missing_paths(order):
    miss = []
    if order.get("fulfillment_status") is None:
        miss.append("fulfillment_status")
    if order.get("fulfillments") is None:
        miss.append("fulfillments")
    if order.get("promised_ship_by") is None:
        miss.append("promised_ship_by")
    for i, li in enumerate(order.get("line_items") or []):
        if li.get("inventory_status") is None:
            miss.append(f"line_items[{i}].inventory_status")
        if li.get("fulfillable_quantity") is None:
            miss.append(f"line_items[{i}].fulfillable_quantity")
    return miss


def age_hours(start, ref):
    if start is None:
        return None
    delta = ref - start
    return int(delta.total_seconds() // 3600)


def address_problem(addr):
    if not addr:
        return True, ["shipping_address"]
    reasons = []
    if addr.get("address_verification") == "failed":
        reasons.append("shipping_address.address_verification=failed")
    for k in ("address1", "city", "zip"):
        v = addr.get(k)
        if v is None or v == "":
            reasons.append(f"shipping_address.{k}=empty")
    return (len(reasons) > 0), reasons


def backorder_evidence(order):
    hits = []
    for i, li in enumerate(order.get("line_items") or []):
        if li.get("inventory_status") == "backordered" and (li.get("fulfillable_quantity") or 0) > 0:
            hits.append(
                f"line_items[{i}].sku={li.get('sku')};inventory_status=backordered;fulfillable_quantity={li.get('fulfillable_quantity')}"
            )
    return hits


def late_shipment(order, ref):
    status = order.get("fulfillment_status")
    if status not in ("unfulfilled", "partial"):
        return False, []
    promised = parse_dt(order.get("promised_ship_by"))
    if promised is None or not (promised < ref):
        return False, []
    fulfillments = order.get("fulfillments") or []
    if status == "unfulfilled":
        success = [f for f in fulfillments if f.get("status") == "success"]
        if success:
            return False, []
        return True, [
            f"fulfillment_status={status}",
            f"promised_ship_by={order.get('promised_ship_by')}",
            "fulfillments:no_success",
        ]
    # partial: still has fulfillable non-fulfilled qty on non-backordered? keep simple:
    # if any success but still unfulfilled remainder via fulfillable_quantity>0 on any item
    still = any((li.get("fulfillable_quantity") or 0) > 0 for li in (order.get("line_items") or []))
    if still:
        return True, [
            f"fulfillment_status={status}",
            f"promised_ship_by={order.get('promised_ship_by')}",
            "line_items:fulfillable_quantity>0_remaining",
        ]
    return False, []


def classify(order, ref):
    miss = missing_paths(order)
    if miss:
        return {
            "exception": "incomplete",
            "evidence": [f"missing:{p}" for p in miss],
            "age_start": order.get("updated_at"),
            "proposed_next_step": "Merchant: supply missing fulfilment fields before classifying; do not guess.",
            "approval_needed": [],
        }

    bad, reasons = address_problem(order.get("shipping_address"))
    if bad:
        return {
            "exception": "address_problem",
            "evidence": reasons,
            "age_start": order.get("updated_at"),
            "proposed_next_step": "Internal: verify/correct shipping address with customer data on file; hold fulfilment until fixed.",
            "approval_needed": ["customer_message"],
        }

    bo = backorder_evidence(order)
    if bo:
        return {
            "exception": "backorder",
            "evidence": bo,
            "age_start": order.get("updated_at"),
            "proposed_next_step": "Internal: confirm restock ETA; draft delay notice for merchant review.",
            "approval_needed": ["customer_message", "inventory_edit"],
        }

    late, reasons = late_shipment(order, ref)
    if late:
        return {
            "exception": "late_shipment",
            "evidence": reasons,
            "age_start": order.get("promised_ship_by"),
            "proposed_next_step": "Internal: escalate fulfilment; draft apology/delay notice for merchant review.",
            "approval_needed": ["customer_message", "cancellation", "discount"],
        }

    return None


def main():
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "fake-orders.json")
    data = json.loads(path.read_text())
    ref = parse_dt(data["meta"]["reference_time_utc"])
    rows = []
    excluded = []
    for order in data["orders"]:
        hit = classify(order, ref)
        if hit is None:
            excluded.append(order["name"])
            continue
        start = parse_dt(hit["age_start"])
        rows.append(
            {
                "order": order["name"],
                "admin_url": order.get("admin_url"),
                "customer": (order.get("customer") or {}).get("display_name"),
                "exception": hit["exception"],
                "evidence": hit["evidence"],
                "age_hours": age_hours(start, ref),
                "age_start": hit["age_start"],
                "proposed_next_step": hit["proposed_next_step"],
                "approval_needed": hit["approval_needed"],
            }
        )

    out = {
        "label": "方法来自网站文章，没有他人实测数据",
        "source_url": data["meta"]["source_url"],
        "reference_time_utc": data["meta"]["reference_time_utc"],
        "input_orders": len(data["orders"]),
        "exception_rows": len(rows),
        "excluded_normal": excluded,
        "queue": rows,
        "actions_executed": [],
        "note": "Queue only. No refund/cancel/discount/inventory/customer send was performed.",
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
