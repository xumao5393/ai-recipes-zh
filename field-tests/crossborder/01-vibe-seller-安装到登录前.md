# 01 · vibe-seller 安装到登录前（实测）

状态：已实测（2026-11-09 14:39–14:51 EST）。环境：Linux 盒子，Python 3.13.5，uv 0.13.7，Node v24.22.1，Google Chrome 156.0.8078.47；无模型 Key、不注册、不填店铺/紫鸟账号。证据：`evidence/01-vibe-seller-install/`（含敏感字段的原件未入库，移动记录见 `evidence/01-vibe-seller-install/MASKING.txt`）。n=1。

## 版本与许可证
- 仓库：[zpoint/vibe-seller](https://github.com/zpoint/vibe-seller)，许可证 Apache-2.0（`LICENSE.txt`）。
- PyPI 稳定版 `vibe-seller==0.2.0`（`pypi-meta.txt`）；GitHub release 标签 `v0.2.0`。Windows 安装包 `VibeSeller-Setup.exe` 大小 **413,477,438 字节**（`release-v0.2.0-assets-sizes.txt`，GitHub Releases API）；本轮未用该安装包。
- 实测当天 `main` 最新提交 `7693f9a7cff956210f62ff2baf707f937d2943c6`（UTC 2026-11-09 10:22:31，合东五区 05:22:31 EST；`repo-meta.txt`）。安装到的 CLI 版本：`vibe-seller 0.2.0`（`version.txt`）。

## 官方 Linux 安装怎么走
README 写的是：

```bash
curl -sSL https://raw.githubusercontent.com/zpoint/vibe-seller/main/install.sh | bash
vibe-seller start
```

打开 `http://localhost:7777`。默认**不需要登录**（官方 README @7693f9a L248、L579；摘录见 `readme-excerpts-7693f9a.txt`）；首次真正要填的是「设置 → AI」的模型 Key（官方 README @7693f9a L250–L252；同上摘录），以及（可选）紫鸟账号 / 店铺绑定。

本轮在隔离 `HOME=<sandbox>/home` 下跑同一份 `install.sh`（`install.sh`、`install-cmd.txt`），等价于官方 `curl | bash`。

## 失败与绕法（都有日志）
1. **fail1**：`install.sh` 用 apt 装 `lsof`，debian 源 `InRelease` 返回 500 / not signed，退出（`fail1-note.txt`、`fail1-apt-lsof-*.txt`）。
   - **workaround1**：直接下载 `lsof_4.99.4+dfsg-2_amd64.deb`，解出二进制放到 `$HOME/.local/bin/lsof`（`workaround1-*.txt`）。
2. **fail2**：同样方式装 `sqlite3` 再次撞 apt 500（`fail2-note.txt`）。
   - **workaround2**：下载 `sqlite3_3.46.1-7+deb13u2_amd64.deb`（及 lib），解出 `sqlite3` 3.46.1（`workaround2-*.txt`）。
3. **fail3 / 半成功**：绕过前两步后，`uv tool install vibe-seller` 成功装上 0.2.0（128 包），项目本地也装好了 `@anthropic-ai/claude-code`；但随后 `playwright install --with-deps chromium` 又去 apt 装系统依赖，再次 500，整段 `install.sh` 以 exit 1 结束（`install3-time.txt`：`elapsed_sec=13`；`fail3-*.txt`）。此时 `vibe-seller` 命令已经可用。
   - **workaround3**：对工具目录里的 playwright 执行 `playwright install chromium`（**不加** `--with-deps`）。Playwright 进度条显示下载 Chrome for Testing **191.1 MiB**、Chrome Headless Shell **120 MiB**、FFmpeg **2.2 MiB**（`workaround3-playwright-stdout.txt`）；exit 0，`elapsed_sec=6`（`workaround3-playwright-time.txt`）。本机已有 Google Chrome 与相关系统库。

未试 docker（环境无 docker）。未走 `--dev` 源码安装（官方 PyPI 路径在绕过 apt 后已通）。

## 体积（`du -sb` / `du -sh`，`du-diagnose-20261109.txt` / `du-exact-corrected-20261109.txt`）
| 路径 | 字节（`du -sb`） | `du -sh` |
|---|---:|---|
| uv tool `vibe-seller` | 741,935,865 | 741M |
| Playwright 浏览器缓存合计 | 711,303,470 | 681M |
| └ chromium-1248（解压后） | 420,921,737 | 403M |
| └ chromium_headless_shell-1248 | 285,084,594 | 273M |
| └ ffmpeg-1013 | 5,296,998 | 5.1M |
| `~/.vibe-seller` | 402,933,377 | 387M |
| └ 其中 `node_modules`（本地 Claude Code） | 342,114,174 | 327M |
| 隔离 HOME 合计 | 2,260,375,218 | 2.2G |

装完当时另有一份 `final-summary.txt`（14:45:27 EST）：tool 741M、playwright 681M、`~/.vibe-seller` 379M、`node_modules` 327M、HOME 2.2G（与上表同量级；随后 agent venv 等使 `.vibe-seller` 变为 387M）。

## 启动与首页
- `vibe-seller start` → 输出 `running on http://0.0.0.0:7777`，`elapsed_sec=3`，exit 0（`start-stdout.txt`、`start-time.txt`）。
- `GET /` → 200，HTML **465** 字节，标题 `Vibe Seller`（SPA 壳；`curl-home.txt`、`homepage.html`）。
- `GET /api/health` → `{"status":"ok","version":"0.2.0"}`；`GET /api/auth/status` → `{"auth_required":false}`（`api-health.json`、`api-auth-status.json`）。
- 默认管理员可见：`/api/auth/me` 返回 username `admin`、本地占位邮箱（打码为 `<local_email>`；`api-auth-me.masked.json`）。
- headless Chrome 曾截到主界面（原 PNG 因侧栏含安装 ID 前缀已归档，见 `homepage-screenshot.NOTE.txt`）。界面为主控台：侧栏「+ New Store」、Tasks、设置齿轮、用户 `admin`；**不是登录页**。

## 安全观察
**「默认 `vibe-seller start` 监听 `0.0.0.0:7777`，且 `auth_required=false`」是本版本 0.2.0 在本机默认启动下观察到的行为，n=1。**

证据：
- 默认启动输出 `running on http://0.0.0.0:7777`（`start-stdout.txt`）。
- `GET /api/auth/status` → `{"auth_required":false}`（`api-auth-status.json`）；设置里 `auth_required` 为 `"false"`（`api-settings.masked.json`）。
- 实测员已于 2026-11-09 14:47–14:48 EST 停掉默认服务（`stop-service-20261109.txt`）。

### 绑定地址（CLI 有选项，已复测）
- `vibe-seller start --help`：`--host HOST`，说明为 `Host interface to bind (default: 0.0.0.0)`（`cli-help-20261109.txt`）。
- 复测：`vibe-seller start --host 127.0.0.1 --port 7777` → 输出 `running on http://127.0.0.1:7777`；`ss` 显示 `127.0.0.1:7777`；`curl http://127.0.0.1:7777/api/health` 返回 200；随即 `vibe-seller stop --port 7777`（`host-127-bind-test-20261109.masked.txt`）。

### 开启认证（文档有、本包 CLI 无）
- 官方 README 写明可用 `vibe-seller reset-auth enable|disable|status|password` 开关登录页（@7693f9a L586、L591、L596–L597；`readme-excerpts-7693f9a.txt`）。
- 本轮安装的 **0.2.0** 打包入口 `vibe-seller -h` 仅有 `start` / `stop` / `upgrade`；执行 `vibe-seller reset-auth status` 报 `invalid choice: 'reset-auth'`（`cli-help-20261109.txt`、`auth-options-check-20261109.txt`）。未改设置、未启认证做持久化测试。源码侧设置键名仍为 `auth_required`（`auth-host-source-hits.txt`）。

服务未保持常开；收尾后 7777/9222 无监听（`residual-check-20261109.txt`）。

## Chrome CDP
- 本机先手动起 `--remote-debugging-port=9222` 可通：`/json/version` 返回 `Chrome/156.0.8078.47`（`cdp-json-version.masked.txt`）。
- 但该端口正是 vibe-seller 默认占用的 CDP 口；占用时 `POST /api/browser/web/start` 报 `address already in use`（`browser-web-start-try.txt`）。
- 释放 9222 后，`POST /api/browser/web/start` → `{"ok":true}`；随后本机 CDP 显示 Playwright 拉起的 `Chrome/156.0.8078.4`（`browser-web-start2-body.masked.txt`、`cdp-after-vibe-start.masked.txt`）。
- 另：仅填店名、后端默认 `chrome` 即可 `POST /api/stores` 建店（无紫鸟、无平台账号）；`POST /api/stores/<id>/browser/start` 也返回 `{"ok":true}`（`store-create-try.masked.txt`、`store-browser-start-body.masked.txt`）。OpenAPI 里 `StoreCreate` 唯一必填是 `name`（`openapi-StoreCreate.txt`）。

## 模型 Key 与店铺账号卡在哪（到此停）
- **网页登录**：默认关闭（实测 `auth_required=false`；官方 README 亦写「默认不需要登录」@7693f9a L579，`readme-excerpts-7693f9a.txt`）。可选功能，本轮未打开。
- **模型 Key**：`GET /api/profiles` 只有系统默认 `Claude`，`env` 为空（`api-profiles.json`）。`POST /api/profiles/validate` 在未配端点/Key 时返回 `{"ok":true,"code":"no_endpoint",...}`（`profile-validate-try.txt`）。预设列表含 DeepSeek / Kimi / MiniMax / GLM / Qwen 等 9 组（`api-profiles-presets-summary.txt`）。**按 README（@7693f9a L252；`readme-excerpts-7693f9a.txt`），真正跑任务前要在「设置 → AI」粘 Key；我们没有 Key，不伪造，停在这一步之前。**
- **紫鸟账号**：`ZiniaoAccountCreate` 必填 `name/company/username/password`（`openapi-StoreCreate.txt`）。`GET /api/ziniao-accounts` 为空数组。**不填真实账号，停。**
- **店铺平台登录**：Chrome 后端建店不要求当场填卖家后台账号（本轮 OpenAPI/`POST /api/stores` 实测）。本轮没测店铺登录流程。

## 给普通人的结论
- Linux 上官方 `install.sh` 在这台盒子上会被**坏掉的 apt 源**拦住（`lsof`、`sqlite3`、Playwright `--with-deps` 三处；`fail1/2/3-*.txt`）。这是**本机 debian 镜像/InRelease 500** 的问题，不是 vibe-seller 安装脚本本身的逻辑错误。**推测，未测**：换正常的 apt 源可能不会碰到这三处失败。本轮用 deb 解包 + 去掉 Playwright `--with-deps` 后，**可以装好并启动**。
- 本轮 0.2.0 在本机默认启动后直接进主界面（免登录），且绑 `0.0.0.0`，n=1（见「安全观察」）。需要只听本机时用 `--host 127.0.0.1`。
- Chrome CDP（9222）本轮实测可被服务拉起。
- 再往下就需要自备模型 Key；紫鸟还要公司名/用户名/密码。这些本轮按规矩不测。

## 证据索引
- 公开证据：`evidence/01-vibe-seller-install/`（清单 `FILES-final.txt`；官方 README 摘录 `readme-excerpts-7693f9a.txt`）
- 含敏感字段的原件未入库，移动记录见 `evidence/01-vibe-seller-install/MASKING.txt`。
- 证据原文写入后不改写；更正与打码另存新文件。
