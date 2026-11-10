# 15 mcp-store-tools：只读 Shopify 目录审计 MCP（离线实测）

**一句话结论**：这是一个只读的 Shopify Storefront MCP（源码里登记了 13 个工具，含 `audit_catalog`）。本机在隔离 venv 里装上依赖后，在 `unshare -rn` 断网命名空间（只打开回环口）跑默认测试：**75 passed, 4 skipped**（n=1，4 条是要连真实 Storefront / `--demo` 的 live 测试，本轮未开）；同一次带 `--cov`，覆盖率 **98.90%**（n=1）。用仓库自带的 `tests/fakes.py` 假 Storefront，加上 13 条自编虚构商品，经 MCP 客户端调 `audit_catalog`，返回的计数、命中 handle、`top_issues` 与事先手算一致（n=1）。**没有**连接 mock.shop 或任何 Shopify 接口，也没有用 `--demo`、没有接真店、没有让 Agent 驱动。整篇只说明离线能不能跑通、这份假目录上计数是否与规则一致，不评价规则准不准。

- 仓库：[thealirazadev/mcp-store-tools](https://github.com/thealirazadev/mcp-store-tools)，固定在 commit [`d0cc9084`](https://github.com/thealirazadev/mcp-store-tools/commit/d0cc908416dadf38602cb002d390bd62b85c114c)（`build: release 0.7.1`；提交时间 2026-11-09 01:32:52 +0500，换算为 **2026-11-08 15:32:52 EST**）。许可证 MIT（clone 内 LICENSE）。2026-11-09 21:26 EST 查询 GitHub API 返回 **403**（`x-ratelimit-remaining: 0`），按规矩这条线停止、不改头不换工具重试，因此星标、fork、仓库创建时间本次**未记录**（见 [repo-meta.txt](evidence/15-mcp-store-tools/repo-meta.txt)）。没有找别人实际使用的记录。
- README 自己写的限制与口径（完整行号见 [readme-limitations-excerpt.txt](evidence/15-mcp-store-tools/readme-limitations-excerpt.txt)）：
  - 覆盖率徽章写 `≥95%`（README L7）——这是**作者自述**；本轮另外跑了一次 `pytest --cov`，得到 98.90%（见下）。
  - 「The default tests never call Shopify: the GraphQL client runs against `httpx.MockTransport`…」（L200–202）。
  - live 测试要 `MCP_STORE_TOOLS_LIVE=1`，才会「calls the tools against the real Storefront API」（L204–205）；接真店还要 Storefront token，README 写的是先在 Shopify 后台装 Headless（L95–98）——那一步算注册，不测。
  - `audit_catalog` 返回的 `scope` 原文（`audit.py` L91–92）：「Published storefront data only: drafts, inventory counts, SEO fields, and sales are not visible to this audit.」
  - SECURITY.md：Storefront token「cannot see orders, customers, or drafts, and cannot write」。

## 1. 先审源码（详见 [source-review.txt](evidence/15-mcp-store-tools/source-review.txt)）

- Python 包，`requires-python >=3.11`；本机 / venv 均为 Python 3.13.5（[python-version.txt](evidence/15-mcp-store-tools/python-version.txt)，n=1）。
- 构建后端是 hatchling，**没有** setup.py，也**没有**自定义 build hook / 安装期脚本。`[project.scripts]` 只有启动入口。
- 运行时出网只在 `storefront.py`：`httpx` POST 到 `https://{shop}/api/{version}/graphql.json`；`--demo` 时店铺为 `mock.shop`、端点为 `https://mock.shop/api`、token 为空。`audit.py` 本身不出网。HTTP 传输是本机 uvicorn，本轮未起。
- `@server.tool` 登记的工具就是 13 个，与 README 表格、以及后面 `list_tools` 的结果一致。另有 3 个 resource、3 个 prompt，不计入 13。
- 审查结论：可以安装依赖，然后只做断网测试和假目录上的 `audit_catalog`。

## 2. mock.shop 条款（读过法律路径，本轮仍不连）

按规矩先找**明确适用于 mock.shop 的条款**。2026-11-09 21:28 EST，用 curl 默认 UA（不加 `-A`、不加 `-L`），对下列 URL 各请求一次（n=1/次），全部 **HTTP 404**，正文是 `No page at /… Start at https://mock.shop/llms.txt`（命令、响应头和正文见 [TERMS-DECISION.txt](evidence/15-mcp-store-tools/TERMS-DECISION.txt) 与 [terms/](evidence/15-mcp-store-tools/terms/)）：

`https://mock.shop/terms`、`/terms-of-service`、`/tos`、`/legal`、`/privacy`、`/privacy-policy`、`/legal/terms`、`/aup`。

没有 403，没有拦截页。DNS 把 mock.shop 解析到 `198.18.0.1`，与 github.com / pypi.org 相同，按本机代理假 IP 记录，未当作 sinkhole，也没有改解析或直连 IP。没有抓首页，没有请求 `/api`。404 正文指向的 `llms.txt` 不是条款页，没有再请求，也没有据此换路径。

**决定**：读不到适用条款，按规则等于不允许；产品页「auth-free, no API keys」一类文案不能当依据。本轮即使读到允许也不会连，实际也未连。

## 3. 安装依赖

隔离 venv，`pip install <upstream> pytest pytest-asyncio pytest-cov`（非 editable，以免改脏 worktree）。第一次因本机没有 `/usr/bin/time`，包还没开始装就退出 127，已记在日志里；随后用 bash 的 `TIMEFORMAT` 重跑同一条 pip 命令，**exit 0**，wall ≈ 13.938 s（[run-pip-install.txt](evidence/15-mcp-store-tools/run-pip-install.txt)，n=1）。wheel：`mcp_store_tools-0.7.1-py3-none-any.whl`，size=25684，sha256=`e57a8840ee157af000d1fc97769cb13f7bca47b4b03a463deb63348c10856e52`。装完后上游 `git status` 仍干净。

## 4. 默认测试（断网，n=1）

`unshare -rn` + `ip link set lo up`，并 unset `MCP_STORE_TOOLS_LIVE` / `SHOPIFY_STORE_DOMAIN` / `SHOPIFY_STOREFRONT_TOKEN`。同一命名空间里 `curl https://pypi.org` 与 `https://github.com` 均为 `Could not resolve host`（exit 6）。然后：

`python -m pytest --cov --cov-report=term -v tests`

结果原文（[run-pytest.txt](evidence/15-mcp-store-tools/run-pytest.txt)）：

```
collected 79 items
...
Required test coverage of 95.0% reached. Total coverage: 98.90%
======================== 75 passed, 4 skipped in 3.90s =========================
```

4 条 skipped 均为 `tests/test_live.py`（未设 `MCP_STORE_TOOLS_LIVE=1`）。覆盖率量的是这次装进 venv 的 0.7.1 包（由同一 commit 打的 wheel），不是作者徽章的口头数字；缺的 7 条语句见该日志的 coverage 表。总 wall ≈ 4.519 s。只跑了这一次。

## 5. 假目录上调 `audit_catalog`（n=1）

输入是 13 条自编虚构商品（不是 mock.shop、也不是真店），GraphQL 节点写在 [fixtures/catalog-nodes.json](evidence/15-mcp-store-tools/fixtures/catalog-nodes.json)。按 `audit.py` 规则事先手算的预期见 [fixtures/hand-expected.md](evidence/15-mcp-store-tools/fixtures/hand-expected.md)。二者 sha256 在 **2026-11-09 21:31:38 EST** 冻结，调用前与调用后核对仍是（[pre-run-sha256-check.txt](evidence/15-mcp-store-tools/pre-run-sha256-check.txt)）：

```
51bdbcd6dfa662d72d4b1cc88cdc94bc30c8208351b09b528eab0023d3c5252a  catalog-nodes.json
ba4da4676f78fa275c6fd7073a11c1ae0a2b28855275bc8e91250b00b0ebcd6f  hand-expected.md
```

驱动脚本（[audit_catalog_driver.py](evidence/15-mcp-store-tools/audit_catalog_driver.py)）用 `tests.fakes` 的 `MockTransport`：Browse 查询返回这份冻结目录，其余仍走仓库自带假响应；再按官方测试同款的进程内 MCP `Client` 调 `list_tools` 和 `audit_catalog`。同样在 `unshare -rn` 里跑（21:32:26–21:32:27 EST，wall ≈ 0.660 s，[run-audit-catalog.txt](evidence/15-mcp-store-tools/run-audit-catalog.txt)）。

完整命令（在 `d0cc908` 的上游 clone 目录里跑；`tests.fakes` 来自上游仓库的 `tests/`，所以要 `PYTHONPATH=.`，否则会报 import 不到 `tests.fakes`）：

```bash
# 目录布局：<sandbox>/15-mcp-store-tools/{upstream,venv,drivers,fixtures}
# upstream = git clone 后 checkout d0cc908；drivers/ 放 audit_catalog_driver.py；fixtures/ 放 catalog-nodes.json
cd <sandbox>/15-mcp-store-tools/upstream
unshare -rn bash -c 'ip link set lo up; PYTHONPATH=. ../venv/bin/python ../drivers/audit_catalog_driver.py \
  --fixture ../fixtures/catalog-nodes.json \
  --expected-sha256 51bdbcd6dfa662d72d4b1cc88cdc94bc30c8208351b09b528eab0023d3c5252a'
```

2026-11-09 21:39 EST 按这条命令又跑了一次（n=1，exit 0，real 0.767 s），输出与入库 JSON 的 sha256 相同（`ee5407f3…126d`）（[rerun-cmd-check-r1.txt](evidence/15-mcp-store-tools/rerun-cmd-check-r1.txt)）；这只是复核命令能跑，不算稳定性证据。

- `list_tools`：13 个名字，与源码一致。
- `audit_catalog`：`products_checked=13`，`truncated=false`，`top_issues=["duplicate_title","short_description","no_image"]`，`notes=[]`；11 类检查的 count 与命中 handle 均与手算一致（对照见 [responses/hand-expected-vs-actual.txt](evidence/15-mcp-store-tools/responses/hand-expected-vs-actual.txt)，完整 JSON 见 [responses/audit-catalog-fictional.json](evidence/15-mcp-store-tools/responses/audit-catalog-fictional.json)）。
- 假传输只记到 **1 次** Browse，URL 是驱动里写的 `https://demo.myshopify.com/api/2026-10/graphql.json`，不是 mock.shop。日志里那条 `HTTP Request: POST … "HTTP/1.1 200 OK"` 是 httpx 对 MockTransport 打的 INFO，不是出网。

只说明这份自编目录上，工具按自身规则给出了与手算相符的计数；**不能**据此说它在真实目录上准不准。

## 没测的

- 没有连接 mock.shop，没有跑 `--demo`，没有连任何 Shopify / Storefront 端点，没有装 Headless，没有真店 token。
- 没有跑 `tests/test_live.py`，没有跑 `evals/` 或 `scripts/render_demo.py`。
- 没有把 MCP 接到 Grok Bot、dsh 或其它外部 Agent / 模型。
- 没有测 `build_cart_link` 等其它工具在这份自编目录上的对错（默认测试盖过仓库自带假数据上的行为，但那不是本轮手算对照的对象）。
- 没有测 HTTP 传输、Docker 镜像。
- GitHub API 因 403 未拿到星标等信息，未重试。
