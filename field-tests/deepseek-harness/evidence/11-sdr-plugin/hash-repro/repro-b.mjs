import { mkdtemp, writeFile, mkdir } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { createHash } from "node:crypto";
import { pathToFileURL } from "node:url";

const PKG = process.env.SDR_PKG;
const OUT = process.env.OUT;
const RUNS = Number(process.env.RUNS || 3);
const { JsonStore, SdrService, draftHash } = await import(pathToFileURL(join(PKG, "lib/domain.js")).href);

await mkdir(OUT, { recursive: true });
const summary = [];

for (let r = 1; r <= RUNS; r++) {
  const directory = await mkdtemp(join(tmpdir(), `dsh-sdr-repro-b${r}-`));
  const storePath = join(directory, "state.json");
  const store = new JsonStore(storePath);
  const sdr = new SdrService({ store });
  const ts0 = new Date().toISOString();
  const created = await sdr.createTask({
    task: "开发 3 个美国户外用品客户",
    campaignVersion: `repro-b-${r}-${Date.now()}`,
  });
  for (let i = 0; i < 5; i++) await sdr.nextStep(created.task_id);
  const draftsBefore = await sdr.getDrafts(created.task_id);
  const ids = draftsBefore.drafts.map((d) => d.email_id);
  const hashesAtApprove = draftsBefore.drafts.map((d) => ({
    email_id: d.email_id,
    draft_hash: d.draft_hash,
    recalc: draftHash(d),
  }));
  const approved = await sdr.reviewDrafts(created.task_id, ids, `repro-${r}`);
  const tsApproved = new Date().toISOString();
  // tamper draft 0 subject
  await store.mutate((data) => {
    data.tasks[created.task_id].drafts[0].subject += ` [TAMPER-R${r}]`;
  });
  const stateAfter = await store.read();
  const d0 = stateAfter.tasks[created.task_id].drafts[0];
  const hashAfter = draftHash(d0);
  const approvalHash = stateAfter.tasks[created.task_id].approvals[d0.email_id]?.draft_hash;
  let continueResult = null;
  let continueError = null;
  const tsContinue = new Date().toISOString();
  try {
    continueResult = await sdr.continueAfterApproval(created.task_id);
  } catch (e) {
    continueError = String(e.message || e);
  }
  const row = {
    run: r,
    n: 1,
    tmp_dir_basename: directory.split("/").pop(),
    task_id: created.task_id,
    ts_start: ts0,
    ts_approved: tsApproved,
    ts_continue: tsContinue,
    hashes_at_approve: hashesAtApprove,
    tampered_email_id: d0.email_id,
    hash_after_tamper: hashAfter,
    approval_stored_hash: approvalHash,
    hashes_equal_after_tamper: approvalHash === hashAfter,
    continue_error: continueError,
    continue_advanced: continueResult?.result?.advanced ?? null,
    continue_stage: continueResult?.task?.stage ?? null,
    pending_after_approve_before_tamper: approved.pending,
  };
  summary.push(row);
  await writeFile(join(OUT, `run-${r}.json`), JSON.stringify(row, null, 2) + "\n");
  console.log(JSON.stringify(row));
}
await writeFile(join(OUT, "summary.json"), JSON.stringify(summary, null, 2) + "\n");
console.log("DONE runs=", RUNS);
