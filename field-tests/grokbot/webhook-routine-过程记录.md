> **进行中、未测通**：本篇是过程记录。webhook 实际触发和延迟都还没测，不能当成“webhook 已测过”或“webhook 可用”。

# Grok Bot：webhook 触发 routine 实测过程记录（进行中）

来源想法：创意员推荐的“闹钟停止 → iPhone 快捷指令 POST webhook → Grok Bot 晨报”（[原帖](https://x.com/Michael_Fenech_/status/2118383590446624846)，发帖时间 2026-11-05 11:43 EST，由帖子 ID 换算得出；内容是作者自述，我们没有验证）。按 Kumo 的安排，iPhone 这一步不测，只测 Grok Bot 侧的 webhook 触发。

## 已做（2026-11-09 EST）
- 14:38：实测员建了测试 routine “实测-webhook触发测试（测完删除）”，触发方式是 webhook。它被唤醒时只把时间和收到的内容写进 evidence/webhook-routine/wakes.log，不发任何消息。
- 14:38–14:39：在创建结果、routine 详情和随后的状态快照里，bot 侧都没看到 webhook URL 或密钥的值。状态快照里只出现了指向主人 App 侧边栏对应字段的链接。文字描述见 [evidence/webhook-routine/01-create-and-get.md](evidence/webhook-routine/01-create-and-get.md)，原始输出存档在仓库外，不入库。
- 14:41：在第一次触发之前改了提示词，敏感请求头只记“有/无”和长度，不写值。

## 结论（限本次）
- 本次在 bot 侧拿不到 URL，所以没有自行触发。

## 未测
- 实际触发、延迟，以及不带 key、带错 key、带对 key 三种情况的差异，全部没测，原因是缺少 URL。
- iPhone 快捷指令那一步不在本次范围内。

## 下一步
- Kumo 会把“向 Mao 要 URL”攒到之后统一去问。拿到 URL 之前不触发。
- 如果到 2026-11-13（周五）还拿不到 URL，就删掉这个测试 routine，并在这里记录删除时间和工具返回的原文。
