#!/usr/bin/env python3
"""Uniform recalc for #10 compare draft.

Reads **unmasked originals** from deepseek-harness/internal-archive/ when present
(so system/tools digests stay reproducible after repo masking). Results
(numbers.json / recalc_compare.out.txt) are what get checked into repo.

America/New_York.
"""
from __future__ import annotations
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
EV = HERE.parents[0]  # evidence/
DH = EV.parents[1]    # deepseek-harness/
ARCH = DH / "internal-archive"

ROWS = [
    {
        "shell": "dsh-true-default",
        "label": "dsh 0.2.2-rc.1 真默认（未设 DSH_TELEMETRY_MODE）",
        "source": "02-dsh-request-capture/captured-true-default/req-01.json",
        "req_count_dir": "02-dsh-request-capture/captured-true-default",
        "note": "run-true-default.txt；body_len=54923",
    },
    {
        "shell": "dsh-telemetry-off",
        "label": "dsh + DSH_TELEMETRY_MODE=off",
        "source": "02-dsh-request-capture/captured-telemetry-off-rerun/req-01.json",
        "req_count_dir": "02-dsh-request-capture/captured-telemetry-off-rerun",
        "note": "与 captured/req-01 同为 54849；以 telemetry-off-rerun 为准",
    },
    {
        "shell": "dsh-patched",
        "label": "dsh + 隐私补丁",
        "source": "02-dsh-request-capture/captured-patched/req-01.json",
        "req_count_dir": "02-dsh-request-capture/captured-patched",
        "note": "",
    },
    {
        "shell": "claude-code",
        "label": "Claude Code 2.1.321",
        "source": "05-claude-code/captured/req-01.json",
        "req_count_dir": "05-claude-code/captured",
        "note": "8 次为同形 401 重试；system/tools 原文在 internal-archive",
    },
    {
        "shell": "opencode",
        "label": "OpenCode 2.2.6",
        "source": "06-opencode/capture-sayhi-20261109-1447/captured/req-01.json",
        "req_count_dir": "06-opencode/capture-sayhi-20261109-1447/captured",
        "note": "system/tools 原文在 internal-archive",
    },
    {
        "shell": "aider",
        "label": "Aider 0.86.2",
        "source": "07-aider/capture-sayhi-20261109-1449/captured/req-01.json",
        "req_count_dir": "07-aider/capture-sayhi-20261109-1449/captured",
        "note": "无 tools 字段；system 原文在 internal-archive",
    },
]


def resolve(rel: str) -> Path:
    """Prefer internal-archive original; fall back to repo evidence."""
    a = ARCH / rel
    if a.exists():
        return a
    return EV / rel


def system_chars(body: dict) -> tuple[int | None, str]:
    sys = body.get("system")
    if isinstance(sys, str):
        return len(sys), 'len(body["system"])  # 顶层 system 字符串'
    if isinstance(sys, list):
        parts = []
        for block in sys:
            if isinstance(block, dict) and isinstance(block.get("text"), str):
                parts.append(block["text"])
            elif isinstance(block, dict) and isinstance(block.get("text"), dict) and "length" in block["text"]:
                # already-masked digest — use stored length
                parts.append("x" * int(block["text"]["length"]))  # only for len
                return sum(int(b["text"]["length"]) for b in sys if isinstance(b, dict) and isinstance(b.get("text"), dict)), \
                    'sum(text.length)  # 打码版摘要字段（应优先用 internal-archive 原件）'
        return len("".join(parts)), 'len("".join(block["text"]))  # 顶层 system 块 join'
    msgs = body.get("messages") or []
    parts = []
    for m in msgs:
        c = m.get("content")
        if m.get("role") == "system":
            if isinstance(c, str):
                parts.append(c)
            elif isinstance(c, dict) and "length" in c:
                return sum(int(x["content"]["length"]) for x in msgs if x.get("role")=="system" and isinstance(x.get("content"), dict)), \
                    'sum(content.length)  # 打码版摘要'
    if parts:
        return len("".join(parts)), 'len("".join(m["content"] for role==system))  # messages join'
    return None, "no system"


def tools_stats(body: dict) -> tuple[str, int | None, int | None, str]:
    if "tools" not in body:
        return "absent", None, None, "无 tools 字段"
    tools = body["tools"]
    # masked form: list of digests + optional _tools_meta
    meta = body.get("_tools_meta")
    if meta and meta.get("_masked"):
        return "present(masked-meta)", meta.get("tools_n"), meta.get("tools_json_compact_chars"), \
            "from _tools_meta (pre-mask compact length)"
    if tools is None:
        return "null", None, None, "tools=null"
    if isinstance(tools, list) and tools and isinstance(tools[0], dict) and tools[0].get("_masked"):
        # digests only — compact length not reconstructible; require archive
        return "present(masked-only)", len(tools), None, "masked digests without compact; use archive"
    compact = json.dumps(tools, ensure_ascii=False, separators=(",", ":"))
    return "present", len(tools), len(compact), "json.dumps(tools, ensure_ascii=False, separators=(',',':'))"


def main() -> None:
    out_rows = []
    lines = []
    lines.append("# recalc_compare.out — generated by recalc_compare.py")
    lines.append("# INPUT: prefer deepseek-harness/internal-archive/<rel> (unmasked originals)")
    lines.append("# body_len = req JSON body_len（原始 HTTP 请求体字节，抓包时记录）")
    lines.append("# system_chars = 在**内部原件**上按下方 system_method 计算（字符数，非 token）")
    lines.append("# tools_json_compact_chars = 同一 dumps 口径，在内部原件上计算")
    lines.append("# 结果文件 numbers.json / 本 out 入库；原件不入库")
    lines.append("# request_count = 该次抓包目录下 req-*.json 个数（仅此配置：本地假服务 + 单次 say hi，n=1）")
    lines.append("")
    for meta in ROWS:
        path = resolve(meta["source"])
        src_kind = "internal-archive" if str(path).startswith(str(ARCH)) else "repo-evidence"
        j = json.loads(path.read_text())
        body = j["body"]
        sc, smethod = system_chars(body)
        tstate, tn, tcompact, tmethod = tools_stats(body)
        req_dir_arch = ARCH / meta["req_count_dir"]
        req_dir_ev = EV / meta["req_count_dir"]
        req_dir = req_dir_arch if req_dir_arch.exists() else req_dir_ev
        n_req = len(sorted(req_dir.glob("req-*.json")))
        row = {
            "shell": meta["shell"],
            "label": meta["label"],
            "source": meta["source"],
            "source_resolved": str(path.relative_to(DH)) if path.is_relative_to(DH) else str(path),
            "source_kind": src_kind,
            "path": j.get("path"),
            "body_len": j.get("body_len"),
            "system_chars": sc,
            "system_method": smethod,
            "system_chars_basis": "computed on internal-archive originals (pre-mask)",
            "tools_state": tstate,
            "tools_n": tn,
            "tools_json_compact_chars": tcompact,
            "tools_method": tmethod,
            "request_count": n_req,
            "request_count_note": "仅此配置：本地假服务 + 单次 say hi，n=1",
            "note": meta["note"],
            "n": 1,
        }
        out_rows.append(row)
        lines.append(
            f"{meta['shell']}\tsrc={src_kind}\tbody_len={row['body_len']}\tsystem_chars={sc}\t({smethod})\t"
            f"tools_state={tstate}\ttools_n={tn}\ttools_compact={tcompact}\trequest_count={n_req}"
        )
    (HERE / "numbers.json").write_text(json.dumps(out_rows, ensure_ascii=False, indent=2) + "\n")
    (HERE / "recalc_compare.out.txt").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
