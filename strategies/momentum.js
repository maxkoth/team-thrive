#!/usr/bin/env node
/**
 * Phase 4 — Momentum Strategy
 * Detects coins up >50% in 1h with rising volume.
 * Entry: market buy on confirmation candle.
 * Exit: trailing stop 15% below peak.
 * Use --dry-run to run against mock data.
 */

import { writeFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const DRY_RUN = process.argv.includes("--dry-run");

// ---------------------------------------------------------------------------
// Mock OHLCV data generator (production: wire to DEXScreener / GeckoTerminal API)
// ---------------------------------------------------------------------------
function fetchMockCandles(symbol, count = 24) {
  let price = 0.001 + Math.random() * 0.01;
  const candles = [];
  for (let i = count; i >= 0; i--) {
    const change = (Math.random() - 0.45) * 0.12;
    price = Math.max(0.000001, price * (1 + change));
    candles.push({
      timestamp: new Date(Date.now() - i * 3600000).toISOString(),
      open: price * (1 - Math.random() * 0.03),
      high: price * (1 + Math.random() * 0.05),
      low: price * (1 - Math.random() * 0.05),
      close: price,
      volume: 100000 + Math.random() * 900000,
    });
  }
  return candles;
}

// ---------------------------------------------------------------------------
// Detect momentum signal
// ---------------------------------------------------------------------------
function detectMomentum(symbol, candles) {
  const latest = candles[candles.length - 1];
  const oneHourAgo = candles[candles.length - 2];

  const priceChange1h =
    ((latest.close - oneHourAgo.open) / oneHourAgo.open) * 100;
  const avgVolume =
    candles.slice(-8, -1).reduce((s, c) => s + c.volume, 0) / 7;
  const volumeRatio = latest.volume / avgVolume;

  // 20-period simple moving average
  const sma20 =
    candles.slice(-20).reduce((s, c) => s + c.close, 0) / Math.min(20, candles.length);
  const aboveSma = latest.close > sma20;

  const triggered = priceChange1h >= 50 && volumeRatio >= 1.5 && aboveSma;

  let peakPrice = Math.max(...candles.slice(-4).map((c) => c.high));
  const trailingStop = peakPrice * 0.85;

  return {
    symbol,
    triggered,
    price_change_1h_pct: priceChange1h.toFixed(2),
    volume_ratio: volumeRatio.toFixed(2),
    above_sma20: aboveSma,
    current_price: latest.close,
    entry_price: triggered ? latest.close : null,
    trailing_stop: triggered ? trailingStop : null,
    trailing_stop_pct: -15,
    peak_price: peakPrice,
    take_profit_1: triggered ? latest.close * 1.3 : null,
    take_profit_2: triggered ? latest.close * 1.7 : null,
    take_profit_3: triggered ? latest.close * 2.5 : null,
    timestamp: new Date().toISOString(),
  };
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------
function main() {
  console.log(`\n📈 Momentum Strategy — ${DRY_RUN ? "DRY RUN" : "LIVE"}\n`);

  const watchlist = ["PUNCH", "FRENS", "COINCOIN", "GOATSEUS", "BONK"];
  const results = [];

  for (const symbol of watchlist) {
    const candles = fetchMockCandles(symbol);
    const signal = detectMomentum(symbol, candles);
    results.push(signal);

    const icon = signal.triggered ? "🚀 SIGNAL" : "   quiet";
    console.log(
      `${icon}  ${symbol.padEnd(12)} 1h: ${signal.price_change_1h_pct.padStart(7)}%  vol_ratio: ${signal.volume_ratio}x  ${signal.triggered ? `entry: $${signal.entry_price?.toFixed(8)}  stop: $${signal.trailing_stop?.toFixed(8)}` : ""}`
    );
  }

  const triggered = results.filter((r) => r.triggered);
  console.log(`\n${triggered.length} momentum signals fired`);

  const outPath = resolve(__dirname, "../data/momentum-signals.json");
  writeFileSync(
    outPath,
    JSON.stringify({ generated_at: new Date().toISOString(), dry_run: DRY_RUN, signals: results }, null, 2)
  );
  console.log(`Saved → ${outPath}`);
}

main();
