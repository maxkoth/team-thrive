#!/usr/bin/env node
/**
 * GlowLab — Automated Review Responder
 * Uses Claude API to generate empathetic, brand-consistent responses to customer reviews.
 * Handles 1-5 star reviews with appropriate tone adjustments.
 *
 * Usage: node review-responder.js
 *        node review-responder.js --batch reviews.json
 */

import Anthropic from '@anthropic-ai/sdk';
import { readFileSync } from 'fs';
import { resolve } from 'path';

const client = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY });

const BRAND_VOICE = `
GlowLab Brand Voice Guidelines:
- Warm, genuine, and personal — never corporate or scripted-sounding
- Science-confident but accessible — mention evidence only when relevant
- Empathetic first, solution-oriented second
- Use the customer's first name when available
- Never be defensive about negative reviews; seek to understand and resolve
- Keep responses concise: 3–5 sentences for positive, up to 8 for negative
- Sign off as: "— The GlowLab Team"
- Do NOT offer discounts publicly in review responses (handle via DM/email)
`;

const SAMPLE_REVIEWS = [
  {
    id: 'r001',
    author: 'Mia',
    rating: 5,
    text: "Absolutely love this mask! Been using it for 3 weeks and my acne has dramatically improved. The blue light mode is incredible. Shipping was fast too.",
  },
  {
    id: 'r002',
    author: 'Anonymous',
    rating: 2,
    text: "The mask itself seems okay but I've been using it for 2 weeks and don't see any results yet. Also the strap is a bit uncomfortable. Maybe I'm doing something wrong?",
  },
  {
    id: 'r003',
    author: 'Jennifer T.',
    rating: 1,
    text: "The USB-C cable stopped working after 5 days. Mask is now useless. Very disappointed for a $97 product.",
  },
  {
    id: 'r004',
    author: 'Daniela',
    rating: 4,
    text: "Really happy with my purchase! Skin is looking better after a month. Only giving 4 stars because the instructions could be clearer about which mode to use for different concerns.",
  },
];

async function generateReviewResponse(review) {
  const starContext = {
    1: 'This is a critical 1-star review indicating a defective product or serious issue.',
    2: 'This is a disappointed 2-star review — customer has concerns but may be persuadable.',
    3: 'This is a neutral 3-star review — customer is lukewarm, there may be a fixable issue.',
    4: 'This is a positive 4-star review with a minor suggestion or small complaint.',
    5: 'This is a glowing 5-star review — reinforce their experience and encourage them.',
  };

  const systemPrompt = `You are responding to customer reviews for GlowLab, a premium LED face mask brand.

${BRAND_VOICE}

${starContext[review.rating]}

Your goals by review type:
- 5 stars: Express genuine gratitude, highlight what they experienced, create community warmth
- 4 stars: Thank them, acknowledge the feedback constructively, show it will be acted on
- 3 stars: Empathize, address the concern directly, offer a resolution path
- 2 stars: Investigate the issue with questions, provide actionable guidance, offer to follow up
- 1 star: Apologize sincerely, take immediate ownership, provide direct contact to fix the issue

Always respond in the second person to the reviewer. Never blame the customer.`;

  const userPrompt = `Write a response to this ${review.rating}-star review:

Reviewer: ${review.author || 'Customer'}
Rating: ${review.rating}/5 stars
Review Text: "${review.text}"

Generate a response that follows GlowLab's brand voice guidelines. Keep it genuine and human.`;

  const response = await client.messages.create({
    model: 'claude-sonnet-4-20250514',
    max_tokens: 400,
    system: systemPrompt,
    messages: [{ role: 'user', content: userPrompt }],
  });

  return response.content[0].text.trim();
}

async function processBatch(reviews) {
  console.log(`Processing ${reviews.length} review(s)...\n`);
  const results = [];

  for (const review of reviews) {
    try {
      console.log(`[${review.id || 'review'}] ${review.rating}★ — "${review.text.slice(0, 60)}..."`);
      const response = await generateReviewResponse(review);
      results.push({ ...review, generatedResponse: response });
      console.log('RESPONSE:', response);
      console.log('---\n');

      // Respectful rate limiting
      await new Promise(r => setTimeout(r, 300));
    } catch (error) {
      if (error instanceof Anthropic.APIError) {
        console.error(`API error for review ${review.id}: ${error.status} ${error.message}`);
        results.push({ ...review, error: error.message });
      } else {
        throw error;
      }
    }
  }

  return results;
}

async function main() {
  if (!process.env.ANTHROPIC_API_KEY) {
    console.error('Error: ANTHROPIC_API_KEY not set.');
    process.exit(1);
  }

  let reviews = SAMPLE_REVIEWS;

  const batchArg = process.argv.indexOf('--batch');
  if (batchArg !== -1 && process.argv[batchArg + 1]) {
    const filePath = resolve(process.argv[batchArg + 1]);
    reviews = JSON.parse(readFileSync(filePath, 'utf-8'));
    console.log(`Loaded ${reviews.length} reviews from ${filePath}\n`);
  }

  console.log('GlowLab Review Responder — Powered by Claude\n');
  const results = await processBatch(reviews);

  console.log(`\n✓ Generated ${results.filter(r => !r.error).length}/${results.length} responses successfully.`);
}

main().catch(err => {
  console.error('Fatal error:', err.message);
  process.exit(1);
});
