#!/usr/bin/env node
/**
 * Phase 3 — Sentiment Analyser
 * Scrapes last 200 posts mentioning a ticker and scores sentiment via Claude.
 * Use --dry-run to skip API calls and return mock scores.
 * Usage: node sentiment.js --ticker BONK [--dry-run]
 */

import Anthropic from "@anthropic-ai/sdk";
import { writeFileSync, readFileSync } from "fs";
import { resolve, dirname } from "path";
import { fileURLToPath } from "url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const DRY_RUN = process.argv.includes("--dry-run");
const TICKER_IDX = process.argv.indexOf("--ticker");
const TICKER = TICKER_IDX !== -1 ? process.argv[TICKER_IDX + 1] : null;

const client = DRY_RUN ? null : new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

// ---------------------------------------------------------------------------
// Mock social posts (production: replace with Twitter API v2 / Telegram scraper)
// ---------------------------------------------------------------------------
function fetchMockPosts(ticker) {
  const templates = [
    `$${ticker} is mooning rn, just aped in 🚀🚀🚀`,
    `$${ticker} dev doxxed, huge community, this is 100x`,
    `Anyone else loading $${ticker}? Chart looks insane`,
    `$${ticker} is a scam, rugpull incoming be careful`,
    `$${ticker} $${ticker} $${ticker} let's gooooo to the moon`,
    `Just copy pasted from another project. $${ticker} avoid`,
    `Whales accumulating $${ticker} on-chain data confirms`,
    `$${ticker} listed on tier-2 CEX, price pumping`,
    `$${ticker} team is anonymous, risky play`,
    `$${ticker} tokenomics look solid, long term hold`,
    `Coordinated shill campaign for $${ticker} — caution`,
    `$${ticker} broke key resistance, next stop 10x`,
    `I lost money on $${ticker} last time, not touching`,
    `$${ticker} narrative aligns with current AI agent meta`,
    `$${ticker} volume dried up, moving on`,
  ];
  const posts = [];
  for (let i = 0; i < 200; i++) {
    posts.push({
      id: `post_${i}`,
      text: templates[i % templates.length],
      platform: i % 3 === 0 ? "twitter" : i % 3 === 1 ? "reddit" : "telegram",
      timestamp: new Date(Date.now() - i * 90000).toISOString(),
    });
  }
  return posts;
}

// ---------------------------------------------------------------------------
// Detect coordinated pump signals (naive: same text repeated)
// ---------------------------------------------------------------------------
function detectCoordination(posts) {
  const freq = {};
  posts.forEach((p) => {
    const key = p.text.toLowerCase().replace(/\s+/g, " ").trim();
    freq[key] = (freq[key] || 0) + 1;
  });
  const suspicious = Object.entries(freq)
    .filter(([, count]) => count >= 5)
    .map(([text, count]) => ({ text, count }));
  return suspicious;
}

// ---------------------------------------------------------------------------
// Send batch to Claude for sentiment scoring
// ---------------------------------------------------------------------------
async function scoreSentimentWithClaude(ticker, posts) {
  const BATCH_SIZE = 50;
  const batches = [];
  for (let i = 0; i < posts.length; i += BATCH_SIZE) {
    batches.push(posts.slice(i, i + BATCH_SIZE));
  }

  const batchResults = [];
  for (const [idx, batch] of batches.entries()) {
    const postText = batch
      .map((p, i) => `${i + 1}. [${p.platform}] ${p.text}`)
      .join("\n");

    const prompt = `You are a crypto sentiment analyst. Analyse these ${batch.length} social media posts about $${ticker}.
For each post assign one label: bullish | neutral | bearish | shill.
"shill" = coordinated/inauthentic promotion.

Posts:
${postText}

Return ONLY a JSON array of ${batch.length} objects: [{"id": 1, "label": "bullish"}, ...]`;

    let fullText = "";
    const stream = client.messages.stream({
      model: "claude-sonnet-4-20250514",
      max_tokens: 1024,
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
    const parsed = JSON.parse(fullText.trim());
    batchResults.push(...parsed.map((r, i) => ({ post: batch[i], ...r })));
    console.log(`  Batch ${idx + 1}/${batches.length} scored`);
  }
  return batchResults;
}

// ---------------------------------------------------------------------------
// Mock scoring
// ---------------------------------------------------------------------------
function mockScorePosts(posts) {
  const labels = ["bullish", "bullish", "neutral", "bearish", "shill"];
  return posts.map((p, i) => ({ post: p, id: i + 1, label: labels[i % 5] }));
}

// ---------------------------------------------------------------------------
// Compute -100..+100 sentiment score
// ---------------------------------------------------------------------------
function computeScore(labelledPosts) {
  const counts = { bullish: 0, neutral: 0, bearish: 0, shill: 0 };
  labelledPosts.forEach((r) => counts[r.label]++);
  const total = labelledPosts.length;
  const score = Math.round(
    ((counts.bullish - counts.bearish - counts.shill * 0.5) / total) * 100
  );
  return { score: Math.max(-100, Math.min(100, score)), counts };
}

// ---------------------------------------------------------------------------
// Main
// ---------------------------------------------------------------------------
async function main() {
  if (!TICKER) {
    console.error("Usage: node sentiment.js --ticker <SYMBOL> [--dry-run]");
    process.exit(1);
  }

  console.log(`\n💬 Sentiment Analyser — $${TICKER} — ${DRY_RUN ? "DRY RUN" : "LIVE"}\n`);

  const posts = fetchMockPosts(TICKER);
  console.log(`Fetched ${posts.length} posts`);

  const coordinated = detectCoordination(posts);
  if (coordinated.length) {
    console.log(`⚠️  Coordinated posts detected (${coordinated.length} patterns):`);
    coordinated.forEach((c) => console.log(`   x${c.count}: "${c.text.slice(0, 60)}..."`));
  }

  let labelled;
  if (DRY_RUN) {
    labelled = mockScorePosts(posts);
  } else {
    labelled = await scoreSentimentWithClaude(TICKER, posts);
  }

  const { score, counts } = computeScore(labelled);

  const result = {
    ticker: TICKER,
    generated_at: new Date().toISOString(),
    dry_run: DRY_RUN,
    post_count: posts.length,
    sentiment_score: score,
    label_counts: counts,
    coordination_alerts: coordinated.length,
    coordinated_patterns: coordinated,
    interpretation:
      score >= 50
        ? "STRONGLY BULLISH"
        : score >= 20
        ? "BULLISH"
        : score >= -20
        ? "NEUTRAL"
        : score >= -50
        ? "BEARISH"
        : "STRONGLY BEARISH",
  };

  console.log(`\nSentiment score: ${score} (${result.interpretation})`);
  console.log("Label breakdown:", counts);

  const outPath = resolve(__dirname, `../data/sentiment-${TICKER}.json`);
  writeFileSync(outPath, JSON.stringify(result, null, 2));
  console.log(`\nResults saved → ${outPath}`);
}

main().catch((e) => {
  console.error("Fatal:", e.message);
  process.exit(1);
});
