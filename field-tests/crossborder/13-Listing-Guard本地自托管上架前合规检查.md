# 13 Listing Guard：本地自托管上架前合规检查（假 listing）

**一句话结论**：这是一个自托管的 Etsy/Amazon 上架前检查（规则 + 自建商标目录 + 变体结构 + MCP）。本机 **没有可用的 Docker 守护进程**（静态二进制起不来：缺 iptables / libnetwork），改用 **Temurin JDK 21.0.13 + PostgreSQL 17.11 + pgvector 0.8.0** 在本机把 API 跑起来（n=1）。`./mvnw -DskipTests -pl api,mcp-server -am package` **BUILD SUCCESS**（约 23 s，n=1）。用 admin 在本机实例建了 `demo-client` 和一把 API key（Kumo 裁定：这不算第三方注册；key 不进公开证据）。自编假 listing 冻结 sha256 后：看到 01 缺 `category` 之后才补的 01b，对 `POST /api/v1/checks` 返回 **0 findings**（只说明补全后能过这一条规则，不能说明「干净样例会被判干净」）；故意违规样例返回多条 ERROR/WARNING；对仓库自带的虚构 DEMO 商标目录，`POST /api/v1/trademark-checks` 对标题 `Zibblefrax` 给出 **HIGH / catalog_exact**；故意错误的 Amazon 变体对 `POST /api/v1/variation-checks` 打出 `parent_sku` 不匹配等 WARNING。MCP 在本机 `127.0.0.1:8765/mcp` 起过一次，`tools/list` 看到 6 个工具；对 01b 调 `check_listing` 返回 findings=[]，但这是缓存命中，MCP 只验证了能转发到 API、能拿回结果，不是重新检查。**整篇只说明本机能不能跑通，不评价准不准。**

- 仓库：[thanhdatpb/Listing-Guard](https://github.com/thanhdatpb/Listing-Guard)，固定在 commit [`deaa18a9`](https://github.com/thanhdatpb/Listing-Guard/commit/deaa18a9e29cb591d770ce2eab5a8d864ba8aa6f)（2026-11-09 10:48 +0700 merge）。2026-11-09 20:22 EST 查询时 0 星、0 fork，许可证 MIT（见 [repo-meta.txt](evidence/13-listing-guard/repo-meta.txt)）。没有找到别人实际使用的记录。
- README「Before you rely on it」原话摘录（完整行号见 [readme-limitations-excerpt.txt](evidence/13-listing-guard/readme-limitations-excerpt.txt)）：
  - **The trademark catalog is yours to load.** No trademark data is shipped or downloaded. …
  - **No accuracy has been measured on real data.** The evaluation of the trademark check (ADR-009, PR A4) has not been run, and every threshold and word list of the trademark ruleset is marked `unverified`. …
  - **Marketplace limits are only as verified as their source.** Each rule records a source status (`verified`, `secondary` or `unverified`) …
  - **Policy retrieval has not been evaluated.** …

## 1. 先审源码（详见 [source-review.txt](evidence/13-listing-guard/source-review.txt)）

- Maven 多模块；`pom.xml` 写 `java.version=21`。Dockerfile 构建用 `eclipse-temurin:25-jdk`，运行用 `25-jre`——我们本地按 21 编译，能过。
- **没有** npm 生命周期脚本。默认 `listing-guard.embedding.provider=none`：规则 / 商标 / 变体检查不需要模型；`provider=api` 才会用 `HttpClient` 打 Google Gemini embeddings；`ollama` 才连本机 Ollama。本轮保持 `none`，没跑 ingest。
- MCP 服务器是独立 jar：只做 REST 客户端，不连库；默认 stdio，可选本机 Streamable HTTP。
- 本机 DNS：`github.com` / `generativelanguage.googleapis.com` / `ollama.com` 解析到 `198.18.0.1`（沙箱出口）。**没有**用 DoH、改 hosts 或直连 IP 去绕；外连模型相关域名一律不碰。

## 2. 环境：Docker 不可用 → JDK 21 + Postgres

| 步骤 | 结果（均 n=1） |
|---|---|
| 系统自带 `docker` / `java` | 均 ABSENT（[docker-availability.txt](evidence/13-listing-guard/docker-availability.txt)） |
| `apt-get install docker.io` | apt 走 http 80 端口，到 198.18.0.1，装不上（[docker-install-attempt.txt](evidence/13-listing-guard/docker-install-attempt.txt)） |
| Docker 静态包 29.9.3 | 能下载；`dockerd` 因缺 iptables / libnetwork bind 起不来 |
| Temurin JDK 21.0.13+9 | 便携包安装成功（[jdk-install.txt](evidence/13-listing-guard/jdk-install.txt)、[java-version.txt](evidence/13-listing-guard/java-version.txt)） |
| PostgreSQL 17.11 + pgvector 0.8.0 | 用 curl 按域名 `https://deb.debian.org/...` 拉 .deb 再 `dpkg`（系统 DNS，没有指定 IP）；集群 online，扩展 `vector`/`pg_trgm` 可用（[postgres-install.txt](evidence/13-listing-guard/postgres-install.txt)、[postgres-start.txt](evidence/13-listing-guard/postgres-start.txt)） |

HTTP 返回 500，哪一层返回的没查清；改用 HTTPS 按域名下载，未使用任何绕行手段。Kumo 已认定不算绕开网络控制。证据第 2 行「curl to Fastly IP」是不准确的表述，更正见 postgres-install.txt、source-review.txt 文末和 [CORRECTIONS.md](evidence/13-listing-guard/CORRECTIONS.md)。

公开依赖下载（JDK、Maven Central、Debian .deb、Docker 静态包）已记进对应证据；**没有**为被 198.18 拦住的域名改解析。

## 3. 构建与启动

- `./mvnw -B -DskipTests -pl api,mcp-server -am package` → **BUILD SUCCESS**，Total time ≈ 23.006 s（[run-mvn-package.txt](evidence/13-listing-guard/run-mvn-package.txt)，n=1）。产物：`listing-guard-api.jar`、`listing-guard-mcp.jar`。
- admin：`client create demo-client` 成功（[run-admin-client-create.txt](evidence/13-listing-guard/run-admin-client-create.txt)，n=1）；`key create demo-client --label=first-key` 打出 key 一次，公开版已打码（[run-admin-key-create.txt](evidence/13-listing-guard/run-admin-key-create.txt)，n=1）。
- 商标目录：指向仓库自带虚构 `catalogs/demo`，`--catalog=demo-fictional-2026-11` → 版本 **`demo-fictional-2026-11-f1deea4df852`**（read 10 / filtered 2 / loaded 8）（[run-trademark-import.txt](evidence/13-listing-guard/run-trademark-import.txt)，n=1）。这是 DEMO 虚构词，不是真实商标库。
- API：`LISTING_GUARD_EMBEDDING_PROVIDER=none` + 上述 catalog version；`/health` → `{"status":"UP"}`（[run-api-start.txt](evidence/13-listing-guard/run-api-start.txt)，n=1）。

## 4. 假 listing 与接口结果（先冻结再调用）

输入与 sha256 见 [fixtures/](evidence/13-listing-guard/fixtures/)，冻结时间 [frozen-at.txt](evidence/13-listing-guard/fixtures/frozen-at.txt)，核对 [pre-run-sha256-check.txt](evidence/13-listing-guard/pre-run-sha256-check.txt)。原始响应见 [responses/](evidence/13-listing-guard/responses/)。01 等在 20:29:41 EST 冻结；**01b 是看到 01 缺 `category` 之后才补的样例**，冻结时间 20:30:50 EST，跟调用是同一秒。

源码写明：`POST /api/v1/checks` **既不展示也不依赖**商标包；商标是 `POST /api/v1/trademark-checks`，变体是 `POST /api/v1/variation-checks`。下表按实际调用的端点记。

| 样例 | 端点 | HTTP | 摘要（n=1） |
|---|---|---|---|
| 01 本意干净但缺 `category` | `/api/v1/checks` | 200 | 1× ERROR `required_fields` / `category` |
| **01b** 看了 01 的结果后补上 `category` | `/api/v1/checks` | 200 | **findings=[]**，summary 0/0/0；只说明补全后能过这一条规则，不能说明「干净样例会被判干净」 |
| 02 明显违规（超长促销标题、quantity=0、重复 tag 等） | `/api/v1/checks` | 200 | 4 ERROR + 4 WARNING（含 `title_length`、`title_promotional_terms`、`tag_count`、`duplicate_tags` 等） |
| 03 标题含 DEMO 词 `Zibblefrax` | `/api/v1/checks` | 200 | 仅缺 category 的规则 ERROR（商标不在此端点） |
| 03 同上 | `/api/v1/trademark-checks` | 200 | **riskLevel=HIGH**，`catalog_exact`，mark=`Zibblefrax`，catalogVersion=`demo-fictional-2026-11-f1deea4df852` |
| 04 故意错误的 Amazon 变体（child `parent_sku=TEE-X`） | `/api/v1/variation-checks` | 200 | 含 `parent_child_structure` / `child_parent_sku_mismatch` 等 WARNING |
| 04b 配套 Amazon listing（给 `/checks`） | `/api/v1/checks` | 200 | `title_repeated_words`、`prohibited_content` 等 WARNING |

01b 的「0 findings」说明的是补全之后能过这一条规则，不能说明「干净样例会被判干净」。以上只说明接口按这些输入**返回了什么**；**不能**据此说规则或商标阈值在真实数据上准不准。DEMO 目录 README 自己也写了：里面的词是编的，偶然像真商标也有可能。

## 5. MCP（本机，无模型）

- stdio 手写 JSON-RPC 帧没对齐，initialize 读到空，进程侧 broken pipe（[run-mcp-min.txt](evidence/13-listing-guard/run-mcp-min.txt)，n=1）——**不算** MCP 验收失败结论，只说明我们的客户端帧不对。
- 改用文档允许的本机 HTTP：`LISTING_GUARD_MCP_TRANSPORT=http` 监听 `127.0.0.1:8765/mcp`（n=1）。`initialize` 200；`tools/list` 得到 6 个工具：`check_listing`、`check_trademark`、`check_variations`、`screen_personalization`、`get_limits`、`get_usage`。对 01b 调 `check_listing` → findings=[]、`cached=true`，checkId `d9ac0055…` 和 createdAt 与 REST 01b 完全一样（[run-mcp-http.txt](evidence/13-listing-guard/run-mcp-http.txt)、[responses/01b-clean-checks.txt](evidence/13-listing-guard/responses/01b-clean-checks.txt)，n=1）。MCP 只验证了能转发到 API、能拿回结果，这次是缓存命中，不是重新检查。未接任何外部 Agent / 模型。

## 没测的

- 没有 `docker compose up --build`（Docker 守护进程起不来）。
- 没有 embedding / ingest / 政策检索 / Ollama / Google API。
- 没有 USPTO 真数据转换，没有真实商标库；只用了仓库自带虚构 DEMO。
- 没有开 console、没有 SMTP、没有 plans 计费路径的完整验收（`PLANS_ENABLED` 保持 false）。
- 没有测准确率，没有在真实 Etsy/Amazon 数据上评估；没有发帖、没有联系作者、没有开 issue。
- stdio MCP 未用官方客户端跑通；HTTP 传输只做了最小 tools/list + 一次 check_listing。
