"""本期的 "Harness"（智能体外壳）：负责把模型、工具（经 MCP）和 Skill 装配起来并循环执行。
用法：python harness.py level1|level2|level3 输出前缀
- level1：普通聊天，模型不带任何工具
- level2：同一个模型 + 通过 MCP 接上的 fetch_page 工具（= Agent）
- level3：level2 + 把 skill/compare-subscriptions/SKILL.md 放进系统提示（= Agent + Skill）
模型：Pollinations 免费匿名接口（https://text.pollinations.ai/openai，无需 key），实测返回 model=gpt-oss-20b
"""
import asyncio, json, os, sys, time, urllib.request, urllib.error, pathlib
GUARD = os.environ.get("GUARD", "1") == "1"  # 护栏开关：GUARD=0 复现没有护栏时的死循环
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client  # 依赖：pip install "mcp==2.3.0"

HERE = pathlib.Path(__file__).parent
API = "https://text.pollinations.ai/openai"
TASK = (HERE / "task_prompt.txt").read_text(encoding="utf-8").strip()

_last_call = [0.0]
def chat(messages, tools=None):
    # 免费匿名接口限速：每个 IP 每 45 秒 1 次回复，所以每次调用前先等够 46 秒
    wait = 46 - (time.time() - _last_call[0])
    if wait > 0: time.sleep(wait)
    _last_call[0] = time.time()
    body = {"model": "openai", "messages": messages, "temperature": 0.2, "seed": int(os.environ.get("SEED", "1")), "max_tokens": 8000}  # 换 SEED 才是独立重跑（同样请求接口会直接返回缓存）
    if tools: body["tools"] = tools
    for attempt in range(4):
        try:
            req = urllib.request.Request(API, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            print("  接口出错，重试：", e, e.read()[:300]); time.sleep(46); _last_call[0] = time.time()
        except Exception as e:
            print("  接口出错，重试：", e); time.sleep(15)
    raise RuntimeError("接口连续失败")

async def run(level, out):
    log = {"level": level, "guard": GUARD, "task": TASK, "steps": []}
    t0 = time.time()
    system = "你是一个乐于助人的中文助手。"
    if level == "level3":
        system += "\n\n下面是你必须遵守的技能说明（Skill）：\n" + (HERE / "skill/compare-subscriptions/SKILL.md").read_text(encoding="utf-8")
    messages = [{"role": "system", "content": system}, {"role": "user", "content": TASK}]
    if level == "level1":
        resp = chat(messages)
        log["model"] = resp.get("model"); final = resp["choices"][0]["message"].get("content", "")
    else:
        params = StdioServerParameters(command=sys.executable, args=[str(HERE / "mcp_fetch_server.py")], env=dict(os.environ))
        async with stdio_client(params) as (r, w):
            async with ClientSession(r, w) as s:
                await s.initialize()
                listed = await s.list_tools()
                tools = [{"type": "function", "function": {"name": t.name, "description": t.description, "parameters": t.input_schema}} for t in listed.tools]
                log["mcp_tools"] = [t.name for t in listed.tools]
                final = None
                seen = set(); MAX_TURNS = 8
                for turn in range(MAX_TURNS):
                    last = GUARD and turn == MAX_TURNS - 1
                    if last:  # 护栏 1：最后一轮收走工具，逼模型用已有材料交答卷
                        messages.append({"role": "user", "content": "工具调用次数已用完。请只根据已经抓到的内容给出最终表格，没抓到的写“官方页未显示”。"})
                    resp = chat(messages, None if last else tools); log["model"] = resp.get("model")
                    msg = resp["choices"][0]["message"]
                    calls = msg.get("tool_calls") or []
                    if not calls or last:
                        final = msg.get("content") or ""
                        if not final: log["empty_answer_reasoning"] = (msg.get("reasoning") or "")[:2000]
                        break
                    messages.append({"role": "assistant", "content": msg.get("content") or "", "tool_calls": calls})
                    for c in calls:
                        args = json.loads(c["function"]["arguments"] or "{}")
                        ts = time.time()
                        key = json.dumps(args, sort_keys=True)
                        if GUARD and key in seen:  # 护栏 2：同一网页不重复抓
                            text = "[护栏] 这个网址已经抓过了，内容不会变。请用已有内容继续，不要重复抓。"
                        else:
                            seen.add(key)
                            res = await s.call_tool(c["function"]["name"], args)
                            text = "".join(getattr(x, "text", "") for x in res.content)
                        log["steps"].append({"tool": c["function"]["name"], "args": args, "secs": round(time.time()-ts, 1), "result_head": text[:300]})
                        print("  调用工具", c["function"]["name"], args, "->", text[:80])
                        messages.append({"role": "tool", "tool_call_id": c["id"], "content": text})
    log["final"] = final; log["seconds"] = round(time.time() - t0, 1)
    log["finished_at"] = time.strftime("%Y-%m-%d %H:%M:%S %Z")
    pathlib.Path(out + ".json").write_text(json.dumps(log, ensure_ascii=False, indent=2), encoding="utf-8")
    pathlib.Path(out + ".md").write_text(final or "(无最终回答)", encoding="utf-8")
    print(f"{level} 完成，用时 {log['seconds']} 秒，工具调用 {len(log['steps'])} 次")

if __name__ == "__main__":
    asyncio.run(run(sys.argv[1], sys.argv[2]))
