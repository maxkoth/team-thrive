#!/usr/bin/env node
/**
 * LinguaFlow — Ad Headline Generator
 * Generates 20 high-converting ad headline variants across platforms.
 *
 * Usage: node ad-headline-generator.js [facebook|tiktok|google|pinterest|all]
 */

import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

const PRODUCT = {
  name: 'LinguaFlow Pro AI Translation Earbuds',
  price: '$59',
  keyBenefits: ['real-time translation', '144 languages', '0.2-second latency', 'works offline', '8-hour battery'],
  audience: 'Travelers, business professionals, expats, healthcare workers, language learners',
  offer: '$20 off + free travel case, free shipping, 30-day guarantee',
  socialProof: '3,100+ verified buyers, 4.8/5 stars',
  angle: 'Break any language barrier instantly — the superpower frequent travelers have been waiting for',
};

const PLATFORMS = {
  facebook: { maxChars: 40, notes: 'Outcome or curiosity-led. Speak to the traveler or professional. Numbers work well.' },
  tiktok: { maxChars: 60, notes: 'POV-style, relatable travel moment, casual tone. Must feel native to TikTok.' },
  google: { maxChars: 30, notes: 'Keyword-rich, direct, spec-forward or benefit-forward. No emojis.' },
  pinterest: { maxChars: 50, notes: 'Travel inspiration, aspirational destinations, "how to" framing for travel.' },
};

async function generateHeadlines(platform = 'all') {
  const targets = platform === 'all' ? Object.keys(PLATFORMS) : [platform];
  const results = {};

  for (const plt of targets) {
    const spec = PLATFORMS[plt];
    const response = await client.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 700,
      system: 'You write high-CTR ad headlines for travel tech products. Your headlines are specific, surprising, and make people feel the product in their life. Avoid generic travel clichés.',
      messages: [{
        role: 'user',
        content: `Generate 5 ${plt.toUpperCase()} headlines for: ${PRODUCT.name} (${PRODUCT.price})\nBenefits: ${PRODUCT.keyBenefits.join(', ')}\nOffer: ${PRODUCT.offer}\nProof: ${PRODUCT.socialProof}\nAngle: ${PRODUCT.angle}\nNotes: ${spec.notes}\nMax chars: ${spec.maxChars}\n\nReturn JSON: [{"headline":"...","angle":"...","charCount":N}]`,
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

  console.log(`\nLinguaFlow Ad Headline Generator — ${plt.toUpperCase()}\n`);
  const headlines = await generateHeadlines(plt);

  for (const [p, items] of Object.entries(headlines)) {
    if (items.error) { console.error(`✗ ${p}: ${items.error}`); continue; }
    console.log(`=== ${p.toUpperCase()} ===`);
    items.forEach((h, i) => console.log(`${i+1}. "${h.headline}"\n   Angle: ${h.angle} | Chars: ${h.charCount}/${PLATFORMS[p].maxChars}`));
    console.log('');
  }
}

main().catch(e => { console.error(e.message); process.exit(1); });
