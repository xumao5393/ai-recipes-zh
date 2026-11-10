// Offline CBM / nEst / packing check. Formulas copied from
// assets/workbench.html (commit e4c909ec) lg module: VEHICLES, lgEffDims,
// lgGross, lgRotations, and the totalCbm/nEst/usage parts of lgCalc.
// Same-rule check only. No network.
import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';

const VEHICLES = {
  container: [
    { key: '20GP', name: "20'GP", en: 'STANDARD', w: 235, h: 239, d: 589, maxWeight: 28000, vol: 33.2 },
    { key: '40GP', name: "40'GP", en: 'STANDARD', w: 235, h: 239, d: 1203, maxWeight: 26000, vol: 67.7 },
    { key: '40HQ', name: "40'HQ", en: 'HIGH CUBE', w: 235, h: 269, d: 1203, maxWeight: 26000, vol: 76.3 },
    { key: '45HQ', name: "45'HQ", en: 'HIGH CUBE', w: 235, h: 269, d: 1355, maxWeight: 25000, vol: 86.0 }
  ],
  truck: [
    { key: '4.2m', name: '4.2m', en: 'TRUCK', w: 190, h: 190, d: 420, maxWeight: 5000, vol: 15.2 },
    { key: '5.2m', name: '5.2m', en: 'TRUCK', w: 210, h: 210, d: 520, maxWeight: 8000, vol: 22.9 },
    { key: '6.8m', name: '6.8m', en: 'TRUCK', w: 230, h: 230, d: 680, maxWeight: 10000, vol: 36.0 },
    { key: '7.6m', name: '7.6m', en: 'TRUCK', w: 230, h: 230, d: 760, maxWeight: 12000, vol: 40.2 }
  ]
};

function num(v) { const n = parseFloat(v); return isFinite(n) && n > 0 ? n : 0; }
function lgEffDims(it) {
  const l = num(it.l), w = num(it.w), h = num(it.h);
  if (it.packMode === 'rate') {
    const r = Math.min(0.9, Math.max(0, num(it.packRate) / 100));
    const s = Math.cbrt(1 / (1 - r));
    return { l: l * s, w: w * s, h: h * s };
  }
  const th = Math.max(0, num(it.packThick));
  return { l: l + 2 * th, w: w + 2 * th, h: h + 2 * th };
}
function lgGross(it) {
  return num(it.net) + num(it.tare) + (it.usePallet ? num(it.palletWeight) : 0);
}
function lgRotations(l, w, h, dir) {
  const rots = [];
  if (dir === 'fixed') rots.push({ w: l, h: h, d: w });
  else if (dir === 'up') { rots.push({ w: l, h: h, d: w }); rots.push({ w: w, h: h, d: l }); }
  else if (dir === 'side') {
    rots.push({ w: l, h: w, d: h }); rots.push({ w: h, h: w, d: l });
    rots.push({ w: w, h: l, d: h }); rots.push({ w: h, h: l, d: w });
  } else {
    rots.push({ w: l, h: h, d: w }); rots.push({ w: l, h: w, d: h });
    rots.push({ w: w, h: h, d: l }); rots.push({ w: w, h: l, d: h });
    rots.push({ w: h, h: l, d: w }); rots.push({ w: h, h: w, d: l });
  }
  const out = [], seen = {};
  for (const r of rots) {
    const k = r.w + '-' + r.h + '-' + r.d;
    if (!seen[k]) { seen[k] = 1; out.push(r); }
  }
  return out;
}
function vehicleByKey(key) {
  for (const list of Object.values(VEHICLES)) {
    for (const v of list) if (v.key === key) return v;
  }
  throw new Error('unknown vehicle ' + key);
}

// Port of lgCalc packing + stats (no DOM/canvas). Same control flow as source.
function lgCalc(items, vehicleKey) {
  const v = vehicleByKey(vehicleKey);
  const containerVol = v.w * v.h * v.d;
  const placed = [];
  let packedWeight = 0, packedVolume = 0, usedVolume = 0;
  let attempted = 0, packed = 0, capped = false;
  let totalW = 0, momX = 0;
  let cursor = 0;
  let weightFull = false, spaceFull = false;
  const COLORS = ['#1','#2','#3','#4','#5','#6','#7','#8'];

  const groups = [];
  items.forEach((it, idx) => {
    const qty = Math.max(0, Math.floor(num(it.qty)));
    if (qty <= 0) return;
    const d = lgEffDims(it);
    if (!(d.l > 0 && d.w > 0 && d.h > 0)) return;
    const n = Math.min(qty, 2000);
    if (n < qty) capped = true;
    attempted += n;
    groups.push({
      item: it, qty: n, dims: d, gross: lgGross(it),
      color: COLORS[idx % COLORS.length],
      name: it.name || ('货物 #' + (idx + 1)),
      dir: it.fragile ? 'up' : it.dir,
      gapL: num(it.gapL), gapW: num(it.gapW), gapH: num(it.gapH),
      usePallet: !!it.usePallet,
      palletL: num(it.palletL), palletW: num(it.palletW),
      maxLayers: Math.floor(num(it.stackLayers)),
      maxLoad: num(it.stackLoad),
      vol: d.l * d.w * d.h
    });
  });
  groups.sort((a, b) => b.vol - a.vol);

  groups.forEach((g) => {
    if (weightFull || spaceFull) return;
    const rotations = g.usePallet
      ? [{ w: g.palletL, h: g.dims.h + 15, d: g.palletW }]
      : lgRotations(g.dims.l, g.dims.w, g.dims.h, g.dir);

    let bestO = null;
    rotations.forEach((rot) => {
      const bw = rot.w + (g.usePallet ? 0 : g.gapL);
      const bh = rot.h + (g.usePallet ? 0 : g.gapH);
      const bd = rot.d + (g.usePallet ? 0 : g.gapW);
      let nx = Math.floor((v.w + 1e-6) / bw);
      let ny = Math.floor((v.h + 1e-6) / bh);
      if (g.maxLayers > 0 && ny > g.maxLayers) ny = g.maxLayers;
      if (g.maxLoad > 0 && g.gross > 0) {
        const nyLoad = Math.floor(g.maxLoad / g.gross) + 1;
        if (ny > nyLoad) ny = nyLoad;
      }
      if (nx < 1 || ny < 1) return;
      const per = nx * ny;
      const rows = Math.ceil(g.qty / per);
      const need = rows * bd;
      const o = { rot, bw, bh, bd, nx, ny, per, rows, need };
      if (!bestO || o.need < bestO.need - 1e-6 ||
          (Math.abs(o.need - bestO.need) < 1e-6 && (o.per > bestO.per || (o.per === bestO.per && o.bh > bestO.bh)))) {
        bestO = o;
      }
    });
    if (!bestO) { spaceFull = true; return; }

    const xBase = Math.max(0, (v.w - bestO.nx * bestO.bw) / 2);
    let remain = g.qty;
    let row = 0;
    const groupStart = cursor;

    while (remain > 0 && !weightFull && !spaceFull) {
      const z0 = groupStart + row * bestO.bd;
      if (z0 + bestO.bd > v.d + 1e-6) { spaceFull = true; break; }
      for (let l = 0; l < bestO.ny && remain > 0 && !weightFull; l++) {
        for (let c = 0; c < bestO.nx && remain > 0; c++) {
          if (packedWeight + g.gross > v.maxWeight + 1e-6) { weightFull = true; break; }
          const x = xBase + c * bestO.bw;
          placed.push({ x, y: l * bestO.bh, z: z0, w: bestO.rot.w, h: bestO.rot.h, d: bestO.rot.d,
            bw: bestO.bw, bh: bestO.bh, bd: bestO.bd, gross: g.gross, layers: l + 1 });
          packedWeight += g.gross;
          packedVolume += g.vol;
          usedVolume += bestO.bw * bestO.bh * bestO.bd;
          totalW += g.gross;
          momX += g.gross * (x + bestO.bw / 2);
          packed++;
          remain--;
        }
      }
      row++;
      if (weightFull) break;
    }
    if (!weightFull && !spaceFull) cursor = groupStart + row * bestO.bd;
    else if (!weightFull) cursor = groupStart + row * bestO.bd;
    if (cursor > v.d) cursor = v.d;
  });

  if (weightFull) cursor = v.d;
  const blocked = attempted - packed;
  const usage = containerVol > 0 ? usedVolume / containerVol * 100 : 0;
  const sat = v.maxWeight > 0 ? packedWeight / v.maxWeight * 100 : 0;
  const cg = totalW > 0 ? ((momX / totalW) - v.w / 2) / v.w * 100 : 0;
  let totalCbm = 0, totalGw = 0;
  items.forEach((it) => {
    const d = lgEffDims(it);
    totalCbm += d.l * d.w * d.h * num(it.qty) / 1000000;
    totalGw += lgGross(it) * num(it.qty);
  });
  const nEst = Math.max(1,
    Math.ceil(totalCbm / (v.vol * 0.85) - 1e-9),
    Math.ceil(totalGw / (v.maxWeight * 0.9) - 1e-9));

  return {
    vehicle: vehicleKey,
    containerVol_cm3: containerVol,
    usage, sat, cg,
    packed, attempted, blocked,
    cbm_packed: packedVolume / 1000000,
    gw_packed: packedWeight,
    totalCbm, totalGw, nEst,
    depthUse: cursor / v.d * 100,
    weightFull, spaceFull, capped
  };
}

const input = JSON.parse(readFileSync(new URL('./fake-input.json', import.meta.url), 'utf8'));
const hand = readFileSync(new URL('./hand-calc.md', import.meta.url), 'utf8');
const expected = {
  A: { totalCbm: 6.0, totalGw: 1100, nEst20: 1, nEst40: 1 },
  B: { totalCbm: 8.0784, totalGw: 1100, nEst20: 1, nEst40: 1 },
  C: { totalCbm: 38.4096, totalGw: 12465, nEst20: 2, nEst40: 1 }
};

function near(a, b, eps = 1e-9) { return Math.abs(a - b) <= eps; }

const results = [];
for (const g of input.groups) {
  for (const vk of input.vehicle_keys) {
    const r = lgCalc(g.items, vk);
    const exp = expected[g.id];
    const nEstExp = vk === '20GP' ? exp.nEst20 : exp.nEst40;
    const row = {
      group: g.id, vehicle: vk,
      totalCbm: r.totalCbm, totalGw: r.totalGw, nEst: r.nEst,
      usage: r.usage, packed: r.packed, attempted: r.attempted,
      match_totalCbm: near(r.totalCbm, exp.totalCbm),
      match_totalGw: near(r.totalGw, exp.totalGw),
      match_nEst: r.nEst === nEstExp,
      hand_totalCbm: exp.totalCbm, hand_totalGw: exp.totalGw, hand_nEst: nEstExp
    };
    results.push(row);
    console.log(JSON.stringify(row));
  }
}
const allOk = results.every(r => r.match_totalCbm && r.match_totalGw && r.match_nEst);
console.log('OVERALL_CLOSED_FORM', allOk ? 'PASS' : 'FAIL', 'n=1');
console.log('HAND_SHA256', createHash('sha256').update(hand).digest('hex'));
console.log('INPUT_SHA256', createHash('sha256').update(readFileSync(new URL('./fake-input.json', import.meta.url))).digest('hex'));
console.log('NOTE same-rule: formulas copied from workbench.html; proves code follows its own rules only');
process.exit(allOk ? 0 : 1);
