# 04 · `dsh web` 能否在 127.0.0.1:3080 起来（实测）

状态：已实测（2026-11-09 14:34–14:35 EST；14:41–14:43 去密钥并补计时/通配；14:50 按第 6 轮复审改措辞/计时 n）。证据：`evidence/04-dsh-web/`（改正记录见 `CORRECTIONS.md`）。

## 方法
```bash
HOME=/tmp/dshhome dsh web --host 127.0.0.1 --port 3080 --no-open
```
无 `DEEPSEEK_API_KEY`。启动后 curl 首页与接口；用 stdout 打印的 `?token=` 换 cookie 再测。证据里的 token/cookie 已打码。

## 实测结果（除计时/通配补测外均为 n=1）
1. **能起来**：stdout 打印 `dsh web: http://127.0.0.1:3080/?token=<redacted>`（stderr 空）。  
   **监听就绪计时（补测 n=4，本机这几次）**：从进程启动到**首次 HTTP 响应**约 **2.18–2.55 s**（以证据秒数为准）：
   - `manual-poll.txt`：首次 **404**（空 body）**2.182982 s**
   - `listen-timing-2.txt`：首次 **404** **2.391242 s**
   - `listen-timing.txt`：首次 **404** **2.436465 s**
   - `ready-poll.txt`：先 404（2.355452 s），首次 **401**（正文 68 字节）**2.551896 s**  
   证据目录：`evidence/04-dsh-web/rerun-listen-and-wildcard/`。
2. **无令牌访问首页**：`GET /` → **401**，正文 68 字节：`dsh web authentication required; reopen the URL printed by dsh web.`（`home.body`）
3. **带 token**：先 **303** 到 `./`，并下发 `HttpOnly; SameSite=Strict` 的 `dsh-auth-…` cookie（Max-Age=2592000）；再 `GET /` → **200**，HTML **40,102** 字节（`home-jar.body`）。
4. **静态资源**（持 cookie；正文已删，仅留状态/字节/sha256，见 `asset-digests.txt`）：
   - `/assets/index-*.js` → 200，**970,770** 字节，sha256 `c7e9821660f7e0f0524cc7cb1a375a5171eebbe68e167b80d290bd2ea391286d`
   - `/assets/vendor-*.js` → 200，**741,528** 字节，sha256 `7675048a90d0419365a342c4eb81713aa8582b82a76b08ba2a8fc27160575265`
   - `/assets/index-*.css` → 200，**87,126** 字节，sha256 `ac7c3d764558542be08b2da02e208c01bf2b9953a7a94bf1fd109bdc03e2d3a4`
   - `/favicon.svg` → 200，3,634 字节；`/manifest.webmanifest` → 200，567 字节
5. **接口**：
   - 无 cookie：`/api/*` → **401** `unauthorized`
   - 持 cookie：`GET /api/file`（无 path）→ **400** `missing path`；相对 path → **400** `absolute path required`；目录 `/` → **403** `not a regular file`
   - 持 cookie：`GET /api/file?path=/.../sandbox/package.json` → **302** 再 **200**，`application/json`，正文 **306** 字节
   - 持 cookie + `Origin: http://127.0.0.1:3080`：`/api/remote.mux` → **101 Switching Protocols**
6. **默认端口 3080**；**拒绝通配地址（补测）**：
   - `dsh web --host 0.0.0.0 --port 3081 --no-open` → exit 1，stderr：`error: --host 0.0.0.0 is an unspecified (wildcard) address, which is not supported: ...`
   - `dsh web --host :: --port 3082 --no-open` → 同类错误  
   证据：`rerun-listen-and-wildcard/wildcard-host.stderr`、`wildcard-v6.stderr`。

## 给普通人的结论
- 不需要 API key 也能把 Web UI 拉起来看界面资源。
- 本地绑定 + 打印令牌换 cookie；没有令牌就 401。这套浏览器信任栅栏的**设计意图**标为**推测**（本文未引用官方文档原文）。
- 本次探测到的认证相关接口（**没有穷举**；状态码以对应 `*.headers` / `ws-remote.mux.txt` 为准）包括：
  - 无令牌 `GET /` → **401**（`home.headers`；正文 68 字节）
  - 无 cookie 探测：`path-_api.body`、`path-_api_.body`、`path-_api_health.body`、`path-_api_session.body`、`path-_api_sessions.body`、`api-file-nokookie.body` 正文均为 `unauthorized`（12 字节；这些文件无独立 headers，正文与文中“无 cookie → unauthorized”一致）
  - 持 cookie：`GET /api/file`（无 path）→ **400** `missing path`（`api-file-GET.headers`）；`OPTIONS`/`POST /api/file` → **404** `not found`；`GET /api/file?path=…/package.json` → **302** 再 **200**（`api-file-ok.headers`，正文 306 字节）
  - 持 cookie + `Origin: http://127.0.0.1:3080`：`/api/remote.mux` → **101 Switching Protocols**（`ws-remote.mux.txt`）
  - 另探测过持 cookie 的 `/api`、`/api/`、`/api/health`、`/api/plugins`、`/api/remotes`、`/api/sessions`、`/api/settings`、`/api/workspace` 等，正文为 `not found`（9 字节，`api_api*.body`；无独立 headers）

## 未做
- 未在浏览器里点完整 UI 流程，未测 TLS，未测远程访问。
