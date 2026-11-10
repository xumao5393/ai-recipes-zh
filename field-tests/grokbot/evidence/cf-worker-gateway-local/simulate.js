/**
 * Simulate 30d * 288 reports/day = 8640 reports against local Worker.
 * Assumptions documented in output JSON.
 */
const WORKER = process.env.WORKER_URL || "http://127.0.0.1:8787";
const HOSTS = (process.env.HOSTS || "vps-a").split(",");
const DAYS = Number(process.env.DAYS || 30);
const PER_DAY = Number(process.env.PER_DAY || 288);
const FAULT_EVENTS = Number(process.env.FAULT_EVENTS || 50);
const FAULT_DURATION_REPORTS = Number(process.env.FAULT_DURATION || 3);

async function post(path, body) {
  const res = await fetch(WORKER + path, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify(body || {}),
  });
  return res.json();
}

function pickFaultEpisodes(total, nEpisodes, duration) {
  const starts = [];
  let guard = 0;
  while (starts.length < nEpisodes && guard < nEpisodes * 200) {
    guard++;
    const start = Math.floor(Math.random() * Math.max(1, total - duration));
    let ok = true;
    for (const s of starts) {
      // keep gap so episodes don't merge (need at least 1 ok between)
      if (!(start + duration + 1 <= s || s + duration + 1 <= start)) ok = false;
    }
    if (ok) starts.push(start);
  }
  const slots = new Set();
  for (const s of starts) for (let i = 0; i < duration; i++) slots.add(s + i);
  return { slots, starts, episodes_placed: starts.length };
}

async function main() {
  const seed = Number(process.env.SEED || 42);
  let state = seed >>> 0;
  Math.random = () => {
    state = (1664525 * state + 1013904223) >>> 0;
    return state / 0x100000000;
  };

  await post("/reset", {});
  const totalPerHost = DAYS * PER_DAY;
  const results = { hosts: {}, totals: { reports: 0, wakes_from_worker: 0 } };
  for (const host of HOSTS) {
    const { slots, starts, episodes_placed } = pickFaultEpisodes(
      totalPerHost,
      FAULT_EVENTS,
      FAULT_DURATION_REPORTS
    );
    let wakes = 0;
    let reports = 0;
    const reasons = {};
    for (let i = 0; i < totalPerHost; i++) {
      const isFault = slots.has(i);
      const status = isFault ? "fault" : "ok";
      const code = isFault ? "E_HEALTH" : "";
      const r = await post("/report", { host, status, code, ts: i });
      reports++;
      if (r.woke) {
        wakes++;
        reasons[r.reason] = (reasons[r.reason] || 0) + 1;
      }
    }
    results.hosts[host] = {
      reports,
      wakes_reported_by_worker: wakes,
      wake_reasons: reasons,
      fault_report_count: slots.size,
      fault_episodes_requested: FAULT_EVENTS,
      fault_episodes_placed: episodes_placed,
      fault_duration_reports: FAULT_DURATION_REPORTS,
      expected_wakes_if_all_episodes_isolated:
        "about 2 per episode (enter fault + leave to ok), so ~2*episodes_placed if no merges",
    };
    results.totals.reports += reports;
    results.totals.wakes_from_worker += wakes;
  }
  results.assumptions = {
    days: DAYS,
    reports_per_day_per_host: PER_DAY,
    hosts: HOSTS,
    total_reports_expected: HOSTS.length * DAYS * PER_DAY,
    fault_episodes_per_host: FAULT_EVENTS,
    fault_duration_reports: FAULT_DURATION_REPORTS,
    wake_rules:
      "wake on first fault, status transition ok<->fault, or fault code change; suppress duplicate same status",
    note_author_claim:
      "Author self-reported 8640->40-60; our numbers depend on fault injection assumptions and are NOT a verification of the author claim.",
    seed,
    implementation: "our own minimal Worker; article published no code",
  };
  const outPath = process.env.OUT || "/tmp/cf-worker-outside-repo/sim-result.json";
  require("fs").writeFileSync(outPath, JSON.stringify(results, null, 2));
  console.log(JSON.stringify(results, null, 2));
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
