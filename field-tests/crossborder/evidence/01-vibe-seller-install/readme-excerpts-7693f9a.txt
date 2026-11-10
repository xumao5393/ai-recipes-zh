# README excerpts for claims in 01-vibe-seller-安装到登录前.md
fetched: raw.githubusercontent.com/zpoint/vibe-seller/7693f9a7cff956210f62ff2baf707f937d2943c6/README.md
fetched_at_est: 2026-11-09 14:53 EST
full_file_sha256: 984ed0908b066d086bc2c20a5c1ef4f843ecc3ffff41a6e84c6b3330c68dfe6a
full_file_bytes: 35640
note: 本地邮箱等敏感字样若出现在邻近行，摘录时刻意跳过，不写入本证据文件。

### claim-A 默认不需要登录（安装成功提示）
source: README.md @ 7693f9a7cff956210f62ff2baf707f937d2943c6
file_sha256: 984ed0908b066d086bc2c20a5c1ef4f843ecc3ffff41a6e84c6b3330c68dfe6a
bytes: 35640
github_lines: https://github.com/zpoint/vibe-seller/blob/7693f9a7cff956210f62ff2baf707f937d2943c6/README.md#L248-L248
--- begin excerpt ---
248|看到 Vibe Seller 首页就是装成功了（默认不需要登录）。
--- end excerpt ---

### claim-A 默认不需要登录（FAQ 完整表述；未收录含本地邮箱的相邻行）
source: README.md @ 7693f9a7cff956210f62ff2baf707f937d2943c6
file_sha256: 984ed0908b066d086bc2c20a5c1ef4f843ecc3ffff41a6e84c6b3330c68dfe6a
bytes: 35640
github_lines: https://github.com/zpoint/vibe-seller/blob/7693f9a7cff956210f62ff2baf707f937d2943c6/README.md#L579-L580
--- begin excerpt ---
579|**默认不需要登录。** 全新装好打开就是主界面——登录是可选功能，只有在「设置 → 账号」里手动打开才生效。所以如果你看到登录页，说明这台机器上有人（多半是给你装机器的同事）主动开了登录。
580|
--- end excerpt ---

### claim-B 填 LLM Key 在「设置 → AI」
source: README.md @ 7693f9a7cff956210f62ff2baf707f937d2943c6
file_sha256: 984ed0908b066d086bc2c20a5c1ef4f843ecc3ffff41a6e84c6b3330c68dfe6a
bytes: 35640
github_lines: https://github.com/zpoint/vibe-seller/blob/7693f9a7cff956210f62ff2baf707f937d2943c6/README.md#L250-L252
--- begin excerpt ---
250|### 5. 填 LLM Key
251|
252|`设置 → AI` → 选一个供应商（[DeepSeek](docs/llm-keys.md#deepseek) 支持按 token 付费、[Claude](docs/llm-keys.md#claude) 上限高、[Kimi](docs/llm-keys.md#kimi)/[MiniMax](docs/llm-keys.md#minimax)/[GLM](docs/llm-keys.md#智谱-glm)/[通义](docs/llm-keys.md#通义千问阿里云百炼)/[MiMo](docs/llm-keys.md#小米-mimo) 都行），粘 API Key 保存。Key 本地加密存储。
--- end excerpt ---

### claim-C reset-auth status
source: README.md @ 7693f9a7cff956210f62ff2baf707f937d2943c6
file_sha256: 984ed0908b066d086bc2c20a5c1ef4f843ecc3ffff41a6e84c6b3330c68dfe6a
bytes: 35640
github_lines: https://github.com/zpoint/vibe-seller/blob/7693f9a7cff956210f62ff2baf707f937d2943c6/README.md#L584-L589
--- begin excerpt ---
584|
585|```bash
586|vibe-seller reset-auth status
587|```
588|
589|它会告诉你：现在要不要登录、默认密码还管不管用、哪些账号能登录、哪个是默认管理员。
--- end excerpt ---

### claim-C reset-auth password（首句）
source: README.md @ 7693f9a7cff956210f62ff2baf707f937d2943c6
file_sha256: 984ed0908b066d086bc2c20a5c1ef4f843ecc3ffff41a6e84c6b3330c68dfe6a
bytes: 35640
github_lines: https://github.com/zpoint/vibe-seller/blob/7693f9a7cff956210f62ff2baf707f937d2943c6/README.md#L591-L591
--- begin excerpt ---
591|忘了密码就用 `vibe-seller reset-auth password` 重置——不带参数时会交互询问新密码，重置的是「默认管理员」账号（它后来改成什么名字都算数）；命令直接改数据库，服务不用重启，正在跑的任务不会断。注意**重置密码不会把已登录的浏览器踢下线**：登录靠的是浏览器里的 JWT cookie（24 小时滚动有效），重置后旧会话照样能用。要强制所有人重新登录，得停服务 → 删 `~/.vibe-seller/data/jwt_secret` → 再启动（用 `JWT_SECRET` 环境变量固定密钥的装法，要改的是那个变量）。
--- end excerpt ---

### claim-C reset-auth disable / enable
source: README.md @ 7693f9a7cff956210f62ff2baf707f937d2943c6
file_sha256: 984ed0908b066d086bc2c20a5c1ef4f843ecc3ffff41a6e84c6b3330c68dfe6a
bytes: 35640
github_lines: https://github.com/zpoint/vibe-seller/blob/7693f9a7cff956210f62ff2baf707f937d2943c6/README.md#L593-L598
--- begin excerpt ---
593|**不想要登录页**（应急用）：
594|
595|```bash
596|vibe-seller reset-auth disable    # 关掉登录页
597|vibe-seller reset-auth enable     # 想开回来的时候
598|```
--- end excerpt ---

