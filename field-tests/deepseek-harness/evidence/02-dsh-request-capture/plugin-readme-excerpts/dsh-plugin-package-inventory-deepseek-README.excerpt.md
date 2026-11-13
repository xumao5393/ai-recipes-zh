# excerpt from /workspace/fourday-20261109/deepseek-harness/sandbox/node_modules/@deepseek-ai/dsh-plugin-package-inventory-deepseek/README.md (package version 0.2.2-rc.1)
# path relative to sandbox: node_modules/@deepseek-ai/dsh-plugin-package-inventory-deepseek/README.md

---
description: "Active Loader package inventory metadata for deployments sending official DeepSeek requests."
kind: "package-reference"
---

# @deepseek-ai/dsh-plugin-package-inventory-deepseek

English | [中文](README.zh.md)

## Summary

Best-effort active Loader-backed plugin package inventory for official DeepSeek LLM API requests. This function plugin injects the Loader, live Agent registry, and `ctx.deepseekLlmApiExtensions`, then owns the `dsh_plugin_packages` field. Enable it when the official API needs the active package list for request diagnostics.

## Table of Contents

- [Configuration](#configuration)
- [Collection](#collection)
- [Model Experience](#model-experience)
- [Known Limitations and Deferred Work](#known-limitations-and-deferred-work)
- [Dev Note](#dev-note)

-----

<a id="configuration"></a>
## Configuration

| Key | Default | Meaning |
|---|---:|---|
| `enabled` | `true` | Register the `dsh_plugin_packages` contribution. Set it to `false` to omit package metadata. |

Shipped profiles use the default, so every official DeepSeek request carries the package inventory when preparation succeeds.

<a id="collection"></a>
## Collection

Every request re-reads active non-group entries from the host Loader tree. When optional `ctx.agentPresets` is present and `sessionId` resolves to a live Agent joined to a standing preset, that preset's separate Loader tree joins the same collection; deployments without the service report the host tree only. Entries are included only while their root fiber is `ACTIVE` and their effective Loader state is enabled.

At activation, the plugin samples the optional `ctx.pluginPackages` service. Shipped app boot mounts that service before profile Loader entries, so bare package and package-subpath identities use the same authoritative runtime resolution as their imports, including its misses, without requiring a `./package.json` export. If the service is absent, the plugin retains native Node package-search lookup for its lifetime and does not switch an existing inventory when a resolver mounts later. A low-level embedder that wants runtime resolution identities must therefore mount `PluginPackages` before both the Loader entries and this plugin.

Each ordinary entry uses its owning Loader tree base. A standing preset's root entries use the harness base, matching the preset Loader's deliberate bare-package override; nested includes retain their own bases. Relative and absolute modules walk to their nearest manifest; manifests without a non-blank string `name` are omitted. A missing or invalid `version` produces a name-only entry, regardless of `private`. A nested directory with its own manifest does not inherit its parent's identity. Package resolution, manifest reading, and JSON parsing failures omit only that entry and log one warning per module; inventory metadata does not block model requests. Entries are deduplicated by name and optional version and sorted with a locale-independent comparison; name-only entries sort before same-name versioned entries, and different versions remain separate.
