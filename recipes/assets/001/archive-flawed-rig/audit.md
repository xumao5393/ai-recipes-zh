# 001 逐次核对表

> 依据本目录官方快照、原始 JSON 与批次日志，整理于美东时间。未新增推理请求。数值相同不等于计费条件正确；缺口不按“正确”计。

| 记录 | 秒 | 工具事件 | 非空输出 | 核对结论 |
|---|---:|---:|---|---|
| [level1_run1](runs/level1_run1.json) | 10.6 | 0 | 是（可能不完整） | Claude $15、Gemini $10 与官方快照不符；ChatGPT $20 无法从本期证据核定。3 个 URL 未见该次打开证据，域名看似官方不等于页面存在或支持数字。 |
| [level1_run2](runs/level1_run2.json) | 0.4 | 0 | 是（可能不完整） | 与 run1 的 final 完全相同；0.4 秒，可能命中缓存，不能计作独立复测。数字及来源问题同 run1。 |
| [level2_run1](runs/level2_run1.json) | 40.8 | 8 | 否 | final=null，没有价格表。工具记录有 403、404 和搜索入口；不能给价格正确率打分。旧版行为与当前 Harness 不完全一致。 |
| [level2_run2](runs/level2_run2.json) | 6.4 | 8 | 否 | final=null；事件序列与 run1 相同，不据此宣称独立成功或新失败率。 |
| [level3_run0_noguard](runs/level3_run0_noguard.json) | 127.9 | 12 | 否 | final=null；12 个事件中 ChatGPT 重复请求 10 次，另两家各 1 次。文件无 guard 字段，名称标注 noguard；不把当前源码的 GUARD 默认值追溯到旧运行。 |
| [level3_run2](runs/level3_run2.json) | 68.6 | 8 | 否 | final=null；出现重复护栏，最后用 cursor/pattern 而无 url 调用工具，留下参数校验错误。没有可验收价格。 |
| [level3_run3](runs/level3_run3.json) | 103.8 | 7 | 是（可能不完整） | 部分回答。Pro $17 年付/$20 月付有证据；Max $100、Ultra $200 的金额有证据但年付标签错误。Claude Pro 功能串成类似 ChatGPT 的描述；Ultra 无限使用不获证据支持。Gemini $4.99 仅在开头，表格断在 Gemini。ChatGPT 留空；缺完整交付。 |
| [v1_fetch12000/level1_seed11](runs/v1_fetch12000/level1_seed11.json) | 11.5 | 0 | 是（可能不完整） | Claude $15、Gemini $10 错；ChatGPT $20 无法核定。给出来源但该档无工具访问，Gemini 链接还与后续抓取的 404 入口相同。不可发布。 |
| [v1_fetch12000/level1_seed22](runs/v1_fetch12000/level1_seed22.json) | 25.3 | 0 | 是（可能不完整） | 只有 137 字符的免责声明和历史趋势假设，断在“若需最”；无价格表，不能说正确完成。 |
| [v1_fetch12000/level1_seed33](runs/v1_fetch12000/level1_seed33.json) | 11.6 | 0 | 是（可能不完整） | Claude $5、Gemini $5 与快照不符；ChatGPT $20 证据不足。声明历史数据不能使当前查价任务通过；token 配额描述也未获快照支持。 |
| [v1_fetch12000/level2_seed11](runs/v1_fetch12000/level2_seed11.json) | 367.9 | 7 | 否 | final 为空字符串。抓取有 HTTP 200，但 Gemini 定价入口 404、首页是登录提示；反复请求被护栏拦截。没有可评分价格。 |
| [v1_fetch12000/level2_seed22](runs/v1_fetch12000/level2_seed22.json) | 762.6 | 7 | 否 | final 为空字符串；旧 Claude 入口 403，另访问 ChatGPT API 路径；日志有读取超时重试。无法归因为单一上下文问题。 |
| [v1_fetch12000/level3_seed11](runs/v1_fetch12000/level3_seed11.json) | 537.1 | 7 | 否 | final 为空字符串；7 个事件仅首个 ChatGPT 请求有正文，其后 6 个均为重复护栏。Skill 没有使其查完三家。 |
| [v1_fetch12000/level3_seed22](runs/v1_fetch12000/level3_seed22.json) | 444.5 | 7 | 否 | final 为空字符串；前三次访问指定三家官网成功，后 4 个重复 ChatGPT 事件被拦。抓到网页不等于答完表格。 |
| [v2_fetch5000/level2_seed11](runs/v2_fetch5000/level2_seed11.json) | 758.3 | 7 | 否 | final 为空字符串；出现 Claude 403、Gemini 404，转到 ai.google.dev/pricing（API，不是个人订阅）；日志有读取超时。 |
| [v2_fetch5000/level2_seed22](runs/v2_fetch5000/level2_seed22.json) | 352.0 | 7 | 否 | final 为空字符串；旧 Claude 入口 403，Gemini 入口 404，3 个重复事件被拦。无可验收价格。 |
| [v2_fetch5000/level3_seed11](runs/v2_fetch5000/level3_seed11.json) | 345.5 | 7 | 是（可能不完整） | 984 字符的部分输出，末行断在来源 URL。4 个数字（Claude 17/100/200，Gemini 4.99）与快照金额一致；Pro 漏年付限定及月付 20；Plus 名称误带脚注 1；漏 Gemini Pro/Ultra；ChatGPT 留空。3 官网成功、3 护栏、1 错误工具名。最便宜结论因缺其他价格不能覆盖三家。 |

## 不形成 JSON 的记录，不塞进完成样本

- v1 的 level2_seed33：批次日志只有开始，没有结果文件。
- v2 的 level3_seed22：有工具事件和四次 output_token_limit_exceeded，随后异常，无最终 JSON。失败时间 2026-11-07 23:42:33 EST（由日志 UTC 转换）。
- v2 的 level2_seed33：日志记载开始，整理时仍运行，已停止，没有最终 JSON。

## 审计限制

- 所有 17 份已保存 JSON 返回模型名均为 gpt-oss-20b；正式批次 10 份，不是完整平衡实验。
- JSON 仅保存每个工具结果前 300 字符，没有保存完整对话、完整模型响应、finish_reason 或 token usage。独立官方文本用于核对金额，但不能证明某个金额完整出现在该次模型收到的截断正文中。
- 官方 ChatGPT 浏览器画面是验证页，不是价格截图；其 HTTP 文本中也缺金额，所以相关价格保留为无法核定。
- 链接判断仅限已保存抓取与官方快照；没有逐一新增访问早期答案中的每个 URL，因此不把全部错误链接武断称为不存在或伪造。
- 12000 与 5000 字符批次、旧版与当前 Harness 不混算因果效果。空 final 本身不能证明必然 token 超限；仅 v2 的日志报错能证明对应那次的原因。
- 不对外推模型优劣、免费服务持续性或赚钱效果作结论。
