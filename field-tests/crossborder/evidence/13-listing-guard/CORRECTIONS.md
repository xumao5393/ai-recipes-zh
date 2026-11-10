# CORRECTIONS · 13-listing-guard

时间：2026-11-09 20:44 EST（America/New_York）。本文件记录对证据原文的更正，以及 Kumo 的认定与新规。`postgres-install.txt`、`source-review.txt` 的原件正文未改，只在文末追加更正段。

## 1. “curl to Fastly IP” 不是直连 IP

`postgres-install.txt` 第 2 行原文：“curl to Fastly IP works”。`source-review.txt` 原文：“curl to Fastly (DNS not 198.18) worked for .deb download”。听上去像直连 IP，跟 03 那次绕法是同一类。

更正：实际命令是 `GET https://deb.debian.org/...`（见 `postgres-install.txt` 的 `download_start` 段），走域名和系统 DNS，没有指定 IP，也没有用 `--resolve` 或直连 IP。是 HTTPS 按域名下载，没有指定 IP。系统 DNS 把 `deb.debian.org` 解析到 Fastly 地址（见 `dns-check.txt`，非 198.18），但不能把“解析到 Fastly”写成“curl 到 Fastly IP”。

原件未改。追加更正前：

| 文件 | 字节数 N | sha256 |
|---|---|---|
| postgres-install.txt | 24432 | 17ccff9e414ae23506efc9aa2153d5d2d607d839c1e85763b4043dc397f65818 |
| source-review.txt | 1860 | 3875848b00670f2c6d064ea6a8530a76c5fe6303d82d7207114946caba260c11 |

可用 `head -c 24432 postgres-install.txt | sha256sum`、`head -c 1860 source-review.txt | sha256sum` 复现。改前原件在 `internal-archive/13-listing-guard/before-r1-review/evidence/`。

## 2. Kumo 认定（2026-11-09 20:36 EST）

apt 走 http 80 端口、到 198.18.0.1 时 HTTP 返回 500，哪一层返回的没查清；随后改用 HTTPS 按域名下载。

**Kumo 认定：这不算绕开网络控制。** 未使用任何绕行手段。

## 3. 新规（自本次起）

以后遇到 403、拦截页或其他明确拒绝，就停下，不换协议重试。

本次 apt 返回的是 HTTP 500（哪一层返回的没查清），不是 403、拦截页或明确拒绝，所以改用 HTTPS 按域名下载这一步按上面第 2 条认定处理；这条新规约束的是此后再遇到 403、拦截页或明确拒绝的情况。
