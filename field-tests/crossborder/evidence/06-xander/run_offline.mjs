// 纯 node 调用 Xander 包内代码（不经 dsh）。用法: node run_offline.mjs <clone副本目录> <fake-input.json>
import { readFileSync, readdirSync, existsSync } from 'node:fs';
import path from 'node:path';
import { pathToFileURL } from 'node:url';
const [root, inputPath] = process.argv.slice(2);
const imp = (p) => import(pathToFileURL(path.resolve(root, p)).href);
const mode = process.argv[4] || 'all';
if (mode === 'all' || mode === 'handlers') {
  const { buildTools } = await imp('server/tools.js');
  const { VERSION } = await imp('lib/version.js');
  const tools = buildTools(VERSION);
  console.log('## tools 数量:', tools.length);
  const byName = Object.fromEntries(tools.map((t) => [t.name, t]));
  for (const [n, a] of [['xander_status', { check: false }], ['xander_switches', {}]]) {
    const r = await byName[n].handler(a);
    console.log(`## ${n} ${JSON.stringify(a)} →`);
    console.log(JSON.stringify(r, null, 1).slice(0, 6000));
  }
  const dir = path.resolve(root, 'skills');
  const skills = readdirSync(dir).filter((d) => existsSync(path.join(dir, d, 'SKILL.md'))).map((d) => {
    const m = readFileSync(path.join(dir, d, 'SKILL.md'), 'utf8').match(/^---[\s\S]*?\nname:\s*(.+)\n/);
    return { dir: d, frontmatterName: m ? m[1].trim() : null };
  });
  console.log('## skills/*/SKILL.md（静态读取，不是 dsh 的技能发现）:', JSON.stringify(skills));
}
if (mode === 'all' || mode === 'calc') {
  const { replenishment, profitBridge } = await imp('lib/calc.js');
  const input = JSON.parse(readFileSync(inputPath, 'utf8'));
  console.log('## replenishment →'); console.log(JSON.stringify(replenishment(input.replenishment), null, 1));
  input.profit.forEach((p, i) => { console.log(`## profitBridge #${i + 1} →`); console.log(JSON.stringify(profitBridge(p), null, 1)); });
}
