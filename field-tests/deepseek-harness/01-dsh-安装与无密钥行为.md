# 01 · 官方 dsh 安装与无密钥时的行为（实测）

状态：已实测（2026-11-09 14:06 EST 初测；14:32–14:34 EST 按审核补证据）。环境：Linux 盒子，Node v24.22.1，npm 11.21.1。证据：`evidence/01-dsh-install/`。

## 实测结果
- 包名 `@deepseek-ai/dsh`。查询时间 2026-11-09 14:32:55 EST：`npm view @deepseek-ai/dsh version engines dist-tags` 显示 `version = 0.2.2-rc.1`，`engines.node = >=24.9.0`，`dist-tags.latest = 0.2.2-rc.1`（同时 `next` 也指向 `0.2.2-rc.1`）（`npm-view.txt`）。
- 本地装进空目录：先 `npm init -y`，再 `npm install @deepseek-ai/dsh@0.2.2-rc.1`。安装日志：`added 654 packages in 28s`，计时 `real 0m27.833s`，退出码 0（`npm-install.txt`）。
  - 装完后 `du -sh node_modules` → `919M`；`du -sb` 表观字节 745,397,549（745397549/1024/1024 = 710.87 MiB）。表观字节小于磁盘占用，推测是因为小文件多（`node_modules-du.txt`，2026-11-09 14:32:51 EST）。
  - npm 11 默认没跑 5 个包的安装脚本（含 `node-pty`、`koffi`），只给了警告（`npm-install.txt`）。本轮 `--version`、`--help`、`headless` 都能启动；交互终端（tui）是否受影响还没测。
  - 坑（已复现）：空目录里不先 `npm init -y`、直接 `npm install @deepseek-ai/dsh@0.2.2-rc.1`，报 `npm error Tracker "idealTree" already exists`，退出码 1（`idealTree-error.txt`；完整 npm debug 见 `idealTree-npm-debug.log`，2026-11-09 14:33:12 EST）。建好 `package.json` 再装就过了。
- `dsh --version` 输出 `0.2.2-rc.1`；`dsh --help` 显示它其实是“按 profile 启动插件栈”的启动器，常用 profile 有 `web`、`tui`、`headless`（`dsh-help.txt`）。
- `dsh headless "任务"`：跑一个任务、答案进 stdout 后退出，支持 `--json` 事件流、`--session-id` 续跑、`--permission-mode`（`headless-help.txt`）。
- 没有 `DEEPSEEK_API_KEY` 时，`dsh headless "say hi"` 报错 `MISSING_CREDENTIAL ... export DEEPSEEK_API_KEY`，退出码 1（`headless-nokey.txt`）。补测计时（bash `TIMEFORMAT`，GNU `time` 未安装；`HOME` 隔离；n=3，2026-11-09 14:32:46 EST）：real = 1.348 s / 1.513 s / 1.523 s，均为 exit=1（`headless-nokey-timing.txt`）。
- 首次运行会在 `~/.dsh/` 下创建：`.anonymous-user-id`、`profiles/`、`sessions/`、`storages/`。证据：全新临时 `HOME` 运行前后 `ls -la`（`first-run-dsh-home.txt`，2026-11-09 14:33 EST）。无 key 的第一次 `headless` 就会建出 `sessions/`（带工作区目录名派生的子目录），不只是抓包/有 key 时才有。

## 从配置里读到的默认值（`--dump-config`，读的是配置不是实测行为）
- 默认模型 `provider: deepseek-official`，`model: deepseek-flash`。
- 遥测插件 `session-telemetry-otel` 默认模式来自 `process.env.DSH_TELEMETRY_MODE || 'FEEDBACK_ONLY'`，上报地址 `dsh-otel-collector.deepseeksvc.com`（`headless-dump-config.txt`）。合法取值只有 `FEEDBACK_ONLY` / `DISABLED`；写成 `off` 会校验失败、插件不激活（实测见 `evidence/02-dsh-request-capture/run.txt`，该证据随 02 复审后入库）。
- 有 `repeat-tool-reminder`：同一工具调用重复到 3/5/8 次时插提醒。它管的是工具重复，不等于社区反馈的“思考死循环”熔断，这一点还没实测。

## 给普通人的结论
- 装起来不难，但 `node_modules` 磁盘占用 `919M`（`du -sh`），Node 必须 24.9 以上。
- 没有 key 也能先装好、看帮助、导出配置，确认环境没问题再去充值。
