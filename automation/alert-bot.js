#!/usr/bin/env node
/**
 * Phase 7 — Alert Bot
 * Sends Telegram alerts on STRONG_BUY signals, Discord webhooks on whale moves,
 * and daily summary reports at 8am.
 * Use --dry-run to log messages without sending.
 */

import { readFileSync, existsSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";
import https from "https";

const __dirname = dirname(fileURLToPath(import.meta.url));
const DRY_RUN = process.argv.includes("--dry-run");

const TELEGRAM_TOKEN = process.env.TELEGRAM_BOT_TOKEN;
const TELEGRAM_CHAT_ID = process.env.TELEGRAM_CHAT_ID;
const DISCORD_WEBHOOK_URL = process.env.DISCORD_WEBHOOK_URL;

// ---------------------------------------------------------------------------
// HTTP POST helper
// ---------------------------------------------------------------------------
function httpPost(url, payload) {
  return new Promise((resolve, reject) => {
    const body = JSON.stringify(payload);
    const u = new URL(url);
    const options = {
      hostname: u.hostname,
      path: u.pathname + u.search,
      method: "POST",
      headers: { "Content-Type": "application/json", "Content-Length": Buffer.byteLength(body) },
    };
    const req = https.request(options, (res) => {
      let data = "";
      res.on("data", (c) => (data += c));
      res.on("end", () => resolve({ status: res.statusCode, body: data }));
    });
    req.on("error", reject);
    req.write(body);
    req.end();
  });
}

// ---------------------------------------------------------------------------
// Telegram message
// ---------------------------------------------------------------------------
async function sendTelegram(message) {
  if (DRY_RUN) {
    console.log(`[TELEGRAM DRY RUN]\n${message}\n`);
    return;
  }
  if (!TELEGRAM_TOKEN || !TELEGRAM_CHAT_ID) {
    console.warn("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set");
    return;
  }
  const url = `https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage`;
  const result = await httpPost(url, {
    chat_id: TELEGRAM_CHAT_ID,
    text: message,
    parse_mode: "Markdown",
  });
  console.log(`Telegram: ${result.status}`);
}

// ---------------------------------------------------------------------------
// Discord webhook
// ---------------------------------------------------------------------------
async function sendDiscord(message) {
  if (DRY_RUN) {
    console.log(`[DISCORD DRY RUN]\n${message}\n`);
    return;
  }
  if (!DISCORD_WEBHOOK_URL) {
    console.warn("DISCORD_WEBHOOK_URL not set");
    return;
  }
  const result = await httpPost(DISCORD_WEBHOOK_URL, { content: message });
  console.log(`Discord: ${result.status}`);
}

// ---------------------------------------------------------------------------
// Alert on STRONG_BUY signals
// ---------------------------------------------------------------------------
async function alertStrongBuys() {
  const signalsPath = resolve(__dirname, "../data/signals.json");
  if (!existsSync(signalsPath)) {
    console.log("No signals file found");
    return;
  }
  const { signals } = JSON.parse(readFileSync(signalsPath, "utf8"));
  const strongBuys = signals.filter((s) => s.signal === "STRONG_BUY");

  for (const s of strongBuys) {
    const msg = [
      `🚀 *STRONG BUY SIGNAL*`,
      ``,
      `*$${s.symbol}* (${s.chain})`,
      `Confidence: ${s.confidence}%`,
      `Entry: ${s.entry_strategy}`,
      `TPs: ${(s.take_profit_targets || []).join(" → ")}`,
      `Stop: ${s.stop_loss}`,
      `Hold: ${s.hold_duration}`,
      ``,
      `📋 ${s.reasoning?.slice(0, 200)}...`,
      ``,
      `_Research only — not financial advice_`,
    ].join("\n");

    await sendTelegram(msg);
  }

  console.log(`Sent ${strongBuys.length} STRONG_BUY alerts`);
}

// ---------------------------------------------------------------------------
// Alert on whale movements
// ---------------------------------------------------------------------------
async function alertWhaleMovements() {
  const whalePath = resolve(__dirname, "../data/whale-activity.json");
  if (!existsSync(whalePath)) {
    console.log("No whale activity file found");
    return;
  }
  const { activity } = JSON.parse(readFileSync(whalePath, "utf8"));
  const actionable = activity.filter((a) => a.recommendation);

  for (const a of actionable) {
    const emoji = a.type === "buy" ? "🐋 BUY" : "🔴 SELL";
    const msg = [
      `${emoji} Whale Alert`,
      ``,
      `**${a.wallet_label || a.wallet}**`,
      `${a.type.toUpperCase()} $${a.symbol} — $${(a.amount_usd || 0).toLocaleString()}`,
      `Chain: ${a.chain}`,
      a.recommendation.action === "MIRROR_BUY"
        ? `💡 Mirror buy: $${a.recommendation.mirror_size_usd} suggested`
        : `⚠️ Consider reducing ${a.symbol} exposure`,
      ``,
      `_Research only_`,
    ].join("\n");

    await sendDiscord(msg);
  }

  console.log(`Sent ${actionable.length} whale alerts`);
}

// ---------------------------------------------------------------------------
// Daily 8am summary
// ---------------------------------------------------------------------------
async function dailySummary() {
  const portfolioPath = resolve(__dirname, "../data/portfolio-tracker.json");
  const portfolio = existsSync(portfolioPath)
    ? JSON.parse(readFileSync(portfolioPath, "utf8"))
    : { total_capital: 10000, deployed: 0, cash_reserve: 10000, open_positions: [], win_rate: "—" };

  const signalsPath = resolve(__dirname, "../data/signals.json");
  const signals = existsSync(signalsPath)
    ? JSON.parse(readFileSync(signalsPath, "utf8")).signals
    : [];

  const buys = signals.filter((s) => ["STRONG_BUY", "BUY"].includes(s.signal));

  const msg = [
    `📊 *Daily Report — ${new Date().toLocaleDateString()}*`,
    ``,
    `💼 Portfolio`,
    `  Capital: $${(portfolio.total_capital || 0).toLocaleString()}`,
    `  Deployed: $${(portfolio.deployed || 0).toFixed(2)}`,
    `  Positions: ${(portfolio.open_positions || []).length}`,
    `  Win Rate: ${portfolio.win_rate || "—"}`,
    ``,
    `🔥 Top Signals Today`,
    ...buys.slice(0, 5).map((s) => `  • $${s.symbol} (${s.chain}) — ${s.signal} ${s.confidence}%`),
    buys.length === 0 ? "  No buy signals today" : "",
    ``,
    `_Full report: open dashboard/index.html_`,
  ]
    .filter((l) => l !== undefined)
    .join("\n");

  await sendTelegram(msg);
  await sendDiscord(msg);
  console.log("Daily summary sent");
}

// ---------------------------------------------------------------------------
// Main — determine which alert to fire based on CLI args
// ---------------------------------------------------------------------------
const mode = process.argv[2] || "all";

async function main() {
  console.log(`\n📣 Alert Bot — ${DRY_RUN ? "DRY RUN" : "LIVE"}  mode: ${mode}\n`);
  if (mode === "signals" || mode === "all") await alertStrongBuys();
  if (mode === "whales"  || mode === "all") await alertWhaleMovements();
  if (mode === "daily"   || mode === "all") await dailySummary();
}

main().catch((e) => {
  console.error("Fatal:", e.message);
  process.exit(1);
});
