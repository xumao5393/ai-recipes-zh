#!/usr/bin/env python3
"""Recompute system_chars / plugin_pkgs_chars for captured/*.json.

Two system algorithms compared on the same files:
  A) len(system) when system is a str  — raw character count of the prompt text
  B) len(json.dumps(system, ensure_ascii=False)) — JSON encoding length
     (includes surrounding quotes + escape expansion, e.g. newline -> \\n)

Original summary.txt used B (2619 / 487).
summary-rerun.txt and reviewer used A (2591 / 481).
This script treats A as the correct "系统提示字符数"口径.
"""
from __future__ import annotations
import json, os, sys
from pathlib import Path

BASE = Path(__file__).resolve().parent

def system_stats(system):
    if isinstance(system, str):
        raw = len(system)
        dumps = len(json.dumps(system, ensure_ascii=False))
        return {
            "system_type": "str",
            "raw_chars_A": raw,
            "json_dumps_chars_B": dumps,
            "dumps_minus_raw": dumps - raw,
            "n_newlines_in_raw": system.count("\n"),
            "n_backslash_in_raw": system.count("\\"),
            "n_quote_in_raw": system.count('"'),
        }
    if isinstance(system, list):
        texts = []
        for b in system:
            if isinstance(b, dict) and isinstance(b.get("text"), str):
                texts.append(b["text"])
            elif isinstance(b, str):
                texts.append(b)
        joined = "".join(texts)
        return {
            "system_type": "list",
            "n_blocks": len(system),
            "sum_text_chars_A": len(joined),
            "json_dumps_chars_B": len(json.dumps(system, ensure_ascii=False)),
        }
    return {"system_type": type(system).__name__}

def field_chars(val):
    """Return (compact_len, spaced_len) of JSON encoding, or (0,0) if missing."""
    if val is None:
        return 0, 0
    compact = json.dumps(val, ensure_ascii=False, separators=(",", ":"))
    spaced = json.dumps(val, ensure_ascii=False)  # default separators (', ', ': ')
    return len(compact), len(spaced)

groups = [
    "captured",
    "captured-patched",
    "captured-true-default",
    "captured-telemetry-off-rerun",
]

print("# recalc_system_and_plugins.py output")
print("# cwd evidence dir:", BASE)
print()

# --- system algorithm on original captured ---
print("== system algorithm on captured/req-01.json and req-02.json ==")
for name in ("req-01.json", "req-02.json"):
    data = json.loads((BASE / "captured" / name).read_text())
    body = data["body"]
    st = system_stats(body.get("system"))
    print(f"{name}: {st}")
print()
print("Explanation: system is a JSON string. Algorithm A = len(str).")
print("Algorithm B = len(json.dumps(str)) = A + 2 (quotes) + escape expansion.")
print("For req-01: B-A = 28 = 2 quotes + 26 escape extras (mostly \\n).")
print("For req-02: B-A = 6 = 2 quotes + 4 escape extras.")
print("Original summary.txt system_chars used B; summary-rerun used A.")
print("Correct 口径 for '系统提示字符数': A (raw chars) => 2591 / 481.")
print()

# --- full table ---
print("== per-file metrics ==")
header = (
    "file body_bytes system_A system_B tools tools_json_compact "
    "session_log_compact plugin_compact plugin_spaced"
)
print(header)
rows = []
for g in groups:
    d = BASE / g
    if not d.is_dir():
        continue
    for fn in sorted(d.glob("req-*.json")):
        data = json.loads(fn.read_text())
        body = data["body"]
        st = system_stats(body.get("system"))
        a = st.get("raw_chars_A") or st.get("sum_text_chars_A")
        b = st.get("json_dumps_chars_B")
        tools = body.get("tools") or []
        tj_c, tj_s = field_chars(tools)
        sl_c, sl_s = field_chars(body.get("dsh_session_log"))
        pp_c, pp_s = field_chars(body.get("dsh_plugin_packages"))
        # missing field -> chars 0
        if body.get("dsh_session_log") is None:
            sl_c = sl_s = 0
        if body.get("dsh_plugin_packages") is None:
            pp_c = pp_s = 0
        rel = f"{g}/{fn.name}"
        line = f"{rel} {data.get('body_len')} {a} {b} {len(tools)} {tj_c} {sl_c} {pp_c} {pp_s}"
        print(line)
        rows.append((g, fn.name, data.get("body_len"), a, b, len(tools), tj_c, sl_c, pp_c, pp_s))

print()
print("== true-default vs telemetry-off plugin delta ==")
# find req-01 of both
def get_pp(group):
    data = json.loads((BASE / group / "req-01.json").read_text())
    pp = data["body"].get("dsh_plugin_packages")
    c, s = field_chars(pp)
    return c, s, data["body_len"]

td_c, td_s, td_body = get_pp("captured-true-default")
off_c, off_s, off_body = get_pp("captured-telemetry-off-rerun")
print(f"true-default: body_bytes={td_body} plugin_compact={td_c} plugin_spaced={td_s}")
print(f"telemetry-off: body_bytes={off_body} plugin_compact={off_c} plugin_spaced={off_s}")
print(f"delta body_bytes: {td_body - off_body}")
print(f"delta plugin_compact: {td_c - off_c}")
print(f"delta plugin_spaced: {td_s - off_s}")
print("Note: body_bytes comes from the raw HTTP body (compact JSON as sent).")
print("plugin_spaced (default json.dumps) over-counts vs body; compact matches the +74 body delta.")

# Also show original captured plugin chars both ways
print()
print("== original captured/req-01 plugin_pkgs ==")
c, s, _ = get_pp("captured")
print(f"compact={c} spaced={s}  (summary.txt had 6144 which is spaced)")
# verify 6144
data = json.loads((BASE/"captured"/"req-01.json").read_text())
spaced = json.dumps(data["body"]["dsh_plugin_packages"], ensure_ascii=False)
compact = json.dumps(data["body"]["dsh_plugin_packages"], ensure_ascii=False, separators=(",", ":"))
print(f"verify spaced len={len(spaced)} compact len={len(compact)}")

# session_log similarly
sl = data["body"]["dsh_session_log"]
print(f"session_log spaced={len(json.dumps(sl, ensure_ascii=False))} compact={len(json.dumps(sl, ensure_ascii=False, separators=(',',':')))}")
# tools
tools = data["body"]["tools"]
print(f"tools spaced={len(json.dumps(tools, ensure_ascii=False))} compact={len(json.dumps(tools, ensure_ascii=False, separators=(',',':')))}")
