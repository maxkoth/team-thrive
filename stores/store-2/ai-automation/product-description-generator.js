#!/usr/bin/env node
/**
 * SaunaZen — Product Description Generator
 * Uses Claude API to auto-generate SEO-optimized, conversion-focused product descriptions.
 *
 * Usage: node product-description-generator.js [--spec path/to/spec.json]
 */

import Anthropic from '@anthropic-ai/sdk';
import { readFileSync } from 'fs';
import { resolve } from 'path';

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

const DEFAULT_SPEC = {
  name: 'SaunaZen Signature Infrared Sauna Blanket',
  category: 'Wellness / Recovery',
  price: 169,
  originalPrice: 249,
  keyFeatures: [
    'Far-infrared heating (4–14µm therapeutic wavelength)',
    '6 independent temperature zones, 77°F–176°F',
    'EMF-safe: <3 milligauss at all settings',
    'Waterproof PU outer, food-grade silicone inner',
    'Auto shut-off at 60 minutes',
    'Folds into included carry bag',
  ],
  benefits: [
    'Deep detoxification — FIR mobilizes toxins stored in fat cells',
    'Muscle recovery — increases circulation by up to 25%',
    'Cortisol reduction — 23% average drop per session',
    'Passive calorie burn — 300–600 calories per 45-minute session',
    'Skin clarity — thermal sweat purges pores + FIR stimulates collagen',
  ],
  targetAudience: 'Health-conscious adults 28–50: athletes, stressed professionals, wellness enthusiasts, chronic pain sufferers',
  tone: 'elevated, calming, science-confident — like a trusted wellness expert, not a salesperson',
  differentiators: ['Far-infrared vs. surface heat', 'EMF certified safe', 'Food-grade materials', '45-day guarantee'],
};

async function generateProductDescription(spec = DEFAULT_SPEC) {
  const system = `You are a luxury wellness copywriter with deep knowledge of infrared therapy, biohacking, and high-end DTC health brands.
Your writing is:
- Calming and authoritative, not hyped or salesy
- Science-backed with specific data (studies, percentages, mechanisms)
- Aspirational — you write for someone who takes their health seriously
- Formatted cleanly for e-commerce (scannable but engaging)
Output as JSON: { shortDescription, longDescription, bulletPoints, seoDescription }`;

  const prompt = `Generate a complete product description for:

${JSON.stringify(spec, null, 2)}

Rules:
- shortDescription: 1 sentence, lead with the transformation (max 140 chars)
- longDescription: 3 paragraphs — what it does → how it works (mechanism) → why it's worth it (300–380 words)
- bulletPoints: 6 benefit-led bullets, format "Outcome: specific mechanism or proof"
- seoDescription: 155-char meta description, keyword-rich but natural`;

  const response = await client.messages.create({
    model: 'claude-sonnet-4-20250514',
    max_tokens: 1500,
    system,
    messages: [{ role: 'user', content: prompt }],
  });

  const raw = response.content[0].text;
  const match = raw.match(/\{[\s\S]*\}/);
  if (!match) throw new Error('No JSON in response');
  return JSON.parse(match[0]);
}

async function main() {
  if (!process.env.ANTHROPIC_API_KEY) { console.error('ANTHROPIC_API_KEY not set'); process.exit(1); }

  let spec = DEFAULT_SPEC;
  const si = process.argv.indexOf('--spec');
  if (si !== -1 && process.argv[si + 1]) {
    spec = JSON.parse(readFileSync(resolve(process.argv[si + 1]), 'utf-8'));
  }

  console.log(`\nSaunaZen Product Description Generator\nModel: claude-sonnet-4-20250514\n`);

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
