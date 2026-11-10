/**
 * Offline probe of @xuxchloris/dsh-sdr state machine + approval hash.
 * No network, no API keys. Synthetic data only.
 */
import assert from "node:assert/strict";
import { mkdtemp, writeFile, mkdir } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
// Resolve from sandbox-sdr/pkg-src
const PKG = process.env.SDR_PKG || "<sandbox-sdr>/pkg-src/node_modules/@xuxchloris/dsh-sdr";
const { JsonStore, SdrService, STAGES, draftHash } = await import(join(PKG, "lib/domain.js"));

const outDir = process.env.OUT || "<evidence/11-sdr-plugin>/probes";
await mkdir(outDir, { recursive: true });
const lines = [];
const log = (s) => { console.log(s); lines.push(s); };

log(`pkg=${PKG}`);
log(`stages=${JSON.stringify(STAGES)}`);
log(`n=1 each case; clock=${new Date().toISOString()}`);

async function fresh() {
  const directory = await mkdtemp(join(tmpdir(), "dsh-sdr-probe-"));
  const store = new JsonStore(join(directory, "state.json"));
  return { sdr: new SdrService({ store }), store, directory };
}

async function toApproval(sdr, version) {
  const created = await sdr.createTask({ task: "开发 3 个美国户外用品客户", campaignVersion: version });
  for (let i = 0; i < 5; i++) await sdr.nextStep(created.task_id);
  const drafts = await sdr.getDrafts(created.task_id);
  return { taskId: created.task_id, drafts };
}

// --- (a) Can model skip stages? ---
// 1) sdr_next_step has no stage arg; calling continue_after_approval early should fail
{
  const { sdr } = await fresh();
  const created = await sdr.createTask({ task: "开发 3 个美国户外用品客户", campaignVersion: `skip-early-${Date.now()}` });
  log(`a1_created stage=${created.stage}`);
  let earlyFail = null;
  try {
    await sdr.continueAfterApproval(created.task_id);
  } catch (e) {
    earlyFail = String(e.message || e);
  }
  log(`a1_continue_after_approval_at_task_parse: ${earlyFail}`);
  assert.ok(earlyFail && /审批后推进不可用|当前阶段/.test(earlyFail));

  // advance only once
  const step1 = await sdr.nextStep(created.task_id);
  log(`a2_after_one_next_step stage=${step1.task.stage}`);
  assert.equal(step1.task.stage, "prospect_discovery");

  // try continue again (still not at approval)
  let earlyFail2 = null;
  try { await sdr.continueAfterApproval(created.task_id); } catch (e) { earlyFail2 = String(e.message || e); }
  log(`a2_continue_at_prospect_discovery: ${earlyFail2}`);
  assert.ok(earlyFail2);

  // try reviewDrafts early
  let reviewFail = null;
  try { await sdr.reviewDrafts(created.task_id, ["x"]); } catch (e) { reviewFail = String(e.message || e); }
  log(`a3_review_at_prospect_discovery: ${reviewFail}`);
  assert.ok(reviewFail && /审批不可用/.test(reviewFail));

  // mutate stage in store to a later stage illegally — does nextStep jump forward from wrong state?
  // Actually better: force stage field to close via store and see nextStep behavior
}

// Force-write stage to skip ahead via store mutation (simulating model somehow corrupting / a bug path)
{
  const { sdr, store } = await fresh();
  const created = await sdr.createTask({ task: "开发 3 个美国户外用品客户", campaignVersion: `force-stage-${Date.now()}` });
  await store.mutate((data) => {
    data.tasks[created.task_id].stage = "close"; // jump to end without doing work
  });
  const t = await sdr.getTask(created.task_id);
  log(`a4_forced_stage_in_store=${t.stage}`);
  // nextStep on close just generates report — stage stays close; no way to "skip into" middle via tool args
  const r = await sdr.nextStep(created.task_id);
  log(`a4_next_on_forced_close stage=${r.task.stage} has_report=${!!r.result.report}`);
  // Importantly: tools don't accept a stage parameter — document schema
  log(`a5_note: sdr_next_step parameters are task_id only; no stage field in tool schema (see index.js)`);
}

// Advance normally to human_approval; nextStep stays blocked
{
  const { sdr } = await fresh();
  const { taskId, drafts } = await toApproval(sdr, `gate-${Date.now()}`);
  log(`a6_at_approval stage=${drafts.stage} drafts=${drafts.drafts.length} pending=${drafts.pending.length}`);
  const blocked = await sdr.nextStep(taskId);
  log(`a6_next_at_approval blocked=${blocked.result.blocked} reason=${blocked.result.reason}`);
  assert.equal(blocked.result.blocked, true);
  assert.equal(blocked.task.stage, "human_approval");
}

// --- (b) Approval binds draft hash ---
{
  const { sdr, store } = await fresh();
  const { taskId, drafts } = await toApproval(sdr, `hash-pre-${Date.now()}`);
  const id0 = drafts.drafts[0].email_id;
  const hashBefore = drafts.drafts[0].draft_hash;
  await store.mutate((data) => { data.tasks[taskId].drafts[0].subject = "TAMPERED-BEFORE-APPROVAL"; });
  let failPre = null;
  try { await sdr.reviewDrafts(taskId, [id0], "probe"); } catch (e) { failPre = String(e.message || e); }
  log(`b1_tamper_before_approve: ${failPre}`);
  assert.ok(failPre && /哈希不匹配/.test(failPre));
  // restore subject for clean path? recompute would still fail because draft_hash field unchanged vs new content
  // Fix by resetting subject
  await store.mutate((data) => {
    // restore original subject from drafts snapshot
    data.tasks[taskId].drafts[0].subject = drafts.drafts[0].subject;
  });
  const ok = await sdr.reviewDrafts(taskId, drafts.drafts.map(d => d.email_id), "probe");
  log(`b2_approve_all pending=${JSON.stringify(ok.pending)} approved_count=${ok.approved.length}`);
  assert.deepEqual(ok.pending, []);

  // After approval, tamper draft content — does continueAfterApproval still pass?
  await store.mutate((data) => { data.tasks[taskId].drafts[0].subject = "TAMPERED-AFTER-APPROVAL"; });
  let postResult = null, postErr = null;
  try {
    postResult = await sdr.continueAfterApproval(taskId);
  } catch (e) {
    postErr = String(e.message || e);
  }
  log(`b3_tamper_after_approve continue_err=${postErr} continue_ok_stage=${postResult?.task?.stage || null}`);
  // Also check: does pending() notice hash mismatch?
  const after = await sdr.getDrafts(taskId);
  const approvalHash = (await store.read()).tasks[taskId].approvals[id0]?.draft_hash;
  const currentHash = draftHash((await store.read()).tasks[taskId].drafts[0]);
  log(`b3_stored_approval_hash=${approvalHash}`);
  log(`b3_current_draft_hash=${currentHash}`);
  log(`b3_hashes_equal=${approvalHash === currentHash}`);
  log(`b3_pending_after_tamper=${JSON.stringify(after.pending)}`);
}

// connector dry-run
{
  const { sdr } = await fresh();
  const status = await sdr.connectorStatus();
  log(`c1_connectors=${status.connectors.map(c => c.channel + ':' + c.dry_run).join(',')}`);
}

await writeFile(join(outDir, "probe-ab.out.txt"), lines.join("\n") + "\n");
log("DONE");
