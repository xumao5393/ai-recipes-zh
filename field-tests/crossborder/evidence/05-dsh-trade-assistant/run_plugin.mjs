// 纯 node 调用 dsh-trade-assistant 的 lib/inquiry.js（不经 dsh、不装包、无网络）。
// 用法: node run_plugin.mjs <clone目录> <inbox.json> [--with-from]
import { readFileSync } from 'node:fs'
import { pathToFileURL } from 'node:url'
import path from 'node:path'
const [cloneDir, inboxPath, flag] = process.argv.slice(2)
const { analyzeInquiry } = await import(pathToFileURL(path.resolve(cloneDir, 'lib/inquiry.js')).href)
const inbox = JSON.parse(readFileSync(inboxPath, 'utf8'))
const out = []
for (const e of inbox) {
  const text = (flag === '--with-from' ? `From: ${e.sender}\n` : '') + `${e.subject}\n\n${e.body}`
  const r = analyzeInquiry({ inquiry_text: text })
  out.push({ id: e.id, inquiry_type: r.inquiry_type, type_evidence: r.type_evidence, key_fields: r.key_fields, red_flags: r.red_flags })
}
console.log(JSON.stringify(out, null, 1))
