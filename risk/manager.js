#!/usr/bin/env node
/**
 * Phase 5 — Portfolio & Risk Manager
 * Enforces position sizing rules, max exposure limits, and drawdown halts.
 * Use --dry-run to simulate without modifying portfolio state.
 */

import { readFileSync, writeFileSync, existsSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const DRY_RUN = process.argv.includes("--dry-run");

const TRACKER_PATH = resolve(__dirname, "../risk/portfolio-tracker.json");
const DATA_PATH = resolve(__dirname, "../data/portfolio-tracker.json");

// ---------------------------------------------------------------------------
// Risk rules
// ---------------------------------------------------------------------------
const RULES = {
  maxRiskPerTradePct: 2,
  maxOpenPositions: 5,
  haltDrawdownPct: 15,
  haltLookbackDays: 7,
};

// ---------------------------------------------------------------------------
// Load or initialise portfolio state
// ---------------------------------------------------------------------------
function loadPortfolio() {
  const path = existsSync(DATA_PATH) ? DATA_PATH : TRACKER_PATH;
  if (existsSync(path)) {
    return JSON.parse(readFileSync(path, "utf8"));
  }
  return {
    total_capital: 10000,
    deployed: 0,
    cash_reserve: 10000,
    open_positions: [],
    closed_trades: [],
    win_rate: null,
    avg_return_per_trade: null,
    best_trade: null,
    worst_trade: null,
    halted: false,
    halt_reason: null,
    last_updated: new Date().toISOString(),
  };
}

// ---------------------------------------------------------------------------
// Calculate position size from stop loss distance
// ---------------------------------------------------------------------------
function calcPositionSize(portfolio, entryPrice, stopLossPrice) {
  const riskAmount = portfolio.total_capital * (RULES.maxRiskPerTradePct / 100);
  const riskPerToken = Math.abs(entryPrice - stopLossPrice);
  if (riskPerToken === 0) return 0;
  const tokenQty = riskAmount / riskPerToken;
  const positionUsd = tokenQty * entryPrice;
  return {
    risk_amount_usd: riskAmount,
    position_size_usd: positionUsd,
    token_quantity: tokenQty,
  };
}

// ---------------------------------------------------------------------------
// Check drawdown halt condition
// ---------------------------------------------------------------------------
function checkHaltCondition(portfolio) {
  const cutoff = new Date(Date.now() - RULES.haltLookbackDays * 86400000);
  const recentTrades = portfolio.closed_trades.filter(
    (t) => new Date(t.closed_at) > cutoff
  );
  if (recentTrades.length === 0) return null;
  const totalPnl = recentTrades.reduce((s, t) => s + t.pnl_pct, 0) / recentTrades.length;
  if (totalPnl <= -RULES.haltDrawdownPct) {
    return `Avg PnL ${totalPnl.toFixed(1)}% over last ${RULES.haltLookbackDays}d exceeds halt threshold`;
  }
  return null;
}

// ---------------------------------------------------------------------------
// Evaluate a prospective trade
// ---------------------------------------------------------------------------
function evaluateTrade(portfolio, trade) {
  const errors = [];
  const warnings = [];

  if (portfolio.halted) {
    errors.push(`Trading HALTED: ${portfolio.halt_reason}`);
  }
  if (portfolio.open_positions.length >= RULES.maxOpenPositions) {
    errors.push(`Max open positions reached (${RULES.maxOpenPositions})`);
  }

  const existing = portfolio.open_positions.find((p) => p.symbol === trade.symbol);
  if (existing) {
    warnings.push(`Already have an open position in ${trade.symbol}`);
  }

  const sizing = calcPositionSize(portfolio, trade.entry_price, trade.stop_loss);
  if (sizing.position_size_usd > portfolio.cash_reserve) {
    errors.push(
      `Insufficient cash: need $${sizing.position_size_usd.toFixed(0)}, have $${portfolio.cash_reserve.toFixed(0)}`
    );
  }

  const haltReason = checkHaltCondition(portfolio);
  if (haltReason) warnings.push(`Near halt condition: ${haltReason}`);

  return {
    approved: errors.length === 0,
    errors,
    warnings,
    recommended_sizing: sizing,
  };
}

// ---------------------------------------------------------------------------
// Open a position
// ---------------------------------------------------------------------------
function openPosition(portfolio, trade) {
  const evaluation = evaluateTrade(portfolio, trade);
  if (!evaluation.approved) {
    console.log(`❌ Trade rejected: ${evaluation.errors.join("; ")}`);
    return portfolio;
  }

  const sizing = evaluation.recommended_sizing;
  const position = {
    id: `POS_${Date.now()}`,
    symbol: trade.symbol,
    chain: trade.chain,
    entry_price: trade.entry_price,
    entry_date: new Date().toISOString(),
    position_size_usd: sizing.position_size_usd,
    token_quantity: sizing.token_quantity,
    stop_loss: trade.stop_loss,
    take_profit_1: trade.take_profit_1,
    take_profit_2: trade.take_profit_2,
    current_price: trade.entry_price,
    unrealized_pnl_usd: 0,
    unrealized_pnl_pct: 0,
  };

  const updated = {
    ...portfolio,
    deployed: portfolio.deployed + sizing.position_size_usd,
    cash_reserve: portfolio.cash_reserve - sizing.position_size_usd,
    open_positions: [...portfolio.open_positions, position],
    last_updated: new Date().toISOString(),
  };

  if (evaluation.warnings.length) {
    evaluation.warnings.forEach((w) => console.log(`  ⚠️  ${w}`));
  }
  console.log(`✅ Opened ${trade.symbol}: $${sizing.position_size_usd.toFixed(2)} (${sizing.token_quantity.toFixed(0)} tokens)`);
  return updated;
}

// ---------------------------------------------------------------------------
// Close a position
// ---------------------------------------------------------------------------
function closePosition(portfolio, positionId, closePrice) {
  const pos = portfolio.open_positions.find((p) => p.id === positionId);
  if (!pos) {
    console.log(`Position ${positionId} not found`);
    return portfolio;
  }

  const pnlUsd = (closePrice - pos.entry_price) * pos.token_quantity;
  const pnlPct = ((closePrice - pos.entry_price) / pos.entry_price) * 100;

  const closedTrade = {
    ...pos,
    close_price: closePrice,
    closed_at: new Date().toISOString(),
    pnl_usd: pnlUsd,
    pnl_pct: pnlPct,
  };

  const closed = [...portfolio.closed_trades, closedTrade];
  const winCount = closed.filter((t) => t.pnl_usd > 0).length;
  const avgReturn = closed.reduce((s, t) => s + t.pnl_pct, 0) / closed.length;
  const best = closed.reduce((b, t) => (!b || t.pnl_pct > b.pnl_pct ? t : b), null);
  const worst = closed.reduce((w, t) => (!w || t.pnl_pct < w.pnl_pct ? t : w), null);

  const updatedCapital = portfolio.total_capital + pnlUsd;
  const updated = {
    ...portfolio,
    total_capital: updatedCapital,
    deployed: portfolio.deployed - pos.position_size_usd,
    cash_reserve: portfolio.cash_reserve + pos.position_size_usd + pnlUsd,
    open_positions: portfolio.open_positions.filter((p) => p.id !== positionId),
    closed_trades: closed,
    win_rate: ((winCount / closed.length) * 100).toFixed(1) + "%",
    avg_return_per_trade: avgReturn.toFixed(2) + "%",
    best_trade: best,
    worst_trade: worst,
    last_updated: new Date().toISOString(),
  };

  const icon = pnlUsd >= 0 ? "🟢" : "🔴";
  console.log(
    `${icon} Closed ${pos.symbol}: ${pnlPct >= 0 ? "+" : ""}${pnlPct.toFixed(1)}%  ($${pnlUsd.toFixed(2)})`
  );

  // Check halt condition after closing
  const haltReason = checkHaltCondition(updated);
  if (haltReason && !updated.halted) {
    console.log(`🚨 HALT TRIGGERED: ${haltReason}`);
    updated.halted = true;
    updated.halt_reason = haltReason;
  }

  return updated;
}

// ---------------------------------------------------------------------------
// Save portfolio state
// ---------------------------------------------------------------------------
function savePortfolio(portfolio) {
  if (!DRY_RUN) {
    writeFileSync(DATA_PATH, JSON.stringify(portfolio, null, 2));
    writeFileSync(TRACKER_PATH, JSON.stringify(portfolio, null, 2));
  }
  return portfolio;
}

// ---------------------------------------------------------------------------
// Print portfolio summary
// ---------------------------------------------------------------------------
function printSummary(portfolio) {
  console.log("\n📊 Portfolio Summary");
  console.log("─".repeat(50));
  console.log(`  Total Capital:    $${portfolio.total_capital.toLocaleString()}`);
  console.log(`  Deployed:         $${portfolio.deployed.toFixed(2)}`);
  console.log(`  Cash Reserve:     $${portfolio.cash_reserve.toFixed(2)}`);
  console.log(`  Open Positions:   ${portfolio.open_positions.length}/${RULES.maxOpenPositions}`);
  console.log(`  Closed Trades:    ${portfolio.closed_trades.length}`);
  console.log(`  Win Rate:         ${portfolio.win_rate || "N/A"}`);
  console.log(`  Avg Return:       ${portfolio.avg_return_per_trade || "N/A"}`);
  if (portfolio.halted) console.log(`  🚨 HALTED: ${portfolio.halt_reason}`);
  if (portfolio.open_positions.length) {
    console.log("\n  Open Positions:");
    portfolio.open_positions.forEach((p) =>
      console.log(
        `    ${p.symbol.padEnd(12)} $${p.position_size_usd.toFixed(2).padStart(9)}  entry: $${p.entry_price}  stop: $${p.stop_loss}`
      )
    );
  }
}

// ---------------------------------------------------------------------------
// Demo run
// ---------------------------------------------------------------------------
function demo() {
  console.log(`\n💼 Risk Manager — ${DRY_RUN ? "DRY RUN" : "LIVE"}\n`);

  let portfolio = loadPortfolio();

  // Simulate opening 3 positions
  portfolio = openPosition(portfolio, {
    symbol: "PUNCH",
    chain: "Solana",
    entry_price: 0.00000391,
    stop_loss: 0.0000032,
    take_profit_1: 0.0000055,
    take_profit_2: 0.0000085,
  });

  portfolio = openPosition(portfolio, {
    symbol: "GOATSEUS",
    chain: "Solana",
    entry_price: 0.01947,
    stop_loss: 0.016,
    take_profit_1: 0.027,
    take_profit_2: 0.042,
  });

  portfolio = openPosition(portfolio, {
    symbol: "FRENS",
    chain: "Solana",
    entry_price: 0.000002875,
    stop_loss: 0.0000023,
    take_profit_1: 0.0000042,
    take_profit_2: 0.0000068,
  });

  // Close one at profit, one at loss
  const pos1 = portfolio.open_positions[0];
  const pos2 = portfolio.open_positions[1];
  if (pos1) portfolio = closePosition(portfolio, pos1.id, pos1.entry_price * 1.6);
  if (pos2) portfolio = closePosition(portfolio, pos2.id, pos2.entry_price * 0.8);

  printSummary(portfolio);
  savePortfolio(portfolio);

  console.log(`\nPortfolio saved → ${DATA_PATH}`);
}

demo();

export { loadPortfolio, savePortfolio, openPosition, closePosition, evaluateTrade, calcPositionSize };
