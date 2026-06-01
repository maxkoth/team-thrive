#!/usr/bin/env node
/**
 * GlowLab — Ad Headline Generator
 * Uses Claude API to generate 20 high-converting ad headline variants
 * for Facebook, TikTok, Google, and Pinterest ads.
 *
 * Usage: node ad-headline-generator.js [--platform facebook|tiktok|google|all]
 */

import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

const PRODUCT_CONTEXT = {
  name: 'GlowLab Pro LED Face Mask',
  price: '$97',
  keyBenefits: ['clears acne', 'boosts collagen', 'fades dark spots', 'reduces fine lines'],
  audience: 'Women 25–44 with skincare concerns (acne, aging, hyperpigmentation)',
  offer: '38% off, 60-day money-back guarantee, free shipping',
  socialProof: '2,400+ verified buyers, 4.9/5 stars',
  uniqueAngle: 'Same technology as $300 dermatology sessions, at home for under $100',
};

const PLATFORM_SPECS = {
  facebook: { maxChars: 40, format: 'Short, punchy, curiosity-driven. Can use emojis sparingly.' },
  tiktok: { maxChars: 60, format: 'Casual, conversational, trend-aware. Hook with relatable POV or controversy.' },
  google: { maxChars: 30, format: 'Keyword-rich, benefit-led, no emojis. Include price or offer when possible.' },
  pinterest: { maxChars: 50, format: 'Aspirational, visual language, "how to" and transformation angles work well.' },
};

async function generateHeadlines(platform = 'all') {
  const platformsToGenerate = platform === 'all' ? Object.keys(PLATFORM_SPECS) : [platform];

  const systemPrompt = `You are a world-class performance marketing copywriter with 10+ years writing ads for DTC beauty and health brands.
Your headlines consistently achieve >3% CTR and you understand what makes someone stop scrolling.

For each headline you write:
- Lead with emotion, curiosity, or a specific outcome — never generic benefits
- Use specific numbers when they strengthen the claim
- Match the platform's content culture and character limits exactly
- Vary the angle: some problem-aware, some solution-aware, some testimonial-style, some contrarian
- Avoid: "amazing", "best ever", "incredible", "you won't believe" — these are red flags
- Include: specific outcomes, numbers, social proof references, urgency when natural`;

  const results = {};

  for (const plt of platformsToGenerate) {
    const spec = PLATFORM_SPECS[plt];

    const userPrompt = `Generate exactly 5 ad headlines for ${plt.toUpperCase()} for this product:

Product: ${PRODUCT_CONTEXT.name}
Price: ${PRODUCT_CONTEXT.price}
Key Benefits: ${PRODUCT_CONTEXT.keyBenefits.join(', ')}
Target Audience: ${PRODUCT_CONTEXT.audience}
Offer: ${PRODUCT_CONTEXT.offer}
Social Proof: ${PRODUCT_CONTEXT.socialProof}
Unique Angle: ${PRODUCT_CONTEXT.uniqueAngle}

Platform specs: ${spec.format}
Max characters: ${spec.maxChars}

Return a JSON array of exactly 5 objects, each with:
- headline: the headline text
- angle: the psychological angle used (e.g., "social proof", "curiosity gap", "loss aversion", "transformation")
- charCount: character count of the headline

Example format:
[{"headline": "...", "angle": "...", "charCount": 28}]`;

    try {
      const response = await client.messages.create({
        model: 'claude-sonnet-4-20250514',
        max_tokens: 800,
        system: systemPrompt,
        messages: [{ role: 'user', content: userPrompt }],
      });

      const raw = response.content[0].text;
      const jsonMatch = raw.match(/\[[\s\S]*\]/);
      if (!jsonMatch) throw new Error(`No JSON array found in response for ${plt}`);

      results[plt] = JSON.parse(jsonMatch[0]);
    } catch (error) {
      if (error instanceof Anthropic.APIError) {
        console.error(`API error for ${plt}: ${error.status} ${error.message}`);
        results[plt] = { error: error.message };
      } else {
        throw error;
      }
    }

    // Rate limit between requests
    await new Promise(r => setTimeout(r, 500));
  }

  return results;
}

async function main() {
  if (!process.env.ANTHROPIC_API_KEY) {
    console.error('Error: ANTHROPIC_API_KEY not set.');
    process.exit(1);
  }

  const platformArg = process.argv.find(a => ['facebook', 'tiktok', 'google', 'pinterest', 'all'].includes(a)) || 'all';

  console.log(`\nGlowLab Ad Headline Generator`);
  console.log(`Platform: ${platformArg.toUpperCase()}`);
  console.log(`Model: claude-sonnet-4-20250514\n`);
  console.log('Generating headlines...\n');

  const headlines = await generateHeadlines(platformArg);

  let totalCount = 0;

  for (const [platform, items] of Object.entries(headlines)) {
    if (items.error) {
      console.error(`✗ ${platform}: ${items.error}`);
      continue;
    }

    console.log(`=== ${platform.toUpperCase()} HEADLINES ===`);
    items.forEach((item, i) => {
      console.log(`${i + 1}. "${item.headline}"`);
      console.log(`   Angle: ${item.angle} | Chars: ${item.charCount}/${PLATFORM_SPECS[platform].maxChars}`);
    });
    console.log('');
    totalCount += items.length;
  }

  console.log(`✓ Generated ${totalCount} headlines total.`);
  console.log('\n=== ALL HEADLINES (JSON) ===');
  console.log(JSON.stringify(headlines, null, 2));
}

main().catch(err => {
  console.error('Fatal:', err.message);
  process.exit(1);
});
