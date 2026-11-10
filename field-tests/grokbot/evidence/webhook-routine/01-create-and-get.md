> **进行中、未测通**：本篇是过程记录。webhook 实际触发和延迟都还没测，不能当成“webhook 已测过”或“webhook 可用”。

# webhook 测试 routine：创建与查看（文字描述）
记录者：实测员。时间：2026-11-09 EST。原始工具输出存档在仓库外，不入库。

- 14:38 EST，实测员建了 routine “实测-webhook触发测试（测完删除）”，触发方式选 webhook。创建结果只显示了 routine 名称、所在目录和“webhook 触发时运行”，没有 webhook URL，也没有密钥。
- 14:38 EST 查看这个 routine 的详情，看到名称、启用状态、触发类型 `{"type":"webhook"}` 和保存的提示词，同样没有 URL 和密钥。
- 14:39 EST bot 侧拿到的 routine 状态里，只有指向主人 App 侧边栏中 URL、key、Authorization header 三个字段的入口链接，链接里不含这些值。当时状态是“从未运行”。
- 14:41 EST 按审核意见改了提示词：Authorization、Cookie，以及名字里带 key/token/secret/auth 的请求头，只记“有/无”和长度，不写值。这次改动是在第一次触发之前做的。

以上都是本次在 bot 侧看到的情况，不代表产品规则。本目录不存放 webhook URL 和密钥。
