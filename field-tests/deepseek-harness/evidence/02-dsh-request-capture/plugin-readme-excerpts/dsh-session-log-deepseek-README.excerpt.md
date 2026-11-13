# excerpt from /workspace/fourday-20261109/deepseek-harness/sandbox/node_modules/@deepseek-ai/dsh-session-log-deepseek/README.md (package version 0.2.2-rc.1)
# path relative to sandbox: node_modules/@deepseek-ai/dsh-session-log-deepseek/README.md

---
description: "Incremental canonical session-log upload for deployments enabling official DeepSeek request metadata."
kind: "package-reference"
---

# @deepseek-ai/dsh-session-log-deepseek

English | [中文](README.zh.md)

## Summary

Incremental canonical session-log upload for official DeepSeek LLM API requests. This function plugin injects `ctx.sessions` and `ctx.deepseekLlmApiExtensions`, then owns the `dsh_session_log` request field and the durable `session-log-deepseek/delivery-accepted` event from which it derives the acceptance watermark. Disable it only when the official API must not receive a Session-log suffix.

## Table of Contents

- [Configuration](#configuration)
- [Request field](#request-field)
- [Upload exclusions](#upload-exclusions)
- [Acceptance and retry](#acceptance-and-retry)
- [Model Experience](#model-experience)
