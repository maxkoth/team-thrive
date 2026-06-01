#!/usr/bin/env node
/**
 * Phase 7 — Paper Trader
 * Simulates all STRONG_BUY signals with $1,000 virtual per trade.
 * Tracks paper performance and generates weekly accuracy reports.
 * Use --dry-run to simulate without writing state.
 * Use --report to print current accuracy report.
 */

import { readFileSync, writeFileSync, existsSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const DRY_RUN = process.argv.includes("--dry-run");
const REPORT_MODE = process.argv.includes("--report");

const PAPER_STATE_PATH = resolve(__dirname, "../data/paper-trades.json");
const TRADE_SIZE_USD = 1000;

// ---------------------------------------------------------------------------
// Load / save paper trading state
// ---------------------------------------------------------------------------
function loadState() {
  if (existsSync(PAPER_STATE_PATH)) {
    return JSON.parse(readFileSync(PAPER_STATE_PATH, "utf8"));
  }
  return { trades: [], virtual_capital: 10000, deployed: 0 };
}

function saveState(state) {
  if (!DRY_RUN) {
    writeFileSync(PAPER_STATE_PATH, JSON.stringify(state, null, 2));
  }
}

// ---------------------------------------------------------------------------
// Simulate price outcome (production: fetch real price after N days)
// ---------------------------------------------------------------------------
function simulatePriceOutcome(signal) {
  // Simple probabilistic model based on signal confidence
  const conf = signal.confidence || 60;
  const winProb = conf / 100;
  const won = Math.random() < winProb;

  // Return distribution: wins avg +55%, losses avg -22%
  let returnPct;
  if (won) {
    returnPct = 20 + Math.random() * 120;
  } else {
    returnPct = -(5 + Math.random() * 40);
  }

  return { won, returnPct: parseFloat(returnPct.toFixed(1)) };
}

// ---------------------------------------------------------------------------
// Simulate entry for a new signal
// ---------------------------------------------------------------------------
function simulateEntry(signal, state) {
  const existing = state.trades.find(
    (t) => t.symbol === signal.symbol && t.status === "open"
  );
  if (existing) {
    console.log(`  Skip ${signal.symbol} — already open paper position`);
    return state;
  }

  const trade = {
    id: `PAPER_${Date.now()}_${signal.symbol}`,
    symbol: signal.symbol,
    chain: signal.chain,
    signal: signal.signal,
    confidence: signal.confidence,
    entry_date: new Date().toISOString(),
    entry_price: signal.entry_price || null,
    position_size_usd: TRADE_SIZE_USD,
    status: "open",
    take_profit_targets: signal.take_profit_targets,
    stop_loss: signal.stop_loss,
    hold_duration: signal.hold_duration,
    outcome: null,
  };

  console.log(`  📝 Paper buy: $${signal.symbol} ($${TRADE_SIZE_USD} virtual)`);
  return {
    ...state,
    trades: [...state.trades, trade],
    deployed: state.deployed + TRADE_SIZE_USD,
    virtual_capital: state.virtual_capital - TRADE_SIZE_USD,
  };
}

// ---------------------------------------------------------------------------
// Resolve open trades older than their hold_duration
// ---------------------------------------------------------------------------
function resolveMaturedTrades(state) {
  const now = Date.now();
  const updated = state.trades.map((t) => {
    if (t.status !== "open") return t;
    const ageDays = (now - new Date(t.entry_date).getTime()) / 86400000;

    const matureAfterDays =
      t.hold_duration?.includes("scalp") ? 0.02
      : t.hold_duration?.includes("swing") ? 3
      : 7;

    if (ageDays < matureAfterDays) return t;

    const { won, returnPct } = simulatePriceOutcome(t);
    const pnlUsd = t.position_size_usd * (returnPct / 100);
    return {
      ...t,
      status: "closed",
      close_date: new Date().toISOString(),
      return_pct: returnPct,
      pnl_usd: parseFloat(pnlUsd.toFixed(2)),
      outcome: won ? "WIN" : "LOSS",
    };
  });

  const closed = updated.filter((t) => t.status === "closed" && !state.trades.find(s => s.id === t.id && s.status === "closed"));
  closed.forEach((t) => {
    const icon = t.outcome === "WIN" ? "🟢" : "🔴";
    console.log(
      `  ${icon} Paper closed: $${t.symbol} ${t.return_pct >= 0 ? "+" : ""}${t.return_pct}% ($${t.pnl_usd})`
    );
  });

  const totalDeployed = updated.filter((t) => t.status === "open").length * TRADE_SIZE_USD;
  const realizedPnl = updated
    .filter((t) => t.status === "closed")
    .reduce((s, t) => s + (t.pnl_usd || 0), 0);

  return {
    ...state,
    trades: updated,
    deployed: totalDeployed,
    virtual_capital: 10000 + realizedPnl - totalDeployed,
  };
}

// ---------------------------------------------------------------------------
// Generate accuracy report
// ---------------------------------------------------------------------------
function generateReport(state) {
  const closed = state.trades.filter((t) => t.status === "closed");
  if (!closed.length) {
    console.log("No closed paper trades yet");
    return;
  }

  const wins = closed.filter((t) => t.outcome === "WIN");
  const winRate = (wins.length / closed.length * 100).toFixed(1);
  const totalPnl = closed.reduce((s, t) => s + (t.pnl_usd || 0), 0);
  const avgReturn = (closed.reduce((s, t) => s + (t.return_pct || 0), 0) / closed.length).toFixed(1);

  const best = closed.reduce((b, t) => (!b || t.return_pct > b.return_pct ? t : b), null);
  const worst = closed.reduce((w, t) => (!w || t.return_pct < w.return_pct ? t : w), null);

  // Break down by signal type
  const bySignal = {};
  closed.forEach((t) => {
    if (!bySignal[t.signal]) bySignal[t.signal] = { count: 0, wins: 0, totalReturn: 0 };
    bySignal[t.signal].count++;
    if (t.outcome === "WIN") bySignal[t.signal].wins++;
    bySignal[t.signal].totalReturn += t.return_pct || 0;
  });

  console.log("\n📈 Paper Trading Accuracy Report");
  console.log("═".repeat(50));
  console.log(`  Total Trades:     ${closed.length}`);
  console.log(`  Win Rate:         ${winRate}%`);
  console.log(`  Total P&L:        $${totalPnl.toFixed(2)}`);
  console.log(`  Avg Return:       ${avgReturn}%`);
  console.log(`  Virtual Capital:  $${state.virtual_capital.toFixed(2)}`);
  console.log(`  Best Trade:       $${best?.symbol} +${best?.return_pct}%`);
  console.log(`  Worst Trade:      $${worst?.symbol} ${worst?.return_pct}%`);
  console.log(`\n  By Signal Type:`);
  Object.entries(bySignal).forEach(([sig, d]) => {
    console.log(`    ${sig.padEnd(15)} ${d.count} trades  win: ${(d.wins/d.count*100).toFixed(0)}%  avg: ${(d.totalReturn/d.count).toFixed(1)}%`);
  });

  const outPath = resolve(__dirname, "../data/paper-report.json");
  writeFileSync(outPath, JSON.stringify({
    generated_at: new Date().toISOString(),
    closed_trades: closed.length,
    win_rate: winRate + "%",
    total_pnl_usd: totalPnl.toFixed(2),
    avg_return_pct: avgReturn,
    virtual_capital: state.virtual_capital,
    best_trade: best,
    worst_trade: worst,
    by_signal: bySignal,
  }, null, 2));
  console.log(`\nReport saved → ${outPath}`);
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------
async function main() {
  console.log(`\n📝 Paper Trader — ${DRY_RUN ? "DRY RUN" : "LIVE"}\n`);

  let state = loadState();
  state = resolveMaturedTrades(state);

  if (REPORT_MODE) {
    generateReport(state);
    saveState(state);
    return;
  }

  // Load new signals and enter STRONG_BUY positions
  const signalsPath = resolve(__dirname, "../data/signals.json");
  if (!existsSync(signalsPath)) {
    console.log("No signals file — run signals/engine.js first");
    saveState(state);
    return;
  }

  const { signals } = JSON.parse(readFileSync(signalsPath, "utf8"));
  const strongBuys = signals.filter((s) => s.signal === "STRONG_BUY");

  console.log(`Processing ${strongBuys.length} STRONG_BUY signals...`);
  for (const signal of strongBuys) {
    state = simulateEntry(signal, state);
  }

  console.log(`\nOpen paper positions: ${state.trades.filter(t => t.status === "open").length}`);
  console.log(`Virtual capital: $${state.virtual_capital.toFixed(2)}`);

  saveState(state);
  console.log(`State saved → ${PAPER_STATE_PATH}`);
}

main().catch((e) => {
  console.error("Fatal:", e.message);
  process.exit(1);
});
