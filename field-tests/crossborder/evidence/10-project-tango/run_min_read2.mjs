import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { mkdtempSync, readdirSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL(".", import.meta.url));
const dataDir = mkdtempSync(join(tmpdir(), "tango-min2-"));
const transport = new StdioClientTransport({
  command: process.execPath,
  args: ["--import", "tsx", join(root, "src", "index.ts")],
  env: { ...process.env, PROJECT_TANGO_DATA_DIR: dataDir },
  stderr: "pipe",
});
const errChunks = [];
transport.stderr?.on("data", (d) => errChunks.push(d));
const client = new Client({ name: "fourday-min-read2", version: "0.0.1" });
await client.connect(transport);

async function call(name, args = {}) {
  const r = await client.callTool({ name, arguments: args });
  const text = (r.content || []).map((c) => (c.type === "text" ? c.text : JSON.stringify(c))).join("\n");
  let parsed; try { parsed = JSON.parse(text); } catch { parsed = text; }
  return { isError: !!r.isError, parsed };
}

const products = await call("list_all_products", {});
const p0 = products.parsed.products[0];
console.log("PRODUCT_KEYS", Object.keys(p0).join(","));
console.log("PRODUCT_COUNT", products.parsed.count);
console.log("PRODUCT_SAMPLE", JSON.stringify(products.parsed.products.slice(0, 3).map(p => ({
  id: p.id, sku: p.sku, name: p.name, stock: p.stock, category: p.category, price: p.price
}))));

const low = await call("get_low_stock_alerts", {});
console.log("LOW_KEYS", Object.keys(low.parsed).join(","));
console.log("LOW_ALERT_KEYS", low.parsed.alerts[0] ? Object.keys(low.parsed.alerts[0]).join(",") : "none");
console.log("LOW_SUMMARY", JSON.stringify({
  alertCount: low.parsed.alertCount, criticalCount: low.parsed.criticalCount, thresholdUsed: low.parsed.thresholdUsed,
  alerts: low.parsed.alerts.slice(0, 5),
}));

const orders = await call("find_orders", { customer_name: "a", limit: 5 });
console.log("ORDERS", JSON.stringify({
  isError: orders.isError,
  count: orders.parsed.count,
  keys: orders.parsed && typeof orders.parsed === "object" ? Object.keys(orders.parsed) : typeof orders.parsed,
  first: orders.parsed.orders ? orders.parsed.orders[0] : orders.parsed,
}, null, 0).slice(0, 800));

const restock = await call("smart_restock_predictor", {});
console.log("RESTOCK_SUMMARY", JSON.stringify({
  thresholdUsed: restock.parsed.thresholdUsed,
  window: restock.parsed.window,
  recommendationCount: restock.parsed.recommendations?.length,
  top3: restock.parsed.recommendations?.slice(0, 3),
}));

console.log("STDERR", Buffer.concat(errChunks).toString("utf8").trim());
console.log("DATA_DIR", dataDir, readdirSync(dataDir).join(","));
await client.close();
console.log("MIN_READ2 n=1 PASS");
