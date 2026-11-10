"""Offline driver: serve a frozen fictional catalog through tests.fakes-style MockTransport,
then call audit_catalog via the in-process MCP client (same pattern as tests/test_server.py).
Does not connect to mock.shop or any Shopify endpoint.
"""
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import httpx
from mcp import Client

from mcp_store_tools.server import build_server
from mcp_store_tools.storefront import Config, Storefront
from tests import fakes


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def catalog_transport(nodes: list[dict[str, Any]], calls: list[dict[str, Any]]) -> httpx.MockTransport:
    def handler(payload: dict[str, Any]) -> dict[str, Any]:
        query: str = payload["query"]
        if "query Browse" in query:
            # one page: all frozen nodes, no cursor
            return {
                "data": {
                    "products": {
                        "nodes": nodes,
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                    }
                }
            }
        # everything else stays on the repo's fake Storefront responses
        return fakes.respond(payload)

    return fakes.transport(handler=handler, calls=calls)


async def run(fixture: Path) -> dict[str, Any]:
    data = json.loads(fixture.read_text())
    nodes = data["nodes"]
    calls: list[dict[str, Any]] = []
    store = Storefront(
        Config(shop="demo.myshopify.com", token="public-token"),
        transport=catalog_transport(nodes, calls),
        backoff=0,
    )
    async with Client(build_server(store)) as client:
        tools = [t.name for t in (await client.list_tools()).tools]
        result = await client.call_tool(
            "audit_catalog", {"max_products": 1000, "examples_per_check": 10}
        )
        if result.is_error:
            raise SystemExit(f"audit_catalog returned a tool error: {result.content}")
        payload = result.structured_content
        if payload is None:
            # fallback like tests/test_server.py
            from mcp_types import TextContent

            first = result.content[0]
            assert isinstance(first, TextContent)
            payload = json.loads(first.text)
    # record only operation names and URLs from the fake transport, not full query text if huge
    call_summary = []
    for c in calls:
        q = c.get("query", "")
        op = "unknown"
        for name in (
            "Search",
            "ProductsByKeyword",
            "Product",
            "Recommendations",
            "StoreInfo",
            "PageSearch",
            "PageList",
            "CollectionBrowse",
            "Browse",
            "Collections",
            "Policies",
        ):
            if f"query {name}" in q:
                op = name
                break
        call_summary.append({"operation": op, "url": c.get("url"), "after": (c.get("variables") or {}).get("after")})
    return {"tools": tools, "report": payload, "transport_calls": call_summary, "call_count": len(calls)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", required=True)
    parser.add_argument("--expected-sha256", required=True, help="sha256 of the fixture file frozen before this run")
    args = parser.parse_args()
    fixture = Path(args.fixture)
    actual = sha256_file(fixture)
    if actual != args.expected_sha256:
        raise SystemExit(f"fixture sha256 mismatch: expected {args.expected_sha256}, got {actual}")
    out = asyncio.run(run(fixture))
    json.dump(out, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
