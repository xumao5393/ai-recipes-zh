# 手算预期（写于调用 audit_catalog 之前）

依据上游 `src/mcp_store_tools/audit.py` 的 CHECKS 规则（再加函数里追加的 `duplicate_title`），对 `catalog-nodes.json` 里 13 条虚构商品逐条对照。描述都是纯文本，经 `plain_text` 后长度不变。`oak-stool` 等完整描述为 117 个字符；`pine-hook` 的描述是 `Short.`，6 个字符。价格经 `_product` 后：单一价是 `20.00 USD`（一个数字），宽价是 `10.00 USD to 50.00 USD`（两个数字，50 > 3×10）。`long-title-banner` 的标题长度为 71（大于 70）。`SHOUTING SIGN` 含 12 个字母且全部大写。

| 检查项 | 预期命中 handle（按文件顺序） | 预期 count |
|---|---|---|
| short_description | pine-hook | 1 |
| no_image | bare-shelf | 1 |
| no_product_type | mystery-box | 1 |
| no_vendor | anonymous-mug | 1 |
| no_tags | plain-coaster | 1 |
| not_on_online_store | warehouse-lamp | 1 |
| sold_out | sold-out-tent | 1 |
| wide_price_range | typo-bundle | 1 |
| title_all_caps | shouting-sign | 1 |
| title_too_long | long-title-banner | 1 |
| duplicate_title | cedar-crate-a, cedar-crate-b | 2 |

products_checked 预期 13。Browse 一次返回全部 13 条，truncated 预期 false。
top_issues：按 count 降序，并列时保持 checks 字典的稳定排序。`duplicate_title` 的 count=2，其余命中项均为 1，故预期 `["duplicate_title", "short_description", "no_image"]`。
not_on_online_store 只有 1 条，不是全部 13 条，不应出现 store_wide 注释；notes 预期为空列表。
oak-stool 预期不出现在任何 examples 里。
