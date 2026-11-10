// Option (a): load workbench.html's loading IIFE unmodified in node vm,
// with a minimal DOM/window stub, then call window.LG.calc (plugin's lgCalc).
import { readFileSync, createWriteStream } from 'node:fs';
import { createHash } from 'node:crypto';
import vm from 'node:vm';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const iifePath = join(here, 'lg-iife-extracted.js');
const iifeBytes = readFileSync(iifePath);
const iifeSha = createHash('sha256').update(iifeBytes).digest('hex');
const input = JSON.parse(readFileSync(join(here, 'fake-input.json'), 'utf8'));
const handSha = createHash('sha256').update(readFileSync(join(here, 'hand-calc.md'))).digest('hex');
const inputSha = createHash('sha256').update(readFileSync(join(here, 'fake-input.json'))).digest('hex');

function el(id) {
  const store = { id, textContent: '', innerHTML: '', className: '', style: { display: '' }, disabled: false, value: '', dataset: {} };
  return {
    get id() { return store.id; },
    get textContent() { return store.textContent; },
    set textContent(v) { store.textContent = String(v); },
    get innerHTML() { return store.innerHTML; },
    set innerHTML(v) { store.innerHTML = String(v); },
    get className() { return store.className; },
    set className(v) { store.className = String(v); },
    style: store.style,
    get disabled() { return store.disabled; },
    set disabled(v) { store.disabled = !!v; },
    get value() { return store.value; },
    set value(v) { store.value = String(v); },
    dataset: store.dataset,
    addEventListener() {},
    removeEventListener() {},
    getBoundingClientRect() { return { width: 800, height: 600, top: 0, left: 0, right: 800, bottom: 600 }; },
    querySelector() { return null; },
    querySelectorAll() { return []; },
    setAttribute() {},
    getAttribute() { return null; },
    appendChild() {},
    removeChild() {},
    classList: { add() {}, remove() {}, toggle() {}, contains() { return false; } },
  };
}

const els = new Map();
function getEl(id) {
  if (!els.has(id)) els.set(id, el(id));
  return els.get(id);
}

// No lgCanvas → lgInit returns early; we drive LG.calc ourselves.
const localStore = new Map();
const noopCtx = new Proxy({}, { get: () => () => {}, set: () => true });

const documentStub = {
  readyState: 'complete',
  body: el('body'),
  documentElement: el('html'),
  getElementById(id) {
    if (id === 'lgCanvas') return null; // force lgInit early-return
    return getEl(id);
  },
  querySelector(sel) {
    if (typeof sel !== 'string') return null;
    if (sel.startsWith('#')) return getEl(sel.slice(1));
    return null;
  },
  querySelectorAll(sel) {
    // lgSync looks for '#lgCargoList .lg-cargo' — return empty so state.items untouched
    return [];
  },
  createElement(tag) { return el(tag); },
  addEventListener() {},
  removeEventListener() {},
};

const windowStub = {
  document: documentStub,
  localStorage: {
    getItem(k) { return localStore.has(k) ? localStore.get(k) : null; },
    setItem(k, v) { localStore.set(k, String(v)); },
    removeItem(k) { localStore.delete(k); },
  },
  addEventListener() {},
  removeEventListener() {},
  print() {},
  console,
  Math,
  parseFloat,
  parseInt,
  isFinite,
  JSON,
  Array,
  Object,
  String,
  Number,
  Boolean,
  Date,
  RegExp,
  Error,
  setTimeout(fn) { /* no delayed calc */ return 0; },
  clearTimeout() {},
  requestAnimationFrame(fn) { return 0; },
  cancelAnimationFrame() {},
};

windowStub.window = windowStub;
windowStub.globalThis = windowStub;
documentStub.defaultView = windowStub;

const context = vm.createContext(windowStub);
vm.runInContext(iifeBytes.toString('utf8'), context, { filename: 'lg-iife-extracted.js' });

if (!windowStub.LG || typeof windowStub.LG.calc !== 'function') {
  console.error('FAIL: window.LG.calc not exposed after loading IIFE');
  process.exit(2);
}
console.log('IIFE_SHA256', iifeSha);
console.log('IIFE_BYTES', iifeBytes.length);
console.log('HAND_SHA256', handSha);
console.log('INPUT_SHA256', inputSha);
console.log('LG_KEYS', Object.keys(windowStub.LG).join(','));

const expected = {
  A: { totalCbm: 6.0, totalGw: 1100, nEst20: 1, nEst40: 1 },
  B: { totalCbm: 8.0784, totalGw: 1100, nEst20: 1, nEst40: 1 },
  C: { totalCbm: 38.4096, totalGw: 12465, nEst20: 2, nEst40: 1 },
};
function near(a, b, eps = 1e-9) { return Math.abs(a - b) <= eps; }

const results = [];
for (const g of input.groups) {
  for (const vk of input.vehicle_keys) {
    // Reset state the way the plugin keeps it
    windowStub.LG.state.tab = 'container';
    windowStub.LG.state.model = vk;
    windowStub.LG.state.items = g.items.map((it, idx) => ({
      id: idx + 1,
      name: it.name,
      l: it.l, w: it.w, h: it.h,
      qty: it.qty,
      net: it.net, tare: it.tare,
      pcsCtn: it.pcsCtn || 10,
      packType: 'none',
      packMode: it.packMode || 'thick',
      packThick: it.packThick || 0,
      packRate: 0,
      stackLayers: it.stackLayers || 0,
      stackLoad: it.stackLoad || 0,
      dir: it.dir || 'any',
      fragile: !!it.fragile,
      gapType: 'standard',
      gapL: it.gapL || 0, gapW: it.gapW || 0, gapH: it.gapH || 0,
      usePallet: !!it.usePallet,
      palletL: it.palletL || 120, palletW: it.palletW || 100, palletWeight: it.palletWeight || 20,
      _adv: false,
    }));
    windowStub.LG.state.nextId = g.items.length + 1;
    windowStub.LG.state.results = [];
    windowStub.LG.state.stats = null;

    windowStub.LG.calc(); // plugin's real lgCalc
    const s = windowStub.LG.state.stats;
    if (!s) {
      console.error('NO_STATS', g.id, vk);
      process.exit(3);
    }
    const exp = expected[g.id];
    const nEstExp = vk === '20GP' ? exp.nEst20 : exp.nEst40;
    const row = {
      group: g.id, vehicle: vk,
      totalCbm: s.totalCbm, totalGw: s.totalGw, nEst: s.nEst,
      usage: s.usage, packed: s.packed, attempted: s.attempted,
      match_totalCbm: near(s.totalCbm, exp.totalCbm),
      match_totalGw: near(s.totalGw, exp.totalGw),
      match_nEst: s.nEst === nEstExp,
      hand_totalCbm: exp.totalCbm, hand_totalGw: exp.totalGw, hand_nEst: nEstExp,
    };
    results.push(row);
    console.log(JSON.stringify(row));
  }
}
const allOk = results.every(r => r.match_totalCbm && r.match_totalGw && r.match_nEst);
console.log('OVERALL_PLUGIN_LGCALC', allOk ? 'PASS' : 'FAIL', 'n=1');
console.log('NOTE source: unmodified IIFE from workbench.html via vm; hand calc unchanged from 19:24:55 EST');
process.exit(allOk ? 0 : 1);
