import { createServer } from 'node:http';
import { Config, apply } from '../src/index.js';
import { CHANNEL_WEBHOOK } from '../src/lib/notify.js';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { readFileSync, writeFileSync } from 'node:fs';

const here = dirname(fileURLToPath(import.meta.url));
const received = [];

const server = createServer(async (req, res) => {
  const chunks = [];
  for await (const c of req) chunks.push(c);
  const body = Buffer.concat(chunks).toString('utf8');
  received.push({
    method: req.method,
    url: req.url,
    contentType: req.headers['content-type'],
    body,
  });
  res.writeHead(200, { 'content-type': 'application/json' });
  res.end('{"ok":true}');
});
await new Promise((r) => server.listen(0, '127.0.0.1', r));
const { port } = server.address();
const webhookUrl = `http://127.0.0.1:${port}/hook`;
console.log('WEBHOOK_URL', webhookUrl);

const handlers = [];
const ctx = {
  logger: { warn: (...a) => console.error('WARN', ...a), info() {}, debug() {}, error: (...a) => console.error('ERR', ...a) },
  fiber: { ctx: { fiber: {} } },
  get() { return undefined; },
  on(event, handler) { handlers.push({ event, handler }); return () => {}; },
  inject() { return () => {}; },
};

const config = Config({
  enabled: true,
  defaultNotify: true,
  channels: [CHANNEL_WEBHOOK],
  events: ['task-complete', 'task-interrupted', 'approval-required', 'question-required'],
  titlePrefix: 'DSH-TEST',
  webhookUrl,
  webhookMethod: 'POST',
  webhookBody: '{"event":"{{event}}","title":"{{title}}","message":"{{message}}","sessionId":"{{sessionId}}","sessionTitle":"{{sessionTitle}}","parentTitle":"{{parentTitle}}","timestamp":"{{timestamp}}"}',
  webhookContentType: 'application/json',
  // leave gotify/ntfy urls empty → skipped
  gotifyUrl: '',
  ntfyUrl: '',
  ntfyTopic: '',
});

const dispose = apply(ctx, config);

async function emit(session, event) {
  for (const entry of handlers) {
    if (entry.event === 'session/event') entry.handler(session, event);
  }
  await new Promise((r) => setTimeout(r, 50));
}

const session = { id: 'sess-local-1', header: { cwd: '/tmp/fake-workdir-for-test' } };

// 1) title then task complete
await emit(session, { type: 'session/title', data: { title: '本地假会话-完成' } });
const before1 = received.length;
await emit(session, { type: 'turn/end', data: { turn: 1, reason: { kind: 'completed' } } });
console.log('AFTER_COMPLETE received_delta', received.length - before1);

// 2) approval needed
const before2 = received.length;
await emit(session, {
  type: 'approval/asked',
  data: { name: 'bash', reason: 'dangerous command needs approval' },
});
console.log('AFTER_APPROVAL received_delta', received.length - before2);

// 3) question (optional)
const before3 = received.length;
await emit(session, {
  type: 'tool/call',
  data: { name: 'ask_user_question', arguments: { question: '要继续吗？' } },
});
console.log('AFTER_QUESTION received_delta', received.length - before3);

dispose();
server.close();

const out = {
  webhookUrl,
  n: 1,
  count: received.length,
  payloads: received,
};
writeFileSync(join(here, 'drive-events-result.json'), JSON.stringify(out, null, 2));
console.log(JSON.stringify(out, null, 2));

// Leak scan
const blob = JSON.stringify(received);
const leaks = {
  has_prompt_like: /system prompt|You are |<\/?system>/i.test(blob),
  has_workspace_path: blob.includes('/' + 'workspace' + '/'),
  has_home_path: blob.includes('/' + 'home' + '/' + String.fromCharCode(98,111,120)),
  has_api_deepseek: blob.includes('api.' + 'deepseek' + '.com'),
  cwd_in_message: received.some((r) => (r.body || '').includes('/tmp/fake-workdir-for-test')),
};
console.log('LEAK_SCAN', JSON.stringify(leaks));
if (received.length < 2) process.exit(2);
process.exit(0);
