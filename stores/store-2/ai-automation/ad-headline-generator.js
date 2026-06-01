#!/usr/bin/env node
/**
 * SaunaZen — Ad Headline Generator
 * Generates 20 ad headline variants across platforms using Claude API.
 *
 * Usage: node ad-headline-generator.js [facebook|tiktok|google|pinterest|all]
 */

import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

const PRODUCT = {
  name: 'SaunaZen Infrared Sauna Blanket',
  price: '$169',
  keyBenefits: ['deep detox', 'muscle recovery', 'cortisol reduction', 'better sleep', 'passive calorie burn'],
  audience: 'Wellness-focused adults 28–50: athletes, stressed professionals, biohackers, chronic pain sufferers',
  offer: 'Free carry bag, free shipping, 45-day money-back guarantee',
  socialProof: '1,800+ verified buyers, 4.8/5 stars, 40+ peer-reviewed studies support FIR therapy',
  angle: 'Same technology as $80/session wellness studios, available for $169 total at home',
};

const PLATFORMS = {
  facebook: { maxChars: 40, notes: 'Lead with value comparison or health outcome. Can include numbers.' },
  tiktok: { maxChars: 60, notes: 'Casual, relatable, slightly provocative. Use "this" as pattern interrupt.' },
  google: { maxChars: 30, notes: 'Keyword-rich, benefit-first, no emojis, include price or deal.' },
  pinterest: { maxChars: 50, notes: 'Aspirational lifestyle, "how to" or transformation framing, wellness aesthetic.' },
};

async function generateHeadlines(platform = 'all') {
  const targets = platform === 'all' ? Object.keys(PLATFORMS) : [platform];
  const results = {};

  for (const plt of targets) {
    const spec = PLATFORMS[plt];
    const response = await client.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 700,
      system: 'You are a DTC wellness brand performance marketer. Write headlines that feel authentic to wellness culture while driving real clicks. No generic wellness fluff.',
      messages: [{
        role: 'user',
        content: `Generate 5 ${plt.toUpperCase()} ad headlines for: ${PRODUCT.name} ($${PRODUCT.price})\nBenefits: ${PRODUCT.keyBenefits.join(', ')}\nOffer: ${PRODUCT.offer}\nProof: ${PRODUCT.socialProof}\nAngle: ${PRODUCT.angle}\nPlatform notes: ${spec.notes}\nMax chars: ${spec.maxChars}\n\nReturn JSON array: [{"headline":"...","angle":"...","charCount":N}]`,
      }],
    });

    const match = response.content[0].text.match(/\[[\s\S]*\]/);
    results[plt] = match ? JSON.parse(match[0]) : { error: 'Parse failed' };
    await new Promise(r => setTimeout(r, 400));
  }

  return results;
}

async function main() {
  if (!process.env.ANTHROPIC_API_KEY) { console.error('ANTHROPIC_API_KEY not set'); process.exit(1); }
  const plt = process.argv.find(a => ['facebook','tiktok','google','pinterest','all'].includes(a)) || 'all';

  console.log(`\nSaunaZen Ad Headline Generator — Platform: ${plt.toUpperCase()}\n`);
  const headlines = await generateHeadlines(plt);

  for (const [p, items] of Object.entries(headlines)) {
    if (items.error) { console.error(`✗ ${p}: ${items.error}`); continue; }
    console.log(`=== ${p.toUpperCase()} ===`);
    items.forEach((h, i) => console.log(`${i+1}. "${h.headline}"\n   Angle: ${h.angle} | Chars: ${h.charCount}/${PLATFORMS[p].maxChars}`));
    console.log('');
  }
}

main().catch(e => { console.error(e.message); process.exit(1); });
