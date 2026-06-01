#!/usr/bin/env node
/**
 * Phase 4 — Whale Follow Strategy
 * Monitors known alpha wallets and suggests mirror trades.
 * Use --dry-run to simulate with mock on-chain events.
 */

import { writeFileSync, readFileSync, existsSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const DRY_RUN = process.argv.includes("--dry-run");

// ---------------------------------------------------------------------------
// Configurable alpha wallet list (add known smart money wallets here)
// ---------------------------------------------------------------------------
const ALPHA_WALLETS = [
  { address: "WALLET_ALPHA_1", label: "Solana Smart Money #1", chain: "Solana" },
  { address: "WALLET_ALPHA_2", label: "Base Degen Whale", chain: "Base" },
  { address: "WALLET_ALPHA_3", label: "Known Meme Trader", chain: "Solana" },
];

const MIN_POSITION_USD = 10000;

// ---------------------------------------------------------------------------
// Mock on-chain transaction events (production: Nansen / Arkham webhooks)
// ---------------------------------------------------------------------------
function fetchMockWhaleActivity() {
  return [
    {
      wallet: "WALLET_ALPHA_1",
      type: "buy",
      symbol: "PUNCH",
      amount_usd: 47000,
      token_amount: 12000000,
      price_per_token: 0.00000391,
      chain: "Solana",
      tx_hash: "TXHASH_001",
      timestamp: new Date(Date.now() - 420000).toISOString(),
    },
    {
      wallet: "WALLET_ALPHA_2",
      type: "buy",
      symbol: "COINCOIN",
      amount_usd: 8000,
      token_amount: 5000000,
      price_per_token: 0.0000016,
      chain: "Base",
      tx_hash: "TXHASH_002",
      timestamp: new Date(Date.now() - 180000).toISOString(),
    },
    {
      wallet: "WALLET_ALPHA_3",
      type: "sell",
      symbol: "FRENS",
      amount_usd: 23000,
      token_amount: 8000000,
      price_per_token: 0.000002875,
      chain: "Solana",
      tx_hash: "TXHASH_003",
      timestamp: new Date(Date.now() - 60000).toISOString(),
    },
    {
      wallet: "WALLET_ALPHA_1",
      type: "buy",
      symbol: "GOATSEUS",
      amount_usd: 18500,
      token_amount: 950000,
      price_per_token: 0.01947,
      chain: "Solana",
      tx_hash: "TXHASH_004",
      timestamp: new Date(Date.now() - 30000).toISOString(),
    },
  ];
}

// ---------------------------------------------------------------------------
// Calculate mirror trade sizing (2% max portfolio risk rule)
// ---------------------------------------------------------------------------
function calcMirrorSize(whaleAmountUsd, portfolioUsd, portfolioPct = 0.5) {
  const maxRisk = portfolioUsd * 0.02;
  const proportional = portfolioUsd * (portfolioPct / 100);
  return Math.min(maxRisk, proportional);
}

const PORTFOLIO_USD = 10000;

// ---------------------------------------------------------------------------
// Process whale activity
// ---------------------------------------------------------------------------
function processActivity(activity) {
  const wallet = ALPHA_WALLETS.find((w) => w.address === activity.wallet);
  const isAboveThreshold = activity.amount_usd >= MIN_POSITION_USD;
  const isBuy = activity.type === "buy";

  let recommendation = null;
  if (isAboveThreshold && isBuy) {
    const mirrorSize = calcMirrorSize(activity.amount_usd, PORTFOLIO_USD);
    const tokensToBuy = mirrorSize / activity.price_per_token;
    recommendation = {
      action: "MIRROR_BUY",
      symbol: activity.symbol,
      chain: activity.chain,
      mirror_size_usd: Math.round(mirrorSize),
      tokens_to_buy: Math.round(tokensToBuy),
      entry_price: activity.price_per_token,
      stop_loss: activity.price_per_token * 0.82,
      take_profit_1: activity.price_per_token * 1.4,
      take_profit_2: activity.price_per_token * 2.2,
      whale_amount_usd: activity.amount_usd,
      whale_label: wallet?.label || activity.wallet,
      rationale: `${wallet?.label} bought $${activity.amount_usd.toLocaleString()} — mirror at 0.5% portfolio`,
    };
  } else if (isAboveThreshold && !isBuy) {
    recommendation = {
      action: "ALERT_WHALE_SELL",
      symbol: activity.symbol,
      chain: activity.chain,
      whale_label: wallet?.label || activity.wallet,
      whale_amount_usd: activity.amount_usd,
      rationale: `${wallet?.label} SOLD $${activity.amount_usd.toLocaleString()} — consider reducing exposure`,
    };
  }

  return {
    ...activity,
    wallet_label: wallet?.label,
    above_threshold: isAboveThreshold,
    recommendation,
    processed_at: new Date().toISOString(),
  };
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------
function main() {
  console.log(`\n🐋 Whale Follow — ${DRY_RUN ? "DRY RUN" : "LIVE"}\n`);
  console.log(`Monitoring ${ALPHA_WALLETS.length} wallets  |  min position: $${MIN_POSITION_USD.toLocaleString()}\n`);

  const activity = fetchMockWhaleActivity();
  const processed = activity.map(processActivity);

  processed.forEach((a) => {
    const icon =
      a.recommendation?.action === "MIRROR_BUY"
        ? "🐋 MIRROR"
        : a.recommendation?.action === "ALERT_WHALE_SELL"
        ? "🔴 SELL  "
        : "   skip ";
    console.log(
      `${icon}  ${a.type.toUpperCase().padEnd(4)} ${a.symbol.padEnd(12)} $${a.amount_usd.toLocaleString().padStart(9)}  [${a.wallet_label || a.wallet}]`
    );
    if (a.recommendation) {
      console.log(`         ${a.recommendation.rationale}`);
    }
  });

  const actionable = processed.filter((a) => a.recommendation);
  console.log(`\n${actionable.length} actionable whale events`);

  const outPath = resolve(__dirname, "../data/whale-activity.json");
  writeFileSync(
    outPath,
    JSON.stringify(
      { generated_at: new Date().toISOString(), dry_run: DRY_RUN, activity: processed },
      null,
      2
    )
  );
  console.log(`Saved → ${outPath}`);
}

main();
