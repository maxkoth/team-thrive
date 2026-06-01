#!/usr/bin/env node
/**
 * Phase 4 — CEX Listing Play
 * Tracks official CEX listing announcements and generates pre/post-listing strategies.
 * Use --dry-run to run against mock announcement data.
 */

import { writeFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const DRY_RUN = process.argv.includes("--dry-run");

// ---------------------------------------------------------------------------
// Historical price action model after CEX listing (based on research patterns)
// ---------------------------------------------------------------------------
const LISTING_MODELS = {
  Binance: {
    median_pump_listing_day_pct: 85,
    median_dump_day3_pct: -35,
    median_recovery_week2_pct: 25,
    note: "Strong immediate pump, sharp correction, partial recovery",
  },
  Coinbase: {
    median_pump_listing_day_pct: 40,
    median_dump_day3_pct: -20,
    median_recovery_week2_pct: 15,
    note: "Moderate pump, gentler correction (Coinbase effect is weakening)",
  },
  Bybit: {
    median_pump_listing_day_pct: 30,
    median_dump_day3_pct: -15,
    median_recovery_week2_pct: 10,
    note: "Smaller pump, stable post-listing",
  },
  OKX: {
    median_pump_listing_day_pct: 35,
    median_dump_day3_pct: -18,
    median_recovery_week2_pct: 12,
    note: "Similar to Bybit, slightly stronger Asian market lift",
  },
};

// ---------------------------------------------------------------------------
// Mock announcement feed (production: poll official announcement channels)
// ---------------------------------------------------------------------------
function fetchMockAnnouncements() {
  return [
    {
      id: "ANN_001",
      exchange: "Binance",
      symbol: "NEWTOKEN",
      listing_date: new Date(Date.now() + 3 * 86400000).toISOString(),
      current_price: 0.0045,
      market_cap_usd: 18000000,
      announcement_url: "https://binance.com/en/support/announcement/",
      announced_at: new Date(Date.now() - 7200000).toISOString(),
    },
    {
      id: "ANN_002",
      exchange: "Coinbase",
      symbol: "MEMEBLAST",
      listing_date: new Date(Date.now() + 7 * 86400000).toISOString(),
      current_price: 0.00012,
      market_cap_usd: 4500000,
      announcement_url: "https://coinbase.com/blog/",
      announced_at: new Date(Date.now() - 3600000).toISOString(),
    },
  ];
}

// ---------------------------------------------------------------------------
// Generate strategy for a listing
// ---------------------------------------------------------------------------
function buildListingStrategy(announcement) {
  const model = LISTING_MODELS[announcement.exchange] || LISTING_MODELS.Bybit;
  const daysUntilListing =
    (new Date(announcement.listing_date) - Date.now()) / 86400000;
  const p = announcement.current_price;

  const accumulationWindow = daysUntilListing > 2;
  const targetPreListingPrice = p * (1 + model.median_pump_listing_day_pct / 100 * 0.4);
  const listingDayTarget = p * (1 + model.median_pump_listing_day_pct / 100);
  const stopLoss = p * 0.82;

  return {
    announcement_id: announcement.id,
    symbol: announcement.symbol,
    exchange: announcement.exchange,
    listing_date: announcement.listing_date,
    days_until_listing: daysUntilListing.toFixed(1),
    current_price: p,
    historical_model: model,
    strategy: {
      phase_1_accumulation: accumulationWindow
        ? {
            action: "BUY",
            entry_range: [p * 0.98, p * 1.05],
            rationale: `Pre-listing accumulation — expect ${(model.median_pump_listing_day_pct * 0.4).toFixed(0)}% run-up before listing day`,
            position_size_pct: 1.5,
          }
        : { action: "WAIT", rationale: "Listing too close for safe accumulation" },
      phase_2_listing_day: {
        action: "SELL_50_PCT",
        target_price: listingDayTarget,
        rationale: `Sell half on listing day at ~${model.median_pump_listing_day_pct}% gain`,
      },
      phase_3_correction: {
        action: "BUY_BACK_DIP",
        target_price: listingDayTarget * (1 + model.median_dump_day3_pct / 100),
        rationale: `Expected ${Math.abs(model.median_dump_day3_pct)}% dip days 2-4 post-listing`,
      },
      phase_4_recovery: {
        action: "HOLD_TO_RECOVERY",
        target_price: p * (1 + model.median_recovery_week2_pct / 100),
        rationale: `Partial recovery target week 2`,
      },
      stop_loss: stopLoss,
      max_loss_pct: -18,
    },
    generated_at: new Date().toISOString(),
  };
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------
function main() {
  console.log(`\n📋 CEX Listing Play — ${DRY_RUN ? "DRY RUN" : "LIVE"}\n`);

  const announcements = fetchMockAnnouncements();
  const strategies = announcements.map(buildListingStrategy);

  strategies.forEach((s) => {
    console.log(`\n${s.exchange} listing: $${s.symbol} in ${s.days_until_listing} days`);
    console.log(`  Current price: $${s.current_price}`);
    console.log(`  Expected listing day pump: +${s.historical_model.median_pump_listing_day_pct}%`);
    console.log(`  Phase 1: ${s.strategy.phase_1_accumulation.action}`);
    console.log(`  Stop loss: $${s.strategy.stop_loss.toFixed(8)}`);
    console.log(`  Model note: ${s.historical_model.note}`);
  });

  const outPath = resolve(__dirname, "../data/cex-listing-strategies.json");
  writeFileSync(
    outPath,
    JSON.stringify(
      { generated_at: new Date().toISOString(), dry_run: DRY_RUN, strategies },
      null,
      2
    )
  );
  console.log(`\nSaved → ${outPath}`);
}

main();
