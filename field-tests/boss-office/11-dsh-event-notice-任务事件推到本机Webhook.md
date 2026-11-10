# 11 dsh-event-notice：任务完成 / 待审批推到本机假 Webhook

**一句话结论**：这是 DeepSeek Harness 的事件通知插件（v0.5.6）。源码审查没有安装期自动脚本，也没有写死公共 ntfy 托管地址——通道 URL 默认空，空则跳过。未声明支持的 dsh 版本；按 commit 钉死执行 `dsh plugin add` 后，`dump-config` 里能看到该插件（n=1）——这只说明配置树里出现了它，**0.2.2-rc.1 运行时会不会真的加载它没测**。自带 `node --test` **55/55 通过**（n=1）。用插件 `apply()` 喂**按插件自测格式手写的**三种会话事件、真实 HTTP 打 **127.0.0.1** 假 Webhook，各收到 1 条（n=1）；载荷含会话标题与工作目录。假事件里本来就没有用户消息/模型输出，**会话正文会不会被带出去：本次没法验证**。这些手写事件与真实 dsh 发出的事件格式是否一致，也**没有验证**。没有接 ntfy/Gotify 公共服务，没有接 DeepSeek 官方地址，也没有起完整 dsh 假模型会话。

- 专题放在 **boss-office**：场景是「老板不盯屏，只在要批/要问时被叫」。行业进度表 01–10 仍留给各行业方案，本篇登记为编号 **11**，避免占 07 教育培训的号。技术上它是 DSH 插件，和 deepseek-harness 的插件实测同类，但主题归老板触达。
- 仓库：[sorchk/dsh-event-notice](https://github.com/sorchk/dsh-event-notice)，钉死 commit [`a791d4de`](https://github.com/sorchk/dsh-event-notice/commit/a791d4de6dcb933278ea602e5db3cb4affbc0ede)（2026-11-10 09:17:17 +0800 = 2026-11-09 20:17:17 EST，message：升级到 0.5.6）。查询时 0 星、0 fork（[repo-meta.txt](evidence/11-dsh-event-notice/repo-meta.txt)）。仓库很新（创建于 11-08），仍在推送。

## 1. 源码审查（[source-review.txt](evidence/11-dsh-event-notice/source-review.txt)）
- `package.json` scripts 只有 `test`；**无** preinstall/install/postinstall/prepare。
- 依赖仅 `@deepseek-ai/schemastery`；lockfile 无 hasInstallScript。
- Gotify / Webhook / ntfy 的服务器地址默认空；**未发现**写死公共 ntfy 托管地址。空地址通道跳过。
- 出网只经 `lib/notify.js` 的 `fetch`，目标是用户配置的 URL。

## 2. 版本
- Node `>=20`：本机 v24.22.1 满足（n=1）。
- **未声明** dsh 版本（[semver-result.txt](evidence/11-dsh-event-notice/semver-result.txt)）。未强装、未 allow-version。

## 3. `npm test`
- `npm ci` 后 `unshare -rn` + lo 跑 `npm test`：**55 pass / 0 fail**，约 0.36s 测试、0.50s wall（[run-npm-test.txt](evidence/11-dsh-event-notice/run-npm-test.txt)，n=1）。

## 4. 装进本机 dsh web（只验到 dump-config）
- 命令：`dsh plugin --profile web add github:sorchk/dsh-event-notice#a791d4de…`（隔离 HOME）。
- 第 1 次在断网命名空间里失败：pnpm 需要 git 拉 GitHub（exit 1）。**未**用 DoH/直连 IP 绕过。
- 第 2 次允许访问 GitHub：exit 0，1.5s；`dump-config` 见 `id: dsh-event-notice`（[run-plugin-add.txt](evidence/11-dsh-event-notice/run-plugin-add.txt)，n=1）。
- **含义限定**：「装成功」在这里只等于配置树 / `dump-config` 里出现了该插件行。没有启动 `dsh web` 或 headless 去看 0.2.2-rc.1 运行时是否真正加载、挂上事件监听。

## 5. 本机假 Webhook（真实 HTTP，n=1）
未启动完整 `dsh web` / 假模型。用插件 `apply()` + `session/event`，喂的是**按插件自带测试格式手写的对象**（与真实 dsh 运行时发出的事件是否同形：**未验证**）；**fetch 不 mock**，打本机监听端口。

| 触发（手写） | 收到 event | 标题片段 |
|---|---|---|
| `turn/end` reason=completed | `task-complete` | DSH-TEST · 任务完成 |
| `approval/asked` | `approval-required` | DSH-TEST · 需要审批 |
| `tool/call` name=ask_user_question | `question-required` | DSH-TEST · 需要回答问题 |

证据：[run-drive-events.txt](evidence/11-dsh-event-notice/run-drive-events.txt)、[drive-events-result.json](evidence/11-dsh-event-notice/drive-events-result.json)。

驱动脚本 [run_drive-events.mjs](evidence/11-dsh-event-notice/run_drive-events.mjs) 里引用的 `../src/index.js`，`src` 就是 `git clone https://github.com/sorchk/dsh-event-notice src` 拉下来、HEAD 为 `a791d4de` 的原版仓库，没改过（见 [git-clone.txt](evidence/11-dsh-event-notice/git-clone.txt)、[UPSTREAM-SHA256.txt](evidence/11-dsh-event-notice/UPSTREAM-SHA256.txt)）。照着跑时，把仓库 clone 成名为 `src` 的目录，和放脚本的目录并排。

### 载荷里实际看到的（对照证据，不是“不含会话正文”的笼统结论）
- **会话正文会不会被带出：本次没法验证。** 喂进去的假事件里本来就没有用户消息、也没有模型输出；[payload-leak-scan.txt](evidence/11-dsh-event-notice/payload-leak-scan.txt) 只扫了 “system prompt / You are” 一类标记，不能用来证明插件不会外泄正文。
- **问题原文没有进载荷：** 驱动里 `ask_user_question` 的 `arguments.question` 是「要继续吗？」，收到的 `question-required` 正文是「助手提出了问题，等待你回答」，**没有**出现「要继续吗？」。见 [drive-events-result.json](evidence/11-dsh-event-notice/drive-events-result.json) 第 3 条 `payloads[2].body`。
- **审批理由原样进了 `message`：** 驱动里 `approval/asked` 的 `reason` 是 `dangerous command needs approval`，收到的正文含「工具 需要审批：dangerous command needs approval」。见同文件 `payloads[1].body`。因此**真实使用时，审批理由里写什么，就会发到 Webhook 那边**。
- 其它扫描：无 `<workspace>`/`<home>` 绝对路径、无 DeepSeek 官方 API 主机名；含测试用工作目录 `/tmp/fake-workdir-for-test`（README 说明会带工作目录，属预期）。

## 没测的
- 未用公共 ntfy 托管服务、公共 Gotify 或任何外网 URL。
- 未起完整 dsh 会话 + 本地假模型；三种事件是手写测试对象，**未对照真实 dsh 事件 schema**。
- 未验证 0.2.2-rc.1 运行时是否真正加载该插件（只看到 `dump-config`）。
- 未测浏览器铃铛按钮、设置页「发送测试通知」、凭据存储里的真实令牌。
- 未测 Gotify / ntfy 通道的真实 HTTP（只测了 Webhook）。
- 未评估通知文案是否适合生产；0 星，无他人使用记录。
