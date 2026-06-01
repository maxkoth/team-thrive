#!/usr/bin/env node
/**
 * Phase 3 — AI Signal Engine
 * Feeds screened coins to Claude claude-sonnet-4-20250514 and returns structured trading signals.
 * Use --dry-run to skip API calls and return mock signals.
 */

import Anthropic from "@anthropic-ai/sdk";
import { readFileSync, writeFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const DRY_RUN = process.argv.includes("--dry-run");

const client = DRY_RUN ? null : new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

// ---------------------------------------------------------------------------
// Signal schema expected from Claude
// ---------------------------------------------------------------------------
const SIGNAL_SCHEMA = `{
  "signal": "STRONG_BUY | BUY | WATCH | AVOID",
  "confidence": <0-100 integer>,
  "entry_strategy": "<description>",
  "take_profit_targets": ["TP1 %", "TP2 %", "TP3 %"],
  "stop_loss": "<% below entry>",
  "hold_duration": "scalp (mins) | swing (days) | hold (weeks)",
  "catalysts": ["<catalyst1>", "..."],
  "risks": ["<risk1>", "..."],
  "reasoning": "<concise paragraph>"
}`;

function buildPrompt(coin, screenerResult) {
  return `You are an expert crypto trading analyst specialising in high-risk meme coins.
Analyse the following coin profile and return ONLY valid JSON matching the schema below — no extra text.

## Coin Profile
Symbol: ${coin.symbol}
Chain: ${coin.chain}
Market Cap: $${Number(coin.market_cap).toLocaleString()}
24h Volume: $${Number(coin["24h_volume"]).toLocaleString()}
Liquidity: $${Number(coin.liquidity_usd).toLocaleString()}
Holders: ${coin.holder_count}
Age: ${coin.age_days} days
Social Score: ${coin.social_score}/100
Rug Risk: ${coin.rug_risk_level}
Opportunity Type: ${coin.opportunity_type}

## Safety Screen
Verdict: ${screenerResult.verdict} (score ${screenerResult.score}/100)
Flags: ${screenerResult.flags.length ? screenerResult.flags.join("; ") : "none"}

## Required JSON Schema
${SIGNAL_SCHEMA}

Respond only with the JSON object.`;
}

// ---------------------------------------------------------------------------
// Retry wrapper with exponential backoff
// ---------------------------------------------------------------------------
async function callClaudeWithRetry(prompt, maxRetries = 3) {
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      let fullText = "";
      const stream = client.messages.stream({
        model: "claude-sonnet-4-20250514",
        max_tokens: 512,
        messages: [{ role: "user", content: prompt }],
      });
      for await (const chunk of stream) {
        if (
          chunk.type === "content_block_delta" &&
          chunk.delta.type === "text_delta"
        ) {
          fullText += chunk.delta.text;
        }
      }
      return JSON.parse(fullText.trim());
    } catch (err) {
      if (attempt === maxRetries) throw err;
      const wait = 1000 * Math.pow(2, attempt);
      console.warn(`  Retry ${attempt + 1} in ${wait}ms — ${err.message}`);
      await new Promise((r) => setTimeout(r, wait));
    }
  }
}

// ---------------------------------------------------------------------------
// Dry-run mock
// ---------------------------------------------------------------------------
function mockSignal(coin) {
  const signals = ["STRONG_BUY", "BUY", "WATCH", "AVOID"];
  const idx = coin.symbol.charCodeAt(0) % 4;
  return {
    signal: signals[idx],
    confidence: 55 + (coin.symbol.charCodeAt(0) % 40),
    entry_strategy: `Buy on first green 15m candle with volume confirmation above 20-period MA`,
    take_profit_targets: ["+25%", "+60%", "+120%"],
    stop_loss: "-18% below entry",
    hold_duration: "swing (days)",
    catalysts: ["social momentum", "low float", "upcoming CEX listing rumour"],
    risks: ["thin liquidity", "whale concentration", "market sentiment reversal"],
    reasoning: `[DRY RUN] ${coin.symbol} shows ${coin.opportunity_type} pattern on ${coin.chain}. Social score ${coin.social_score} with ${coin.rug_risk_level} rug risk. Entry timing favourable given current market conditions.`,
  };
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------
async function main() {
  console.log(`\n🤖 AI Signal Engine — ${DRY_RUN ? "DRY RUN" : "LIVE (Claude API)"}\n`);

  const discoveries = JSON.parse(
    readFileSync(resolve(__dirname, "../research/discoveries.json"), "utf8")
  );

  let screenerData = { results: [], qualified: [] };
  try {
    screenerData = JSON.parse(
      readFileSync(resolve(__dirname, "../data/screener-results.json"), "utf8")
    );
  } catch {
    console.warn("⚠️  No screener results found — processing all coins");
    screenerData.qualified = discoveries.coins.map((c) => c.symbol);
    screenerData.results = discoveries.coins.map((c) => ({
      symbol: c.symbol,
      verdict: "WARN",
      score: 60,
      flags: [],
    }));
  }

  const qualifiedCoins = discoveries.coins.filter((c) =>
    screenerData.qualified.includes(c.symbol)
  );

  console.log(`Processing ${qualifiedCoins.length} qualified coins...\n`);

  const signals = [];
  for (const coin of qualifiedCoins) {
    process.stdout.write(`  Analysing ${coin.symbol}...`);
    const screenerResult = screenerData.results.find(
      (r) => r.symbol === coin.symbol
    ) || { verdict: "WARN", score: 60, flags: [] };

    let signal;
    if (DRY_RUN) {
      signal = mockSignal(coin);
    } else {
      signal = await callClaudeWithRetry(buildPrompt(coin, screenerResult));
    }

    const entry = {
      symbol: coin.symbol,
      chain: coin.chain,
      contract_address: coin.contract_address,
      market_cap: coin.market_cap,
      generated_at: new Date().toISOString(),
      ...signal,
    };
    signals.push(entry);
    console.log(` ${signal.signal} (${signal.confidence}%)`);
  }

  const output = {
    generated_at: new Date().toISOString(),
    dry_run: DRY_RUN,
    signals,
  };

  const outPath = resolve(__dirname, "../data/signals.json");
  writeFileSync(outPath, JSON.stringify(output, null, 2));
  console.log(`\nSignals saved → ${outPath}`);

  // Print summary
  const counts = signals.reduce((acc, s) => {
    acc[s.signal] = (acc[s.signal] || 0) + 1;
    return acc;
  }, {});
  console.log("\nSignal summary:", counts);
}

main().catch((e) => {
  console.error("Fatal:", e.message);
  process.exit(1);
});
