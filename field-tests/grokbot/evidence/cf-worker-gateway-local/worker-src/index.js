/**
 * Local-only Cloudflare Worker simulation of:
 * VPS reports every 5 min -> Worker dedupe/filter -> wake only on state change/fault
 * Author article did NOT publish code; this is our own minimal implementation.
 *
 * Assumptions (documented in article):
 * - Report payload: { host, status: "ok"|"fault", code?, ts }
 * - Wake when: status transitions to fault, OR status transitions from fault to ok (recovery),
 *   OR first-seen host with fault. Repeated identical "ok" or identical "fault" within window = no wake.
 * - Dedupe key: host + status (+ code for fault)
 */

const lastByHost = new Map(); // in-memory for local single-isolate; durable KV not used offline

function json(data, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { "content-type": "application/json" },
  });
}

async function wake(env, reason, event) {
  const url = env.WAKE_WEBHOOK_URL;
  const body = JSON.stringify({ reason, event, at: Date.now() });
  const res = await fetch(url, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body,
  });
  return { ok: res.ok, status: res.status };
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (request.method === "GET" && url.pathname === "/health") {
      return json({ ok: true, hosts: lastByHost.size });
    }
    if (request.method === "POST" && url.pathname === "/report") {
      let event;
      try {
        event = await request.json();
      } catch {
        return json({ error: "invalid json" }, 400);
      }
      const host = String(event.host || "");
      const status = String(event.status || "");
      if (!host || (status !== "ok" && status !== "fault")) {
        return json({ error: "need host and status ok|fault" }, 400);
      }
      const code = event.code != null ? String(event.code) : "";
      const prev = lastByHost.get(host);
      let shouldWake = false;
      let reason = "suppressed";
      if (!prev) {
        if (status === "fault") {
          shouldWake = true;
          reason = "first_fault";
        } else {
          reason = "first_ok_no_wake";
        }
      } else if (prev.status !== status) {
        shouldWake = true;
        reason = status === "fault" ? "transition_to_fault" : "transition_to_ok";
      } else if (status === "fault" && prev.code !== code) {
        shouldWake = true;
        reason = "fault_code_change";
      } else {
        reason = "duplicate";
      }
      lastByHost.set(host, { status, code, ts: event.ts || Date.now() });
      let wakeResult = null;
      if (shouldWake) {
        try {
          wakeResult = await wake(env, reason, event);
        } catch (e) {
          wakeResult = { ok: false, error: String(e) };
        }
      }
      return json({ woke: shouldWake, reason, wakeResult, host, status });
    }
    if (request.method === "POST" && url.pathname === "/reset") {
      lastByHost.clear();
      return json({ reset: true });
    }
    return json({ error: "not found" }, 404);
  },
};
