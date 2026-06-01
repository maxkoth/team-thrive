#!/usr/bin/env node
/**
 * Phase 7 — Scheduler
 * Runs the full discovery → screening → signal pipeline every 15 minutes.
 * Logs all runs to /logs/run-history.json.
 * Skips run if total crypto volume < $40B (dead market).
 * Use --dry-run to pass through to all sub-processes.
 * Use --once to run the pipeline a single time then exit.
 */

import { execSync, spawnSync } from "child_process";
import { readFileSync, writeFileSync, existsSync, mkdirSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const DRY_RUN = process.argv.includes("--dry-run");
const RUN_ONCE = process.argv.includes("--once");

const INTERVAL_MS = 15 * 60 * 1000;
const DEAD_MARKET_VOLUME_B = 40;
const HISTORY_PATH = resolve(__dirname, "../logs/run-history.json");
const ROOT = resolve(__dirname, "..");

mkdirSync(resolve(__dirname, "../logs"), { recursive: true });
mkdirSync(resolve(__dirname, "../data"), { recursive: true });

// ---------------------------------------------------------------------------
// Run history
// ---------------------------------------------------------------------------
function loadHistory() {
  if (existsSync(HISTORY_PATH)) return JSON.parse(readFileSync(HISTORY_PATH, "utf8"));
  return { runs: [] };
}

function appendHistory(record) {
  const h = loadHistory();
  h.runs = [record, ...h.runs].slice(0, 500);
  writeFileSync(HISTORY_PATH, JSON.stringify(h, null, 2));
}

// ---------------------------------------------------------------------------
// Market activity check (mock: production → hit CoinGecko global endpoint)
// ---------------------------------------------------------------------------
async function getMarketVolume24h() {
  if (DRY_RUN) return 85; // always active in dry run
  try {
    const res = execSync(
      `curl -s "https://api.coingecko.com/api/v3/global" --max-time 10`,
      { encoding: "utf8" }
    );
    const data = JSON.parse(res);
    const volumeB = data.data?.total_volume?.usd / 1e9;
    return volumeB || 0;
  } catch {
    return 999; // default active if check fails
  }
}

// ---------------------------------------------------------------------------
// Run a node script and capture output
// ---------------------------------------------------------------------------
function runScript(relPath, extraArgs = []) {
  const args = ["--input-type=module", relPath, ...(DRY_RUN ? ["--dry-run"] : []), ...extraArgs];
  const result = spawnSync(process.execPath, args, {
    cwd: ROOT,
    encoding: "utf8",
    env: { ...process.env },
    timeout: 120000,
  });
  return {
    stdout: result.stdout || "",
    stderr: result.stderr || "",
    exitCode: result.status,
    error: result.error?.message,
  };
}

// ---------------------------------------------------------------------------
// Full pipeline run
// ---------------------------------------------------------------------------
async function runPipeline() {
  const startTime = Date.now();
  const runId = `RUN_${startTime}`;
  console.log(`\n${"═".repeat(60)}`);
  console.log(`🔄 Pipeline Run: ${new Date().toISOString()}  [${runId}]`);
  console.log(`${"═".repeat(60)}`);

  const volumeB = await getMarketVolume24h();
  if (volumeB < DEAD_MARKET_VOLUME_B) {
    const record = {
      run_id: runId,
      timestamp: new Date().toISOString(),
      skipped: true,
      reason: `Market volume $${volumeB.toFixed(1)}B < threshold $${DEAD_MARKET_VOLUME_B}B`,
      duration_ms: Date.now() - startTime,
    };
    console.log(`💤 SKIPPED: ${record.reason}`);
    appendHistory(record);
    return;
  }

  console.log(`📊 Market volume: $${volumeB.toFixed(1)}B — pipeline active\n`);

  const steps = [
    { name: "Rug Screener",  script: "screener/rugcheck.js" },
    { name: "Signal Engine", script: "signals/engine.js" },
    { name: "Momentum",      script: "strategies/momentum.js" },
    { name: "Sniper",        script: "strategies/new-launch-sniper.js" },
    { name: "CEX Listings",  script: "strategies/cex-listing-play.js" },
    { name: "Whale Follow",  script: "strategies/whale-follow.js" },
    { name: "Paper Trader",  script: "automation/paper-trader.js" },
    { name: "Alert Bot",     script: "automation/alert-bot.js", args: ["signals"] },
  ];

  const stepResults = [];
  for (const step of steps) {
    process.stdout.write(`  ▶ ${step.name.padEnd(16)}`);
    const result = runScript(resolve(ROOT, step.script), step.args || []);
    const ok = result.exitCode === 0;
    console.log(ok ? " ✅" : ` ❌ (exit ${result.exitCode})`);
    if (!ok && result.stderr) console.log(`    ${result.stderr.slice(0, 200)}`);
    stepResults.push({ name: step.name, ok, exitCode: result.exitCode });
  }

  const record = {
    run_id: runId,
    timestamp: new Date().toISOString(),
    skipped: false,
    market_volume_b: volumeB,
    duration_ms: Date.now() - startTime,
    steps: stepResults,
    errors: stepResults.filter((s) => !s.ok).length,
  };

  appendHistory(record);
  console.log(`\n✅ Pipeline complete in ${record.duration_ms}ms  (${record.errors} errors)`);
  if (record.errors) console.log(`  ⚠️ Check step errors above`);
}

// ---------------------------------------------------------------------------
// Scheduler loop
// ---------------------------------------------------------------------------
async function main() {
  console.log(`\n⏰ Scheduler starting — interval: ${INTERVAL_MS / 60000}min  ${DRY_RUN ? "[DRY RUN]" : ""}`);
  if (RUN_ONCE) {
    console.log("  Mode: single run");
  }

  await runPipeline();

  if (RUN_ONCE) {
    console.log("\nDone (--once mode)");
    process.exit(0);
  }

  console.log(`\nNext run in ${INTERVAL_MS / 60000} minutes...`);
  setInterval(async () => {
    await runPipeline();
    console.log(`Next run in ${INTERVAL_MS / 60000} minutes...`);
  }, INTERVAL_MS);
}

main().catch((e) => {
  console.error("Fatal:", e.message);
  process.exit(1);
});
