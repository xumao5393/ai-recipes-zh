#!/usr/bin/env python3
"""Supplementary check (written AFTER seeing agent outputs, 2026-11-09 ~19:30 EST):
for every 'path=value' evidence string, look up the path in fake-orders.json and
report whether the stated value matches the data. 'missing:path' must be null/absent."""
import json, re, sys
orders = {o["name"]: o for o in json.load(open(sys.argv[1]))["orders"]}
def get(o, path):
    cur = o
    for part in re.findall(r"[^.\[\]]+|\[\d+\]", path):
        if part.startswith("["):
            i = int(part[1:-1])
            if not isinstance(cur, list) or i >= len(cur): return ("ABSENT",)
            cur = cur[i]
        else:
            if not isinstance(cur, dict) or part not in cur: return ("ABSENT",)
            cur = cur[part]
    return cur
def norm(v):
    if isinstance(v, (list, dict)): return json.dumps(v, ensure_ascii=False, separators=(",", ":"))
    if v is None: return "null"
    return str(v)
bad = 0; total = 0
for row in json.load(open(sys.argv[2]))["queue"]:
    o = orders[row["order"]]
    for ev in row["evidence"]:
        total += 1
        if ev.startswith("missing:"):
            v = get(o, ev[8:])
            ok = v is None or v == ("ABSENT",) or v == [] 
            print(("OK  " if ok else "BAD ") + row["order"], ev, "| data:", norm(v) if v != ("ABSENT",) else "ABSENT")
        else:
            path, _, val = ev.partition("=")
            v = get(o, path)
            got = norm(v) if v != ("ABSENT",) else "ABSENT"
            ok = got == val or (got == "" and val in ('""', "")) or got.replace(" ", "") == val.replace(" ", "")
            print(("OK  " if ok else "BAD ") + row["order"], ev, "| data:", got)
        bad += 0 if ok else 1
print(f"TOTAL evidence={total} mismatched={bad}")
