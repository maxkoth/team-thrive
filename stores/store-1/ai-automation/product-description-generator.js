#!/usr/bin/env node
/**
 * GlowLab — Product Description Generator
 * Uses Claude API to auto-generate SEO-optimized, conversion-focused product descriptions
 * from a JSON product spec.
 *
 * Usage: node product-description-generator.js [--spec path/to/spec.json]
 */

import Anthropic from '@anthropic-ai/sdk';
import { readFileSync } from 'fs';
import { resolve } from 'path';

const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

const DEFAULT_SPEC = {
  name: 'GlowLab Pro LED Face Mask',
  category: 'Beauty / Skincare Tech',
  price: 97,
  originalPrice: 156,
  keyFeatures: [
    '136 medical-grade LED chips',
    '7 clinically-studied wavelengths (415nm–850nm)',
    'USB-C rechargeable, auto 10-minute shutoff',
    'FDA-cleared wavelengths',
    'Universal fit adjustable silicone strap',
    'Includes free Radiance Serum sample',
  ],
  benefits: [
    'Clears acne — blue light kills P. acnes bacteria',
    'Boosts collagen and reduces fine lines (red light)',
    'Fades hyperpigmentation and dark spots (green light)',
    'Calms redness and rosacea (yellow light)',
  ],
  targetAudience: 'Women aged 25–44 dealing with acne, fine lines, or uneven skin tone',
  tone: 'confident, warm, science-backed but accessible — not clinical jargon',
  competitors: ['CurrentBody LED Mask', 'Dr. Dennis Gross SpectraLite', 'Omnilux'],
  differentiators: ['Most affordable clinic-equivalent', '7 wavelengths vs 2-4 in competitors', '60-day guarantee'],
};

async function generateProductDescription(spec = DEFAULT_SPEC) {
  const systemPrompt = `You are an expert e-commerce copywriter specializing in beauty and skincare products.
You write product descriptions that:
1. Lead with the most compelling customer outcome (not features)
2. Use sensory language and transformation storytelling
3. Include specific proof points and numbers where available
4. Naturally weave in SEO keywords without stuffing
5. Create urgency without fake scarcity
6. Match the brand's warm, science-backed tone
Format your output as JSON with these fields: shortDescription, longDescription, bulletPoints, seoDescription`;

  const userPrompt = `Generate a complete product description for this product:

${JSON.stringify(spec, null, 2)}

Requirements:
- shortDescription: 1–2 sentences, lead with the transformation (max 150 chars)
- longDescription: 3 paragraphs, story arc: problem → solution → proof → call to action (300–400 words)
- bulletPoints: array of 6 benefit-led bullet points (not feature-led). Format as "Benefit: supporting detail"
- seoDescription: 155-character meta description optimized for search intent

Avoid: passive voice, generic adjectives ("amazing", "great"), unsubstantiated superlatives.
Include: specific numbers, clinical references, before/after framing.`;

  try {
    const response = await client.messages.create({
      model: 'claude-sonnet-4-20250514',
      max_tokens: 1500,
      system: systemPrompt,
      messages: [{ role: 'user', content: userPrompt }],
    });

    const rawText = response.content[0].text;

    // Extract JSON from response
    const jsonMatch = rawText.match(/\{[\s\S]*\}/);
    if (!jsonMatch) {
      throw new Error('Claude did not return valid JSON. Raw response:\n' + rawText);
    }

    const result = JSON.parse(jsonMatch[0]);
    return result;
  } catch (error) {
    if (error instanceof Anthropic.APIError) {
      console.error(`Anthropic API error ${error.status}: ${error.message}`);
      throw error;
    }
    throw error;
  }
}

async function main() {
  let spec = DEFAULT_SPEC;

  // Allow passing a custom spec file
  const specArgIndex = process.argv.indexOf('--spec');
  if (specArgIndex !== -1 && process.argv[specArgIndex + 1]) {
    const specPath = resolve(process.argv[specArgIndex + 1]);
    try {
      spec = JSON.parse(readFileSync(specPath, 'utf-8'));
      console.log(`Using spec from: ${specPath}`);
    } catch (e) {
      console.error('Failed to load spec file:', e.message);
      process.exit(1);
    }
  }

  if (!process.env.ANTHROPIC_API_KEY) {
    console.error('Error: ANTHROPIC_API_KEY environment variable not set.');
    console.error('Run: export ANTHROPIC_API_KEY=your_key_here');
    process.exit(1);
  }

  console.log(`\nGenerating product description for: ${spec.name}`);
  console.log('Model: claude-sonnet-4-20250514\n');

  try {
    const description = await generateProductDescription(spec);

    console.log('=== SHORT DESCRIPTION ===');
    console.log(description.shortDescription);

    console.log('\n=== LONG DESCRIPTION ===');
    console.log(description.longDescription);

    console.log('\n=== BULLET POINTS ===');
    description.bulletPoints.forEach((point, i) => console.log(`${i + 1}. ${point}`));

    console.log('\n=== SEO META DESCRIPTION ===');
    console.log(description.seoDescription);

    console.log('\n=== RAW JSON (for import) ===');
    console.log(JSON.stringify(description, null, 2));
  } catch (error) {
    console.error('Failed to generate description:', error.message);
    process.exit(1);
  }
}

main();
