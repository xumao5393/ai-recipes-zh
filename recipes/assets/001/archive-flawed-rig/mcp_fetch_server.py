"""最小 MCP 服务器：只提供一个工具 fetch_page（抓网页正文）。
任何支持 MCP 的 AI 客户端（Claude Desktop、Cursor、本期的 harness.py）都能接上它。
运行依赖：pip install "mcp==2.3.0" beautifulsoup4（本期实测版本）
"""
import os, re, urllib.request
from bs4 import BeautifulSoup
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("fetch-page")
MAX_CHARS = int(os.environ.get("FETCH_MAX_CHARS", "5000"))  # v1 实测用 12000，模型被撑爆；v2 改成 5000

@mcp.tool()
def fetch_page(url: str) -> str:
    """抓取一个网页，返回去掉标签后的纯文本（默认最多 5000 字符）。注意：靠 JavaScript 才显示的内容抓不到。"""
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            html = r.read().decode("utf-8", "ignore")
            code = r.status
    except Exception as e:
        return f"[抓取失败] {url} -> {e}"
    soup = BeautifulSoup(html, "html.parser")
    for t in soup(["script", "style", "noscript", "svg"]):
        t.decompose()
    text = re.sub(r"\s+", " ", soup.get_text(" ")).strip()
    return f"[HTTP {code}] {url}\n{text[:MAX_CHARS]}"

if __name__ == "__main__":
    mcp.run()  # stdio 模式
