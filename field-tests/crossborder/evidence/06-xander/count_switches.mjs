// 补充：run_offline.mjs 把 handler 输出截到 6000 字符，开关条数看不全；这里只数条数和 on 的个数。
import path from 'node:path'; import { pathToFileURL } from 'node:url';
const root = process.argv[2];
const { buildTools } = await import(pathToFileURL(path.resolve(root, 'server/tools.js')).href);
const t = buildTools('x').find((x) => x.name === 'xander_switches');
const d = JSON.parse(await t.handler({}));
console.log('顶层字段:', Object.keys(d).join(','));
console.log('开关条数:', d.items.length, '其中 on=true:', d.items.filter((i) => i.on).length, 'implemented=true:', d.items.filter((i) => i.implemented).length);
console.log('工具总数:', buildTools('x').length, '名称:', buildTools('x').map((x) => x.name).join(','));
