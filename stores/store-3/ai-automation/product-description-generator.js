#!/usr/bin/env node
/**
 * LinguaFlow — Product Description Generator
 * Uses Claude API to generate compelling, accurate product descriptions
 * for translation technology products.
 *
 * Usage: node product-description-generator.js [--spec path/to/spec.json]
 */

import Anthropic from '@anthropic-ai/sdk';
import { readFileSync } from 'fs';
import { resolve } from 'path';

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

const DEFAULT_SPEC = {
  name: 'LinguaFlow Pro AI Translation Earbuds',
  category: 'Consumer Tech / Travel Accessories',
  price: 59,
  originalPrice: 79,
  keyFeatures: [
    'Real-time translation in 144 languages (0.2-second latency)',
    '40 languages work fully offline (no internet required)',
    '4-microphone array with active noise cancellation',
    '8-hour battery + 32-hour charging case',
    'Bidirectional translation mode (both parties wear earbuds)',
    'Business vocabulary for 12 professional domains',
    'IPX5 waterproof rating',
    'Bluetooth 5.3',
  ],
  useCases: ['international travel', 'business negotiations', 'medical appointments', 'language learning', 'multilingual families'],
  targetAudience: 'Frequent travelers, business professionals, expats, healthcare workers, language learners',
  tone: 'confident and empowering — this solves a real human problem. Tech-credible but human-focused.',
  differentiators: ['0.2s latency vs 1–3s for most competitors', '40 offline languages', 'Business vocabulary mode', 'Dual earbud bidirectional mode'],
};

async function generateProductDescription(spec = DEFAULT_SPEC) {
  const system = `You are a tech product copywriter who specializes in travel and communication technology for DTC brands.
Your copy is:
- Grounded in real use cases and scenarios, not abstract tech specs
- Empowering — the product gives the buyer a superpower
- Honest about limitations (you mention when a spec is approximate or context-dependent)
- Specific: use numbers, countries, situations
Return JSON: { shortDescription, longDescription, bulletPoints, seoDescription }`;

  const prompt = `Write a complete product description for:

${JSON.stringify(spec, null, 2)}

Requirements:
- shortDescription: 1 powerful sentence, outcome-first (max 140 chars)
- longDescription: 3 paragraphs — the problem it solves → the technology → real-world use cases (320–400 words)
- bulletPoints: 6 benefit-led bullets. Format "Superpower: how it works"
- seoDescription: 155-char meta, include key specs naturally

Avoid: "revolutionary", "game-changing", "cutting-edge" — be specific instead.`;

  const response = await client.messages.create({
    model: 'claude-sonnet-4-20250514',
    max_tokens: 1500,
    system,
    messages: [{ role: 'user', content: prompt }],
  });

  const match = response.content[0].text.match(/\{[\s\S]*\}/);
  if (!match) throw new Error('No JSON found in Claude response');
  return JSON.parse(match[0]);
}

async function main() {
  if (!process.env.ANTHROPIC_API_KEY) { console.error('ANTHROPIC_API_KEY not set'); process.exit(1); }

  let spec = DEFAULT_SPEC;
  const si = process.argv.indexOf('--spec');
  if (si !== -1 && process.argv[si + 1]) {
    spec = JSON.parse(readFileSync(resolve(process.argv[si + 1]), 'utf-8'));
  }

  console.log(`\nLinguaFlow Product Description Generator`);
  console.log(`Model: claude-sonnet-4-20250514\n`);

  try {
    const d = await generateProductDescription(spec);
    console.log('=== SHORT ===\n', d.shortDescription);
    console.log('\n=== LONG ===\n', d.longDescription);
    console.log('\n=== BULLETS ===');
    d.bulletPoints.forEach((b, i) => console.log(`${i+1}. ${b}`));
    console.log('\n=== SEO META ===\n', d.seoDescription);
    console.log('\n=== JSON ===\n', JSON.stringify(d, null, 2));
  } catch (e) {
    if (e instanceof Anthropic.APIError) { console.error(`API Error ${e.status}: ${e.message}`); }
    else { console.error(e.message); }
    process.exit(1);
  }
}

main();
