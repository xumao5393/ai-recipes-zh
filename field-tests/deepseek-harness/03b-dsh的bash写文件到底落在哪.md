# 03b · dsh 的 bash 写 `/tmp` 到底落在哪（实测）

状态：已实测（2026-11-09 14:54–14:57 EST）。证据：`evidence/03b-tmp-write-where/`（n=1，除非另标）。  
承接 #03 F.3：工具显示写 `/tmp` 成功，宿主机 `/tmp` 找不到。

## 方法
- 本地 Anthropic SSE 回放（`replay_server_03b.py`）：第 1 次 `bash` 写入唯一标记并 `sleep 12`；收到 `tool_result` 后再发第 2 次 `bash` 读回同一路径；然后结束。
- `dsh headless --json --permission-mode workspace-write --approval-policy never`，`DEEPSEEK_BASE_URL`→本机回放，`HOME=/tmp/dshhome-03b`。
- 宿主机并行 `host_watch.py`：抽样 `/proc/<pid>/cmdline`、`ns/mnt`、`mountinfo`（仅 `/tmp` 行）、`root/tmp` 是否出现标记文件；**只存环境变量名，不存值**。
- `strace`：**未跑成**（系统无 strace；apt/deb 源 500/404）。见 `strace/UNAVAILABLE.txt`。改用 `/proc` + cmdline。
- 包内文档/实现只引用路径与行号（`pkg-notes/citations.txt`），不拷贝构建产物。

标记：`dsh03b-20261109-145405-59568077`（文件名因脚本写成 `/tmp/dsh03b-$MARK.txt` 而出现双前缀，仍唯一）。

## 实测结果

### 1. 命令执行期间文件在哪（n=1）
- 工具结果（第 1 次 bash）显示：
  - `HOST_PID=2`（**私有 PID 命名空间**内的 PID）
  - `NS_MNT=mnt:[4026532337]`（宿主机本次为 `mnt:[4026532322]`，**不同**）
  - `df /tmp` → **tmpfs**；`mountinfo` 行：`tmpfs` 挂在 `/tmp`
  - `ls` 显示文件存在，内容为标记字符串
- 宿主机侧在进程存活时，通过 `/proc/<pid>/root/tmp/` **读到同名文件**（32 字节，内容=标记）。见 `host/key-facts.json`。
- 宿主机自己的 `/tmp`：**始终没有**该文件（监视期间与结束后的 `after-search.txt`）。

### 2. 是怎么拉起的（n=1，cmdline 观测）
相关进程链（摘自 `host/host-watch.cleaned.json`）：
1. `bwrap --ro-bind / / --dev /dev --unshare-pid --proc /proc --die-with-parent --tmpfs /tmp --bind <workdir> <workdir> -- bash -c ...`
2. 子进程 `bash -c ...`（与父 bwrap **同一**非宿主机 mount ns）

未观察到 `firejail` / `landlock-run` 作为本命令的直接 runner（本轮 cmdline 是 **bwrap**）。  
`strace` 缺失，故 clone/unshare/mount 的系统调用序列 **未用 strace 验证**（标：未测）。

### 3. 退出后还在吗；下一命令能否读到（n=1）
- 第 1 次 bash 结束后，宿主机仍找不到文件。
- **同一 headless 会话**内第 2 次 bash（新的一次 confine）：
  - `ls`/`cat` 同一路径 → **No such file**
  - `NS_MNT=mnt:[4026532334]`（与第 1 次的 `…2337` **不同**）
  - 仍是 `HOST_PID=2`
- 结论（仅本样本，本机 **bwrap** 后端）：`/tmp` 写入落在该次调用的 bwrap 临时 tmpfs 上；调用结束即消失；**不会**留在宿主机 `/tmp`，也**不能**被同会话下一次 bash 看到。Landlock 后端按 README 可能不同（未测）。

### 4. 与已安装包描述对照（引用，不是独立实测）
- `@deepseek-ai/dsh-sandbox-local/lib/index.js` **L35**：`workspace-write` 时 `args.push("--tmpfs", "/tmp")`。
- 同文件 **L176**：Linux 链 `["bwrap", "landlock"]`（先 bwrap）。
- `@deepseek-ai/dsh-bash-sandbox/README.md` **L39**：`workspace-write` 下 `/tmp` 在 bwrap 上为 ephemeral。  
以上为包内文字/源码；本轮实测与「bwrap + `--tmpfs /tmp`」一致。

## 给普通人的结论
- 在 **`workspace-write` 模式**下（本轮显式传了 `--permission-mode workspace-write`），bash 写 `/tmp/某文件` **看起来成功**，其实写在 **沙箱私有的 tmpfs `/tmp`**，不是你在终端里看到的宿主机 `/tmp`。
- **本机选中的后端是 bwrap**（cmdline 实测）。`dsh-bash-sandbox/README.md` L39 写明：bwrap 下 `/tmp` 是临时的；**若落到 Landlock 后端，README 说会写进宿主机 `/tmp`（本轮未测）**。因此「不会留在宿主机 `/tmp`」只对 bwrap 样本成立。
- 同一会话里两次 bash 调用观察到的是**不同的 mount 命名空间**（n=1 会话、2 次调用）；**不要**指望跨两次 bash 用 `/tmp` 传文件。要持久就写工作区路径。

## 未做
- 未跑成 `strace`；未测 `danger-full-access`、Landlock 后端、macOS Seatbelt。
- 未测网络命名空间是否隔离（文档称文件隔离为主）。
- 全盘 `find /` 未做（权限与耗时）；只查了 `/tmp`、`/var/tmp`、证据树与 `/proc/<pid>/root/tmp`。
