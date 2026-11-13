# captured/ 请求归属（补记，2026-11-09 14:43 EST）

本目录在同一次回放服务生命周期内连续写入，**混有两次 headless 运行**：

| 文件 | 归属 | 说明 |
|---|---|---|
| req-01 / resp-01 | **Run A** | bash `echo hi` + `--permission-mode danger-full-access --approval-policy never`（见 `../runA.txt`） |
| req-02 / resp-02 | **Run A** | 会话标题请求 |
| req-03 / resp-03 | **Run A** | 带 tool_result 的续轮 |
| req-04 / resp-04 | **Run B** | bash `echo hi`，默认权限（见 `../runB.txt`） |
| req-05 / resp-05 | **Run B** | 会话标题请求 |
| req-06 / resp-06 | **Run B** | 带 tool_result 的续轮 |

未拆目录（避免移动已有证据原文）；以后每次抓包用新子目录。
