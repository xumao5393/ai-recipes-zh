# README / SECURITY / audit.py 与本轮相关的原文摘录
# 仓库: https://github.com/thealirazadev/mcp-store-tools
# commit: d0cc908416dadf38602cb002d390bd62b85c114c

==== README.md ====
L7: ![coverage](https://img.shields.io/badge/coverage-%E2%89%A595%25-brightgreen)
L14: catalog for the merchant in one call. It is read-only by construction: it uses a Storefront API
L15: token, which can only see what the public storefront already shows.
L19:                                              13 read-only tools          (public token)
L34: - **A whole-catalog audit in one tool call.** `audit_catalog` walks up to 5,000 products in the
L35:   server and returns counts, percentages, examples, and the top three fixes, instead of the
L36:   model paging through the catalog and burning tokens.
L53: No Shopify account needed: `--demo` uses Shopify's public sample store.
L79: Every tool carries the MCP `readOnlyHint`, and failures come back as tool errors the model can
L80: relay ("the store is busy, try again shortly"), never stack traces or the token.
L181: Product descriptions and policies are written by merchants and suppliers, so the server treats
L182: them as untrusted:
L183: 
L184: - HTML is stripped to plain text (script and style contents are dropped), so markup cannot hide
L185:   instructions.
L186: - Every text field is length-capped, so one product cannot flood the model's context.
L187: - Tool descriptions and the server instructions tell the model the content is data to quote,
L188:   not instructions to follow.
L200: The default tests never call Shopify: the GraphQL client runs against `httpx.MockTransport`, the
L201: server tests connect a real MCP client in-process to check the tool list, schemas, and error
L202: results a client actually sees, and a skill test checks `SKILL.md` names exactly the served tools.
L203: 
L204: `MCP_STORE_TOOLS_LIVE=1 uv run pytest tests/test_live.py` starts the server in demo mode over
L205: stdio and over HTTP and calls the tools against the real Storefront API. CI runs it weekly, and
L206: builds the Docker image on every push. With `SHOPIFY_STORE_DOMAIN` and
L207: `SHOPIFY_STOREFRONT_TOKEN` also set (a development store with test data), it additionally checks
L208: a real store and the wrong-token error; CI reads them from the `SHOPIFY_STORE_DOMAIN` variable and

==== SECURITY.md ====
L14:   what the public storefront shows. It cannot see orders, customers, or drafts, and cannot write
L15:   anything. Never configure it with an Admin API token.
L16: - **Store content is untrusted.** Product and policy text is stripped of HTML, length-capped, and

==== src/mcp_store_tools/audit.py（audit_catalog 返回的 scope 原文） ====
L91:         "scope": "Published storefront data only: drafts, inventory counts, SEO fields, and "
L92:         "sales are not visible to this audit.",
L93:     }
