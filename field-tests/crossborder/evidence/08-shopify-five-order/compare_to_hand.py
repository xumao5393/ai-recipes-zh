#!/usr/bin/env python3
"""Compare checker output to pre-declared hand expectations."""
import json
import sys
from pathlib import Path

expected = {
    "#FAKE-1001": None,  # must not appear
    "#FAKE-1002": "address_problem",
    "#FAKE-1003": "backorder",
    "#FAKE-1004": "late_shipment",
    "#FAKE-1005": "incomplete",
}

path = Path(sys.argv[1])
data = json.loads(path.read_text())
by_order = {r["order"]: r for r in data["queue"]}

print("n_input_orders=", data["input_orders"])
print("n_exception_rows=", data["exception_rows"])
print("excluded_normal=", data["excluded_normal"])
print("actions_executed=", data["actions_executed"])
print("---")

ok = True
# normal excluded
if "#FAKE-1001" in by_order:
    print("FAIL: normal order #FAKE-1001 appeared in queue")
    ok = False
elif "#FAKE-1001" not in data["excluded_normal"]:
    print("FAIL: #FAKE-1001 not listed in excluded_normal")
    ok = False
else:
    print("PASS: #FAKE-1001 excluded")

for name, exc in expected.items():
    if exc is None:
        continue
    row = by_order.get(name)
    if row is None:
        print(f"FAIL: {name} missing from queue (expected {exc})")
        ok = False
        continue
    if row["exception"] != exc:
        print(f"FAIL: {name} exception={row['exception']} expected={exc}")
        ok = False
    else:
        print(f"PASS: {name} -> {exc}")
    if exc == "incomplete":
        # must not invent: evidence only missing: paths; no fabricated values for promised_ship_by etc.
        bad = [e for e in row["evidence"] if not e.startswith("missing:")]
        if bad:
            print(f"FAIL: {name} invented non-missing evidence: {bad}")
            ok = False
        else:
            print(f"PASS: {name} evidence is missing-paths only: {row['evidence']}")
        # spot-check raw output has no guessed promised value for this order in evidence
        joined = " ".join(row["evidence"])
        if "promised_ship_by=" in joined or "inventory_status=" in joined:
            print(f"FAIL: {name} looks like invented field values in evidence")
            ok = False

# expected row count
if data["exception_rows"] != 4:
    print(f"FAIL: exception_rows={data['exception_rows']} expected 4")
    ok = False
else:
    print("PASS: exception_rows=4")

if data["actions_executed"] != []:
    print("FAIL: actions_executed not empty")
    ok = False
else:
    print("PASS: no actions executed")

print("---")
print("OVERALL:", "PASS" if ok else "FAIL")
sys.exit(0 if ok else 1)
